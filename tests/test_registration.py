# -*- coding: utf-8 -*-
# Standard library imports...
import hashlib
import hmac
import logging
import logging.config
import json
import os
import yaml
import random
import re
import requests
from requests import exceptions
import string
import sys
import unittest
from unittest.mock import patch
from urllib.parse import urlparse

# Third-party imports...
from parameterized import parameterized
from datetime import datetime
from click.testing import CliRunner
from flask import Flask

# Local imports...
try:
    from .context import matrix_registration
except ModuleNotFoundError:
    from context import matrix_registration
from matrix_registration.config import Config
from matrix_registration.app import create_app
from matrix_registration.tokens import db
from matrix_registration.app import (
    create_app,
    cli,
)

logger = logging.getLogger(__name__)


LOGGING = {
    "version": 1,
    "root": {"level": "NOTSET", "handlers": ["console"]},
    "formatters": {
        "precise": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "NOTSET",
            "formatter": "precise",
            "stream": "ext://sys.stdout",
        }
    },
}

GOOD_CONFIG = {
    "server_location": "https://matrix.org",
    "server_name": "matrix.org",
    "registration_shared_secret": "coolsharesecret",
    "admin_api_shared_secret": "coolpassword",
    "base_url": "/element",
    "client_redirect": "",
    "client_logo": "",
    "db": "sqlite:///%s/tests/db.sqlite" % (os.getcwd(),),
    "host": "",
    "port": 5000,
    "rate_limit": ["100 per day", "10 per minute"],
    "allow_cors": False,
    "password": {"min_length": 8},
    "username": {
        "validation_regex": ["[a-z\d]"],
        "invalidation_regex": [".*?(admin|support).*?"],
    },
    "ip_logging": False,
    "logging": LOGGING,
}

BAD_CONFIG1 = dict(  # wrong matrix server location -> 500
    GOOD_CONFIG.items(),
    server_location="https://wronghs.org",
)

BAD_CONFIG2 = dict(  # wrong admin secret password -> 401
    GOOD_CONFIG.items(),
    admin_api_shared_secret="wrongpassword",
)

BAD_CONFIG3 = dict(  # wrong matrix shared password -> 500
    GOOD_CONFIG.items(),
    registration_shared_secret="wrongsecret",
)

usernames = []
nonces = []
logging.config.dictConfig(LOGGING)


def mock_new_user(username):
    access_token = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=256)
    )
    device_id = "".join(random.choices(string.ascii_uppercase, k=8))
    home_server = matrix_registration.config.config.server_location
    username = username.rsplit(":")[0].split("@")[-1]
    user_id = "@{}:{}".format(username, home_server)
    usernames.append(username)

    user = {
        "access_token": access_token,
        "device_id": device_id,
        "home_server": home_server,
        "user_id": user_id,
    }
    return user


def mocked__get_nonce(server_location):
    nonce = "".join(random.choices(string.ascii_lowercase + string.digits, k=129))
    nonces.append(nonce)
    return nonce


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code == 200:
                return self.status_code
            else:
                raise exceptions.HTTPError(response=self)

    # print(args[0])
    # print(matrix_registration.config.config.server_location)
    domain = urlparse(GOOD_CONFIG["server_location"]).hostname
    re_mxid = r"^@?[a-zA-Z_\-=\.\/0-9]+(:" + re.escape(domain) + r")?$"
    location = "_synapse/admin/v1/register"

    if args[0] == "%s/%s" % (GOOD_CONFIG["server_location"], location):
        if kwargs:
            req = kwargs["json"]
            if not req["nonce"] in nonces:
                return MockResponse(
                    {"'errcode': 'M_UNKOWN", "'error': 'unrecognised nonce'"}, 400
                )

            mac = hmac.new(
                key=str.encode(GOOD_CONFIG["registration_shared_secret"]),
                digestmod=hashlib.sha1,
            )

            mac.update(req["nonce"].encode())
            mac.update(b"\x00")
            mac.update(req["username"].encode())
            mac.update(b"\x00")
            mac.update(req["password"].encode())
            mac.update(b"\x00")
            mac.update(b"admin" if req["admin"] else b"notadmin")
            mac = mac.hexdigest()
            if not re.search(re_mxid, req["username"]):
                return MockResponse(
                    {
                        "'errcode': 'M_INVALID_USERNAME",
                        "'error': 'User ID can only contain"
                        + "characters a-z, 0-9, or '=_-./'",
                    },
                    400,
                )
            if req["username"].rsplit(":")[0].split("@")[-1] in usernames:
                return MockResponse(
                    {"errcode": "M_USER_IN_USE", "error": "User ID already taken."}, 400
                )
            if req["mac"] != mac:
                return MockResponse(
                    {"errcode": "M_UNKNOWN", "error": "HMAC incorrect"}, 403
                )
            return MockResponse(mock_new_user(req["username"]), 200)
    return MockResponse(None, 404)


class TokensTest(unittest.TestCase):
    def setUp(self):
        matrix_registration.config.config = Config(GOOD_CONFIG)
        app = create_app(testing=True)
        with app.app_context():
            app.config.from_mapping(
                SQLALCHEMY_DATABASE_URI=matrix_registration.config.config.db,
                SQLALCHEMY_TRACK_MODIFICATIONS=False,
            )
            db.init_app(app)
            db.create_all()

        self.app = app

    def tearDown(self):
        os.remove(matrix_registration.config.config.db[10:])

    def test_random_readable_string(self):
        for n in range(10):
            string = matrix_registration.tokens.random_readable_string(length=n)
            words = re.sub("([a-z])([A-Z])", r"\1 \2", string).split()
            self.assertEqual(len(words), n)

    def test_tokens_empty(self):
        with self.app.app_context():
            test_tokens = matrix_registration.tokens.Tokens()

            # no token should exist at this point
            self.assertFalse(test_tokens.active(""))
            test_token = test_tokens.new()

            # no empty token should have been created
            self.assertFalse(test_tokens.active(""))

    def test_tokens_disable(self):
        with self.app.app_context():
            test_tokens = matrix_registration.tokens.Tokens()
            test_token = test_tokens.new()

            # new tokens should be active first, inactive after disabling it
            self.assertTrue(test_token.active())
            self.assertTrue(test_token.disable())
            self.assertFalse(test_token.active())

            test_token2 = test_tokens.new()

            self.assertTrue(test_tokens.active(test_token2.name))
            self.assertTrue(test_tokens.disable(test_token2.name))
            self.assertFalse(test_tokens.active(test_token2.name))

            test_token3 = test_tokens.new()
            test_token3.use()

            self.assertFalse(test_tokens.active(test_token2.name))
            self.assertFalse(test_tokens.disable(test_token2.name))
            self.assertFalse(test_tokens.active(test_token2.name))

    def test_tokens_load(self):
        with self.app.app_context():
            test_tokens = matrix_registration.tokens.Tokens()

            test_token = test_tokens.new()
            test_token2 = test_tokens.new()
            test_token3 = test_tokens.new(max_usage=True)
            test_token4 = test_tokens.new(
                expiration_date=datetime.fromisoformat("2111-01-01")
            )
            test_token5 = test_tokens.new(
                expiration_date=datetime.fromisoformat("1999-01-01")
            )

            test_tokens.disable(test_token2.name)
            test_tokens.use(test_token3.name)
            test_tokens.use(test_token4.name)

            test_tokens.load()

            # token1: active, unused, no expiration date
            # token2: inactive, unused, no expiration date
            # token3: used once, one-time, now inactive
            # token4: active, used once, expiration date
            # token5: inactive, expiration date

            self.assertEqual(
                test_token.name, test_tokens.get_token(test_token.name).name
            )
            self.assertEqual(
                test_token2.name, test_tokens.get_token(test_token2.name).name
            )
            self.assertEqual(
                test_token2.active(), test_tokens.get_token(test_token2.name).active()
            )
            self.assertEqual(
                test_token3.used, test_tokens.get_token(test_token3.name).used
            )
            self.assertEqual(
                test_token3.active(), test_tokens.get_token(test_token3.name).active()
            )
            self.assertEqual(
                test_token4.used, test_tokens.get_token(test_token4.name).used
            )
            self.assertEqual(
                test_token4.expiration_date,
                test_tokens.get_token(test_token4.name).expiration_date,
            )
            self.assertEqual(
                test_token5.active(), test_tokens.get_token(test_token5.name).active()
            )

    @parameterized.expand(
        [
            [None, False],
            [datetime.fromisoformat("2100-01-12"), False],
            [None, True],
            [datetime.fromisoformat("2100-01-12"), True],
        ]
    )
    def test_tokens_new(self, expiration_date, max_usage):
        with self.app.app_context():
            test_tokens = matrix_registration.tokens.Tokens()
            test_token = test_tokens.new(
                expiration_date=expiration_date, max_usage=max_usage
            )

            self.assertIsNotNone(test_token)
            if expiration_date:
                self.assertIsNotNone(test_token.expiration_date)
            else:
                self.assertIsNone(test_token.expiration_date)
            if max_usage:
                self.assertTrue(test_token.max_usage)
            else:
                self.assertFalse(test_token.max_usage)
            self.assertTrue(test_tokens.active(test_token.name))

    @parameterized.expand(
        [
            [None, False, 10, True],
            [datetime.fromisoformat("2100-01-12"), False, 10, True],
            [None, True, 1, False],
            [None, True, 0, True],
            [datetime.fromisoformat("2100-01-12"), True, 1, False],
            [datetime.fromisoformat("2100-01-12"), True, 2, False],
            [datetime.fromisoformat("2100-01-12"), True, 0, True],
        ]
    )
    def test_tokens_active_form(self, expiration_date, max_usage, times_used, active):
        with self.app.app_context():
            test_tokens = matrix_registration.tokens.Tokens()
            test_token = test_tokens.new(
                expiration_date=expiration_date, max_usage=max_usage
            )

            for n in range(times_used):
                test_tokens.use(test_token.name)

            if not max_usage:
                self.assertEqual(test_token.used, times_used)
            elif times_used == 0:
                self.assertEqual(test_token.used, 0)
            else:
                self.assertEqual(test_token.used, 1)
            self.assertEqual(test_tokens.active(test_token.name), active)

    @parameterized.expand(
        [
            [None, True],
            [datetime.fromisoformat("2100-01-12"), False],
            [datetime.fromisoformat("2200-01-13"), True],
        ]
    )
    def test_tokens_active(self, expiration_date, active):
        with self.app.app_context():
            test_tokens = matrix_registration.tokens.Tokens()
            test_token = test_tokens.new(expiration_date=expiration_date)

            self.assertEqual(test_tokens.active(test_token.name), True)
            # date changed to after expiration date
            with patch("matrix_registration.tokens.datetime") as mock_date:
                mock_date.now.return_value = datetime.fromisoformat("2200-01-12")
                self.assertEqual(test_tokens.active(test_token.name), active)

    @parameterized.expand(
        [
            ["DoubleWizardSky"],
            ["null"],
            ["false"],
        ]
    )
    def test_tokens_repr(self, name):
        with self.app.app_context():
            test_token1 = matrix_registration.tokens.Token(name=name)

            self.assertEqual(str(test_token1), name)

    def test_token_repr(self):
        with self.app.app_context():
            test_tokens = matrix_registration.tokens.Tokens()
            test_token1 = test_tokens.new()
            test_token2 = test_tokens.new()
            test_token3 = test_tokens.new()
            test_token4 = test_tokens.new()
            test_token5 = test_tokens.new()

            expected_answer = (
                "%s, " % test_token1.name
                + "%s, " % test_token2.name
                + "%s, " % test_token3.name
                + "%s, " % test_token4.name
                + "%s" % test_token5.name
            )

            self.assertEqual(str(test_tokens), expected_answer)


class ApiTest(unittest.TestCase):
    def setUp(self):
        matrix_registration.config.config = Config(GOOD_CONFIG)
        app = create_app(testing=True)
        with app.app_context():
            app.config.from_mapping(
                SQLALCHEMY_DATABASE_URI=matrix_registration.config.config.db,
                SQLALCHEMY_TRACK_MODIFICATIONS=False,
            )
            db.init_app(app)
            db.create_all()
            self.client = app.test_client()
        self.app = app

    def tearDown(self):
        os.remove(matrix_registration.config.config.db[10:])

    @parameterized.expand(
        [
            ["test1", "test1234", "test1234", True, 200],
            ["", "test1234", "test1234", True, 400],
            ["test2", "", "test1234", True, 400],
            ["test3", "test1234", "", True, 400],
            ["test4", "test1234", "test1234", False, 400],
            ["@test5:matrix.org", "test1234", "test1234", True, 200],
            ["@test6:wronghs.org", "test1234", "test1234", True, 400],
            ["test7", "test1234", "tet1234", True, 400],
            ["teüst8", "test1234", "test1234", True, 400],
            ["@test9@matrix.org", "test1234", "test1234", True, 400],
            ["test11@matrix.org", "test1234", "test1234", True, 400],
            ["", "test1234", "test1234", True, 400],
            [
                "".join(random.choices(string.ascii_uppercase, k=256)),
                "test1234",
                "test1234",
                True,
                400,
            ],
            ["@admin:matrix.org", "test1234", "test1234", True, 400],
            ["matrixadmin123", "test1234", "test1234", True, 400],
        ]
    )
    # check form activeators
    @patch("matrix_registration.matrix_api._get_nonce", side_effect=mocked__get_nonce)
    @patch(
        "matrix_registration.matrix_api.requests.post", side_effect=mocked_requests_post
    )
    def test_register(
        self, username, password, confirm, token, status, mock_get, mock_nonce
    ):
        matrix_registration.config.config = Config(GOOD_CONFIG)
        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(
                expiration_date=None, max_usage=True
            )
            # replace matrix with in config set hs
            domain = urlparse(
                matrix_registration.config.config.server_location
            ).hostname
            if username:
                username = username.replace("matrix.org", domain)

            if not token:
                test_token.name = ""
            rv = self.client.post(
                "/register",
                data=dict(
                    username=username,
                    password=password,
                    confirm=confirm,
                    token=test_token.name,
                ),
            )
            if rv.status_code == 200:
                account_data = json.loads(rv.data.decode("utf8").replace("'", '"'))
                # print(account_data)
            self.assertEqual(rv.status_code, status)

    @patch("matrix_registration.matrix_api._get_nonce", side_effect=mocked__get_nonce)
    @patch(
        "matrix_registration.matrix_api.requests.post", side_effect=mocked_requests_post
    )
    def test_register_wrong_hs(self, mock_get, mock_nonce):
        matrix_registration.config.config = Config(BAD_CONFIG1)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(
                expiration_date=None, max_usage=True
            )
            rv = self.client.post(
                "/register",
                data=dict(
                    username="username",
                    password="password",
                    confirm="password",
                    token=test_token.name,
                ),
            )
            self.assertEqual(rv.status_code, 500)

    @patch("matrix_registration.matrix_api._get_nonce", side_effect=mocked__get_nonce)
    @patch(
        "matrix_registration.matrix_api.requests.post", side_effect=mocked_requests_post
    )
    def test_register_wrong_secret(self, mock_get, mock_nonce):
        matrix_registration.config.config = Config(BAD_CONFIG3)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(
                expiration_date=None, max_usage=True
            )
            rv = self.client.post(
                "/register",
                data=dict(
                    username="username",
                    password="password",
                    confirm="password",
                    token=test_token.name,
                ),
            )
            self.assertEqual(rv.status_code, 500)

    def test_get_tokens(self):
        matrix_registration.config.config = Config(GOOD_CONFIG)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(
                expiration_date=None, max_usage=True
            )

            secret = matrix_registration.config.config.admin_api_shared_secret
            headers = {"Authorization": "SharedSecret %s" % secret}
            rv = self.client.get("/api/token", headers=headers)

            self.assertEqual(rv.status_code, 200)
            token_data = json.loads(rv.data.decode("utf8").replace("'", '"'))

            self.assertEqual(token_data[0]["expiration_date"], None)
            self.assertEqual(token_data[0]["max_usage"], True)

    def test_error_get_tokens(self):
        matrix_registration.config.config = Config(BAD_CONFIG2)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(
                expiration_date=None, max_usage=True
            )

            secret = matrix_registration.config.config.admin_api_shared_secret
            matrix_registration.config.config = Config(GOOD_CONFIG)
            headers = {"Authorization": "SharedSecret %s" % secret}
            rv = self.client.get("/api/token", headers=headers)

            self.assertEqual(rv.status_code, 401)
            token_data = json.loads(rv.data.decode("utf8").replace("'", '"'))

            self.assertEqual(token_data["errcode"], "MR_BAD_SECRET")
            self.assertEqual(token_data["error"], "wrong shared secret")

    @parameterized.expand(
        [
            [None, True, None],
            ["2020-12-24", False, "2020-12-24 00:00:00"],
            ["2200-05-12", True, "2200-05-12 00:00:00"],
        ]
    )
    def test_post_token(self, expiration_date, max_usage, parsed_date):
        matrix_registration.config.config = Config(GOOD_CONFIG)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(
                expiration_date=None, max_usage=True
            )

            secret = matrix_registration.config.config.admin_api_shared_secret
            headers = {"Authorization": "SharedSecret %s" % secret}
            rv = self.client.post(
                "/api/token",
                data=json.dumps(
                    dict(expiration_date=expiration_date, max_usage=max_usage)
                ),
                content_type="application/json",
                headers=headers,
            )

            self.assertEqual(rv.status_code, 200)
            token_data = json.loads(rv.data.decode("utf8").replace("'", '"'))
            self.assertEqual(token_data["expiration_date"], parsed_date)
            self.assertEqual(token_data["max_usage"], max_usage)
            self.assertTrue(token_data["name"] is not None)

    def test_error_post_token(self):
        matrix_registration.config.config = Config(BAD_CONFIG2)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(
                expiration_date=None, max_usage=True
            )

            secret = matrix_registration.config.config.admin_api_shared_secret
            matrix_registration.config.config = Config(GOOD_CONFIG)
            headers = {"Authorization": "SharedSecret %s" % secret}
            rv = self.client.post(
                "/api/token",
                data=json.dumps(dict(expiration_date="24.12.2020", max_usage=False)),
                content_type="application/json",
                headers=headers,
            )

            self.assertEqual(rv.status_code, 401)
            token_data = json.loads(rv.data.decode("utf8").replace("'", '"'))

            self.assertEqual(token_data["errcode"], "MR_BAD_SECRET")
            self.assertEqual(token_data["error"], "wrong shared secret")

            secret = matrix_registration.config.config.admin_api_shared_secret
            headers = {"Authorization": "SharedSecret %s" % secret}
            rv = self.client.post(
                "/api/token",
                data=json.dumps(dict(expiration_date="2020-24-12", max_usage=False)),
                content_type="application/json",
                headers=headers,
            )

            self.assertEqual(rv.status_code, 400)
            token_data = json.loads(rv.data.decode("utf8"))
            self.assertEqual(token_data["errcode"], "MR_BAD_DATE_FORMAT")
            self.assertEqual(token_data["error"], "date wasn't in YYYY-MM-DD format")

    def test_patch_token(self):
        matrix_registration.config.config = Config(GOOD_CONFIG)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(max_usage=True)

            secret = matrix_registration.config.config.admin_api_shared_secret
            headers = {"Authorization": "SharedSecret %s" % secret}
            rv = self.client.patch(
                "/api/token/" + test_token.name,
                data=json.dumps(dict(disabled=True)),
                content_type="application/json",
                headers=headers,
            )

            self.assertEqual(rv.status_code, 200)
            token_data = json.loads(rv.data.decode("utf8").replace("'", '"'))
            self.assertEqual(token_data["active"], False)
            self.assertEqual(token_data["max_usage"], True)
            self.assertEqual(token_data["name"], test_token.name)

    def test_error_patch_token(self):
        matrix_registration.config.config = Config(BAD_CONFIG2)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(max_usage=True)

            secret = matrix_registration.config.config.admin_api_shared_secret
            headers = {"Authorization": "SharedSecret %s" % secret}
            matrix_registration.config.config = Config(GOOD_CONFIG)
            rv = self.client.patch(
                "/api/token/" + test_token.name,
                data=json.dumps(dict(disabled=True)),
                content_type="application/json",
                headers=headers,
            )

            self.assertEqual(rv.status_code, 401)
            token_data = json.loads(rv.data.decode("utf8").replace("'", '"'))
            self.assertEqual(token_data["errcode"], "MR_BAD_SECRET")
            self.assertEqual(token_data["error"], "wrong shared secret")

            secret = matrix_registration.config.config.admin_api_shared_secret
            headers = {"Authorization": "SharedSecret %s" % secret}
            rv = self.client.patch(
                "/api/token/" + test_token.name,
                data=json.dumps(dict(active=False)),
                content_type="application/json",
                headers=headers,
            )

            self.assertEqual(rv.status_code, 400)
            token_data = json.loads(rv.data.decode("utf8"))
            self.assertEqual(token_data["errcode"], "MR_BAD_USER_REQUEST")
            self.assertEqual(
                token_data["error"], "you're not allowed to change this property"
            )

            rv = self.client.patch(
                "/api/token/" + "nicememe",
                data=json.dumps(dict(disabled=True)),
                content_type="application/json",
                headers=headers,
            )

            self.assertEqual(rv.status_code, 404)
            token_data = json.loads(rv.data.decode("utf8"))
            self.assertEqual(token_data["errcode"], "MR_TOKEN_NOT_FOUND")
            self.assertEqual(token_data["error"], "token does not exist")

    @parameterized.expand(
        [
            [None, True, None],
            [datetime.fromisoformat("2020-12-24"), False, "2020-12-24 00:00:00"],
            [datetime.fromisoformat("2200-05-12"), True, "2200-05-12 00:00:00"],
        ]
    )
    def test_get_token(self, expiration_date, max_usage, parsed_date):
        matrix_registration.config.config = Config(BAD_CONFIG2)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(
                expiration_date=expiration_date, max_usage=max_usage
            )

            secret = matrix_registration.config.config.admin_api_shared_secret
            headers = {"Authorization": "SharedSecret %s" % secret}
            rv = self.client.get(
                "/api/token/" + test_token.name,
                content_type="application/json",
                headers=headers,
            )

            self.assertEqual(rv.status_code, 200)
            token_data = json.loads(rv.data.decode("utf8"))
            self.assertEqual(token_data["expiration_date"], parsed_date)
            self.assertEqual(token_data["max_usage"], max_usage)

    def test_error_get_token(self):
        matrix_registration.config.config = Config(BAD_CONFIG2)
        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(max_usage=True)

            secret = matrix_registration.config.config.admin_api_shared_secret
            headers = {"Authorization": "SharedSecret %s" % secret}
            rv = self.client.get(
                "/api/token/" + "nice_meme",
                content_type="application/json",
                headers=headers,
            )

            self.assertEqual(rv.status_code, 404)
            token_data = json.loads(rv.data.decode("utf8"))
            self.assertEqual(token_data["errcode"], "MR_TOKEN_NOT_FOUND")
            self.assertEqual(token_data["error"], "token does not exist")

            matrix_registration.config.config = Config(BAD_CONFIG2)

            secret = matrix_registration.config.config.admin_api_shared_secret
            headers = {"Authorization": "SharedSecret %s" % secret}
            matrix_registration.config.config = Config(GOOD_CONFIG)
            rv = self.client.patch(
                "/api/token/" + test_token.name,
                data=json.dumps(dict(disabled=True)),
                content_type="application/json",
                headers=headers,
            )

            self.assertEqual(rv.status_code, 401)
            token_data = json.loads(rv.data.decode("utf8").replace("'", '"'))
            self.assertEqual(token_data["errcode"], "MR_BAD_SECRET")
            self.assertEqual(token_data["error"], "wrong shared secret")


class ConfigTest(unittest.TestCase):
    def test_config_update(self):
        matrix_registration.config.config = Config(GOOD_CONFIG)
        self.assertEqual(matrix_registration.config.config.port, GOOD_CONFIG["port"])
        self.assertEqual(
            matrix_registration.config.config.server_location,
            GOOD_CONFIG["server_location"],
        )

        matrix_registration.config.config.update(BAD_CONFIG1)
        self.assertEqual(matrix_registration.config.config.port, BAD_CONFIG1["port"])
        self.assertEqual(
            matrix_registration.config.config.server_location,
            BAD_CONFIG1["server_location"],
        )

    def test_config_path(self):
        # BAD_CONFIG1_path = "x"
        good_config_path = "tests/test_config.yaml"

        with open(good_config_path, "w") as outfile:
            yaml.dump(GOOD_CONFIG, outfile, default_flow_style=False)

        matrix_registration.config.config = Config(good_config_path)
        self.assertIsNotNone(matrix_registration.config.config)
        os.remove(good_config_path)


class CliTest(unittest.TestCase):
    path = "tests/test_config.yaml"
    db = "tests/db.sqlite"

    def setUp(self):
        try:
            os.remove(self.db)
        except FileNotFoundError:
            pass
        with open(self.path, "w") as outfile:
            yaml.dump(GOOD_CONFIG, outfile, default_flow_style=False)

    def tearDown(self):
        os.remove(self.path)
        os.remove(self.db)

    def test_create_token(self):
        runner = create_app().test_cli_runner()
        generate = runner.invoke(cli, ["--config-path", self.path, "generate", "-m", 1])
        name1 = generate.output.strip()

        status = runner.invoke(cli, ["--config-path", self.path, "status", "-s", name1])
        valid, info_dict_string = status.output.strip().split("\n", 1)
        self.assertEqual(valid, "This token is valid")
        comparison_dict = {
            "name": name1,
            "used": 0,
            "expiration_date": None,
            "max_usage": 1,
            "disabled": False,
            "ips": [],
            "active": True,
        }
        self.assertEqual(json.loads(info_dict_string), comparison_dict)

        runner.invoke(cli, ["--config-path", self.path, "status", "-d", name1])
        status = runner.invoke(cli, ["--config-path", self.path, "status", "-s", name1])
        valid, info_dict_string = status.output.strip().split("\n", 1)
        self.assertEqual(valid, "This token is not valid")
        comparison_dict = {
            "name": name1,
            "used": 0,
            "expiration_date": None,
            "max_usage": 1,
            "disabled": True,
            "ips": [],
            "active": False,
        }
        self.assertEqual(json.loads(info_dict_string), comparison_dict)

        generate = runner.invoke(
            cli, ["--config-path", self.path, "generate", "-e", "2220-05-12"]
        )
        name2 = generate.output.strip()

        status = runner.invoke(cli, ["--config-path", self.path, "status", "-s", name2])
        valid, info_dict_string = status.output.strip().split("\n", 1)
        self.assertEqual(valid, "This token is valid")
        comparison_dict = {
            "name": name2,
            "used": 0,
            "expiration_date": "2220-05-12 00:00:00",
            "max_usage": 0,
            "disabled": False,
            "ips": [],
            "active": True,
        }
        self.assertEqual(json.loads(info_dict_string), comparison_dict)

        status = runner.invoke(cli, ["--config-path", self.path, "status", "-l"])
        list = status.output.strip()
        self.assertEqual(list, f"{name1}, {name2}")


if "logging" in sys.argv:
    logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    unittest.main()
