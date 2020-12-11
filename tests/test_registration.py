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
from requests import exceptions
import string
import sys
import unittest
from unittest.mock import patch
from urllib.parse import urlparse

# Third-party imports...
from parameterized import parameterized
from dateutil import parser

# Local imports...
try:
    from .context import matrix_registration
except ModuleNotFoundError:
    from context import matrix_registration
from matrix_registration.config import Config
from matrix_registration.app import create_app
from matrix_registration.tokens import db

logger = logging.getLogger(__name__)


LOGGING = {
    "version": 1,
    "root": {
        "level": "NOTSET",
        "handlers": [
            "console"
        ]
    },
    "formatters": {
        "precise": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "NOTSET",
            "formatter": "precise",
            "stream": "ext://sys.stdout"
        }
    }
}

GOOD_CONFIG = {
    'server_location': 'https://righths.org',
    'shared_secret': 'coolsharesecret',
    'admin_secret': 'coolpassword',
    'db': 'sqlite:///%s/tests/db.sqlite' % (os.getcwd(),),
    'port': 5000,
    'password': {
        'min_length': 8
    },
    'logging': LOGGING
}

BAD_CONFIG1 = dict(  # wrong matrix server location -> 500
    GOOD_CONFIG.items(),
    server_location='https://wronghs.org',
)

BAD_CONFIG2 = dict(  # wrong admin secret password -> 401
    GOOD_CONFIG.items(),
    admin_secret='wrongpassword',
)

BAD_CONFIG3 = dict(  # wrong matrix shared password -> 500
    GOOD_CONFIG.items(),
    shared_secret='wrongsecret',
)

usernames = []
nonces = []
logging.config.dictConfig(LOGGING)


def mock_new_user(username):
    access_token = ''.join(random.choices(string.ascii_lowercase +
                                          string.digits, k=256))
    device_id = ''.join(random.choices(string.ascii_uppercase, k=8))
    home_server = matrix_registration.config.config.server_location
    username = username.rsplit(":")[0].split("@")[-1]
    user_id = "@{}:{}".format(username, home_server)
    usernames.append(username)

    user = {
        'access_token': access_token,
        'device_id': device_id,
        'home_server': home_server,
        'user_id': user_id
    }
    return user


def mocked__get_nonce(server_location):
    nonce = ''.join(random.choices(string.ascii_lowercase +
                                   string.digits, k=129))
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
    domain = urlparse(GOOD_CONFIG['server_location']).hostname
    re_mxid = r"^@?[a-zA-Z_\-=\.\/0-9]+(:" + \
              re.escape(domain) + \
              r")?$"
    location = '_synapse/admin/v1/register'

    if args[0] == '%s/%s' % (GOOD_CONFIG['server_location'], location):
        if kwargs:
            req = kwargs['json']
            if not req['nonce'] in nonces:
                return MockResponse({"'errcode': 'M_UNKOWN",
                                     "'error': 'unrecognised nonce'"},
                                    400)

            mac = hmac.new(
                key=str.encode(GOOD_CONFIG['shared_secret']),
                digestmod=hashlib.sha1,
            )

            mac.update(req['nonce'].encode())
            mac.update(b'\x00')
            mac.update(req['username'].encode())
            mac.update(b'\x00')
            mac.update(req['password'].encode())
            mac.update(b'\x00')
            mac.update(b'admin' if req['admin'] else b'notadmin')
            mac = mac.hexdigest()
            if not re.search(re_mxid, req['username']):
                return MockResponse({"'errcode': 'M_INVALID_USERNAME",
                                     "'error': 'User ID can only contain" +
                                     "characters a-z, 0-9, or '=_-./'"},
                                    400)
            if req['username'].rsplit(":")[0].split("@")[-1] in usernames:
                return MockResponse({'errcode': 'M_USER_IN_USE',
                                     'error': 'User ID already taken.'},
                                    400)
            if req['mac'] != mac:
                return MockResponse({'errcode': 'M_UNKNOWN',
                                     'error': 'HMAC incorrect'},
                                    403)
            return MockResponse(mock_new_user(req['username']), 200)
    return MockResponse(None, 404)


class TokensTest(unittest.TestCase):
    def setUp(self):
        matrix_registration.config.config = Config(GOOD_CONFIG)
        app = create_app(testing=True)
        with app.app_context():
            app.config.from_mapping(
                SQLALCHEMY_DATABASE_URI=matrix_registration.config.config.db,
                SQLALCHEMY_TRACK_MODIFICATIONS=False
            )
            db.init_app(app)
            db.create_all()

        self.app = app

    def tearDown(self):
        os.remove(matrix_registration.config.config.db[10:])

    def test_random_readable_string(self):
        for n in range(10):
            string = matrix_registration.tokens.random_readable_string(length=n)
            words = re.sub('([a-z])([A-Z])', r'\1 \2', string).split()
            self.assertEqual(len(words), n)

    def test_tokens_empty(self):
        with self.app.app_context():
            test_tokens = matrix_registration.tokens.Tokens()

            # no token should exist at this point
            self.assertFalse(test_tokens.valid(""))
            test_token = test_tokens.new()

            # no empty token should have been created
            self.assertFalse(test_tokens.valid(""))

    def test_tokens_disable(self):
        with self.app.app_context():
            test_tokens = matrix_registration.tokens.Tokens()
            test_token = test_tokens.new()

            # new tokens should be valid first, invalid after disabling it
            self.assertTrue(test_token.valid())
            self.assertTrue(test_token.disable())
            self.assertFalse(test_token.valid())

            test_token2 = test_tokens.new()

            self.assertTrue(test_tokens.valid(test_token2.name))
            self.assertTrue(test_tokens.disable(test_token2.name))
            self.assertFalse(test_tokens.valid(test_token2.name))

            test_token3 = test_tokens.new()
            test_token3.use()

            self.assertFalse(test_tokens.valid(test_token2.name))
            self.assertFalse(test_tokens.disable(test_token2.name))
            self.assertFalse(test_tokens.valid(test_token2.name))

    def test_tokens_load(self):
        with self.app.app_context():
            test_tokens = matrix_registration.tokens.Tokens()

            test_token = test_tokens.new()
            test_token2 = test_tokens.new()
            test_token3 = test_tokens.new(one_time=True)
            test_token4 = test_tokens.new(ex_date=parser.parse("2111-01-01"))
            test_token5 = test_tokens.new(ex_date=parser.parse("1999-01-01"))

            test_tokens.disable(test_token2.name)
            test_tokens.use(test_token3.name)
            test_tokens.use(test_token4.name)

            test_tokens.load()

            # token1: valid, unused, no expiration date
            # token2: invalid, unused, no expiration date
            # token3: used once, one-time, now invalid
            # token4: valid, used once, expiration date
            # token5: invalid, expiration date

            self.assertEqual(test_token.name,
                             test_tokens.get_token(test_token.name).name)
            self.assertEqual(test_token2.name,
                             test_tokens.get_token(test_token2.name).name)
            self.assertEqual(test_token2.valid(),
                             test_tokens.get_token(test_token2.name).valid())
            self.assertEqual(test_token3.used,
                             test_tokens.get_token(test_token3.name).used)
            self.assertEqual(test_token3.valid(),
                             test_tokens.get_token(test_token3.name).valid())
            self.assertEqual(test_token4.used,
                             test_tokens.get_token(test_token4.name).used)
            self.assertEqual(test_token4.ex_date,
                             test_tokens.get_token(test_token4.name).ex_date)
            self.assertEqual(test_token5.valid(),
                             test_tokens.get_token(test_token5.name).valid())

    @parameterized.expand([
        [None, False],
        [parser.parse('2100-01-12'), False],
        [None, True],
        [parser.parse('2100-01-12'), True]
    ])
    def test_tokens_new(self, ex_date, one_time):
        with self.app.app_context():
            test_tokens = matrix_registration.tokens.Tokens()
            test_token = test_tokens.new(ex_date=ex_date, one_time=one_time)

            self.assertIsNotNone(test_token)
            if ex_date:
                self.assertIsNotNone(test_token.ex_date)
            else:
                self.assertIsNone(test_token.ex_date)
            if one_time:
                self.assertTrue(test_token.one_time)
            else:
                self.assertFalse(test_token.one_time)
            self.assertTrue(test_tokens.valid(test_token.name))

    @parameterized.expand([
        [None, False, 10, True],
        [parser.parse('2100-01-12'), False, 10, True],
        [None, True, 1, False],
        [None, True, 0, True],
        [parser.parse('2100-01-12'), True, 1, False],
        [parser.parse('2100-01-12'), True, 2, False],
        [parser.parse('2100-01-12'), True, 0, True]
    ])
    def test_tokens_valid_form(self, ex_date, one_time, times_used, valid):
        with self.app.app_context():
            test_tokens = matrix_registration.tokens.Tokens()
            test_token = test_tokens.new(ex_date=ex_date, one_time=one_time)

            for n in range(times_used):
                test_tokens.use(test_token.name)

            if not one_time:
                self.assertEqual(test_token.used, times_used)
            elif times_used == 0:
                self.assertEqual(test_token.used, 0)
            else:
                self.assertEqual(test_token.used, 1)
            self.assertEqual(test_tokens.valid(test_token.name), valid)

    @parameterized.expand([
        [None, True],
        [parser.parse('2100-01-12'), False],
        [parser.parse('2200-01-13'), True],
    ])
    def test_tokens_valid(self, ex_date, valid):
        with self.app.app_context():
            test_tokens = matrix_registration.tokens.Tokens()
            test_token = test_tokens.new(ex_date=ex_date)

            self.assertEqual(test_tokens.valid(test_token.name), True)
            # date changed to after expiration date
            with patch('matrix_registration.tokens.datetime') as mock_date:
                mock_date.now.return_value = parser.parse('2200-01-12')
                self.assertEqual(test_tokens.valid(test_token.name), valid)

    @parameterized.expand([
        ['DoubleWizardSky'],
        ['null'],
        ['false'],
    ])
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

            expected_answer = ('%s, ' % test_token1.name +
                               '%s, ' % test_token2.name +
                               '%s, ' % test_token3.name +
                               '%s, ' % test_token4.name +
                               '%s' % test_token5.name)

            self.assertEqual(str(test_tokens), expected_answer)


class ApiTest(unittest.TestCase):
    def setUp(self):
        matrix_registration.config.config = Config(GOOD_CONFIG)
        app = create_app(testing=True)
        with app.app_context():
            app.config.from_mapping(
                SQLALCHEMY_DATABASE_URI=matrix_registration.config.config.db,
                SQLALCHEMY_TRACK_MODIFICATIONS=False
            )
            db.init_app(app)
            db.create_all()
            self.client = app.test_client()
        self.app = app

    def tearDown(self):
        os.remove(matrix_registration.config.config.db[10:])

    @parameterized.expand([
        ['test1', 'test1234', 'test1234', True, 200],
        [None, 'test1234', 'test1234', True, 400],
        ['test2', None, 'test1234', True, 400],
        ['test3', 'test1234', None, True, 400],
        ['test4', 'test1234', 'test1234', False, 400],
        ['@test5:matrix.org', 'test1234', 'test1234', True, 200],
        ['@test6:wronghs.org', 'test1234', 'test1234', True, 400],
        ['test7', 'test1234', 'tet1234', True, 400],
        ['teüst8', 'test1234', 'test1234', True, 400],
        ['@test9@matrix.org', 'test1234', 'test1234', True, 400],
        ['test11@matrix.org', 'test1234', 'test1234', True, 400],
        ['', 'test1234', 'test1234', True, 400],
        [''.join(random.choices(string.ascii_uppercase, k=256)),
         'test1234', 'test1234', True, 400]
    ])
    # check form validators
    @patch('matrix_registration.matrix_api._get_nonce',
           side_effect=mocked__get_nonce)
    @patch('matrix_registration.matrix_api.requests.post',
           side_effect=mocked_requests_post)
    def test_register(self, username, password, confirm, token,
                      status, mock_get, mock_nonce):
        matrix_registration.config.config = Config(GOOD_CONFIG)
        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(ex_date=None,
                                                               one_time=True)
            # replace matrix with in config set hs
            domain = urlparse(matrix_registration.config.config.server_location).hostname
            if username:
                username = username.replace("matrix.org", domain)

            if not token:
                test_token.name = ""
            rv = self.client.post('/register', data=dict(
                username=username,
                password=password,
                confirm=confirm,
                token=test_token.name
            ))
            if rv.status_code == 200:
                account_data = json.loads(rv.data.decode('utf8').replace("'", '"'))
                # print(account_data)
            self.assertEqual(rv.status_code, status)

    @patch('matrix_registration.matrix_api._get_nonce',
           side_effect=mocked__get_nonce)
    @patch('matrix_registration.matrix_api.requests.post',
           side_effect=mocked_requests_post)
    def test_register_wrong_hs(self, mock_get, mock_nonce):
        matrix_registration.config.config = Config(BAD_CONFIG1)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(ex_date=None,
                                                               one_time=True)
            rv = self.client.post('/register', data=dict(
                username='username',
                password='password',
                confirm='password',
                token=test_token.name
            ))
            self.assertEqual(rv.status_code, 500)

    @patch('matrix_registration.matrix_api._get_nonce',
           side_effect=mocked__get_nonce)
    @patch('matrix_registration.matrix_api.requests.post',
           side_effect=mocked_requests_post)
    def test_register_wrong_secret(self, mock_get, mock_nonce):
        matrix_registration.config.config = Config(BAD_CONFIG3)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(ex_date=None,
                                                               one_time=True)
            rv = self.client.post('/register', data=dict(
                username='username',
                password='password',
                confirm='password',
                token=test_token.name
            ))
            self.assertEqual(rv.status_code, 500)

    def test_get_tokens(self):
        matrix_registration.config.config = Config(GOOD_CONFIG)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(ex_date=None,
                                                               one_time=True)

            secret = matrix_registration.config.config.admin_secret
            headers = {'Authorization': 'SharedSecret %s' % secret}
            rv = self.client.get('/token', headers=headers)

            self.assertEqual(rv.status_code, 200)
            token_data = json.loads(rv.data.decode('utf8').replace("'", '"'))

            self.assertEqual(token_data[0]['ex_date'], None)
            self.assertEqual(token_data[0]['one_time'], True)

    def test_error_get_tokens(self):
        matrix_registration.config.config = Config(BAD_CONFIG2)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(ex_date=None,
                                                               one_time=True)

            secret = matrix_registration.config.config.admin_secret
            matrix_registration.config.config = Config(GOOD_CONFIG)
            headers = {'Authorization': 'SharedSecret %s' % secret}
            rv = self.client.get('/token', headers=headers)

            self.assertEqual(rv.status_code, 401)
            token_data = json.loads(rv.data.decode('utf8').replace("'", '"'))

            self.assertEqual(token_data['errcode'], 'MR_BAD_SECRET')
            self.assertEqual(token_data['error'], 'wrong shared secret')

    @parameterized.expand([
        [None, True, None],
        ['2020-12-24', False, '2020-12-24 00:00:00'],
        ['2200-05-12', True, '2200-05-12 00:00:00'],
    ])
    def test_post_token(self, ex_date, one_time, parsed_date):
        matrix_registration.config.config = Config(GOOD_CONFIG)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(ex_date=None,
                                                               one_time=True)

            secret = matrix_registration.config.config.admin_secret
            headers = {'Authorization': 'SharedSecret %s' % secret}
            rv = self.client.post('/token',
                                  data=json.dumps(dict(ex_date=ex_date,
                                                       one_time=one_time)),
                                  content_type='application/json',
                                  headers=headers)

            self.assertEqual(rv.status_code, 200)
            token_data = json.loads(rv.data.decode('utf8').replace("'", '"'))
            self.assertEqual(token_data['ex_date'], parsed_date)
            self.assertEqual(token_data['one_time'], one_time)
            self.assertTrue(token_data['name'] is not None)

    def test_error_post_token(self):
        matrix_registration.config.config = Config(BAD_CONFIG2)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(ex_date=None,
                                                               one_time=True)

            secret = matrix_registration.config.config.admin_secret
            matrix_registration.config.config = Config(GOOD_CONFIG)
            headers = {'Authorization': 'SharedSecret %s' % secret}
            rv = self.client.post('/token',
                                  data=json.dumps(dict(ex_date='24.12.2020',
                                                       one_time=False)),
                                  content_type='application/json',
                                  headers=headers)

            self.assertEqual(rv.status_code, 401)
            token_data = json.loads(rv.data.decode('utf8').replace("'", '"'))

            self.assertEqual(token_data['errcode'], 'MR_BAD_SECRET')
            self.assertEqual(token_data['error'], 'wrong shared secret')

            secret = matrix_registration.config.config.admin_secret
            headers = {'Authorization': 'SharedSecret %s' % secret}
            rv = self.client.post('/token',
                                  data=json.dumps(dict(ex_date='2020-24-12',
                                                       one_time=False)),
                                  content_type='application/json',
                                  headers=headers)

            self.assertEqual(rv.status_code, 400)
            token_data = json.loads(rv.data.decode('utf8'))
            self.assertEqual(token_data['errcode'], 'MR_BAD_DATE_FORMAT')
            self.assertEqual(token_data['error'], "date wasn't YYYY-MM-DD format")

    def test_put_token(self):
        matrix_registration.config.config = Config(GOOD_CONFIG)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(one_time=True)

            secret = matrix_registration.config.config.admin_secret
            headers = {'Authorization': 'SharedSecret %s' % secret}
            rv = self.client.put('/token/' + test_token.name,
                                 data=json.dumps(dict(disable=True)),
                                 content_type='application/json',
                                 headers=headers)

            self.assertEqual(rv.status_code, 200)
            token_data = json.loads(rv.data.decode('utf8').replace("'", '"'))
            self.assertEqual(token_data['valid'], False)
            self.assertEqual(token_data['one_time'], True)
            self.assertEqual(token_data['name'], test_token.name)

    def test_error_put_token(self):
        matrix_registration.config.config = Config(BAD_CONFIG2)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(one_time=True)

            secret = matrix_registration.config.config.admin_secret
            headers = {'Authorization': 'SharedSecret %s' % secret}
            matrix_registration.config.config = Config(GOOD_CONFIG)
            rv = self.client.put('/token/' + test_token.name,
                                 data=json.dumps(dict(disable=True)),
                                 content_type='application/json',
                                 headers=headers)

            self.assertEqual(rv.status_code, 401)
            token_data = json.loads(rv.data.decode('utf8').replace("'", '"'))
            self.assertEqual(token_data['errcode'], 'MR_BAD_SECRET')
            self.assertEqual(token_data['error'], 'wrong shared secret')

            secret = matrix_registration.config.config.admin_secret
            headers = {'Authorization': 'SharedSecret %s' % secret}
            rv = self.client.put('/token/' + test_token.name,
                                 data=json.dumps(dict(disable=False)),
                                 content_type='application/json',
                                 headers=headers)

            self.assertEqual(rv.status_code, 400)
            token_data = json.loads(rv.data.decode('utf8'))
            self.assertEqual(token_data['errcode'], 'MR_BAD_USER_REQUEST')
            self.assertEqual(token_data['error'], 'PUT only allows "disable": true')

            rv = self.client.put('/token/' + "nicememe",
                                 data=json.dumps(dict(disable=True)),
                                 content_type='application/json',
                                 headers=headers)

            self.assertEqual(rv.status_code, 404)
            token_data = json.loads(rv.data.decode('utf8'))
            self.assertEqual(token_data['errcode'], 'MR_TOKEN_NOT_FOUND')
            self.assertEqual(token_data['error'], 'token does not exist or is already disabled')


    @parameterized.expand([
        [None, True, None],
        [parser.isoparse('2020-12-24'), False, '2020-12-24 00:00:00'],
        [parser.isoparse('2200-05-12'), True, '2200-05-12 00:00:00'],
    ])
    def test_get_token(self, ex_date, one_time, parsed_date):
        matrix_registration.config.config = Config(BAD_CONFIG2)

        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(ex_date=ex_date,
                                                               one_time=one_time)

            secret = matrix_registration.config.config.admin_secret
            headers = {'Authorization': 'SharedSecret %s' % secret}
            rv = self.client.get('/token/' + test_token.name,
                                 content_type='application/json',
                                 headers=headers)

            self.assertEqual(rv.status_code, 200)
            token_data = json.loads(rv.data.decode('utf8'))
            self.assertEqual(token_data['ex_date'], parsed_date)
            self.assertEqual(token_data['one_time'], one_time)

    def test_error_get_token(self):
        matrix_registration.config.config = Config(BAD_CONFIG2)
        with self.app.app_context():
            matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
            test_token = matrix_registration.tokens.tokens.new(one_time=True)

            secret = matrix_registration.config.config.admin_secret
            headers = {'Authorization': 'SharedSecret %s' % secret}
            rv = self.client.get('/token/' + 'nice_meme',
                                 content_type='application/json',
                                 headers=headers)

            self.assertEqual(rv.status_code, 404)
            token_data = json.loads(rv.data.decode('utf8'))
            self.assertEqual(token_data['errcode'], 'MR_TOKEN_NOT_FOUND')
            self.assertEqual(token_data['error'], 'token does not exist')

            matrix_registration.config.config = Config(BAD_CONFIG2)

            secret = matrix_registration.config.config.admin_secret
            headers = {'Authorization': 'SharedSecret %s' % secret}
            matrix_registration.config.config = Config(GOOD_CONFIG)
            rv = self.client.put('/token/' + test_token.name,
                                 data=json.dumps(dict(disable=True)),
                                 content_type='application/json',
                                 headers=headers)

            self.assertEqual(rv.status_code, 401)
            token_data = json.loads(rv.data.decode('utf8').replace("'", '"'))
            self.assertEqual(token_data['errcode'], 'MR_BAD_SECRET')
            self.assertEqual(token_data['error'], 'wrong shared secret')


class ConfigTest(unittest.TestCase):
    def test_config_update(self):
        matrix_registration.config.config = Config(GOOD_CONFIG)
        self.assertEqual(matrix_registration.config.config.port,
                         GOOD_CONFIG['port'])
        self.assertEqual(matrix_registration.config.config.server_location,
                         GOOD_CONFIG['server_location'])

        matrix_registration.config.config.update(BAD_CONFIG1)
        self.assertEqual(matrix_registration.config.config.port,
                         BAD_CONFIG1['port'])
        self.assertEqual(matrix_registration.config.config.server_location,
                         BAD_CONFIG1['server_location'])

    def test_config_path(self):
        # BAD_CONFIG1_path = "x"
        good_config_path = "tests/test_config.yaml"

        with open(good_config_path, 'w') as outfile:
            yaml.dump(GOOD_CONFIG, outfile, default_flow_style=False)

        matrix_registration.config.config = Config(good_config_path)
        self.assertIsNotNone(matrix_registration.config.config)
        os.remove(good_config_path)

# TODO: - tests for /token/<token>
#       - a nonce is only valid for 60s


if "logging" in sys.argv:
    logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    unittest.main()
