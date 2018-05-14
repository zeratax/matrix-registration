# Standard library imports...
from datetime import date
import json
import os
import random
import re
import string
import unittest
from unittest.mock import Mock, patch
from urllib.parse import urlsplit

# Third-party imports...
from parameterized import parameterized
from dateutil import parser

# Local imports...
from .context import matrix_registration
from matrix_registration.config import Config

api = matrix_registration.api

CONFIG_PATH = 'tests/config.yaml'


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            return self.status_code

    # print(args[0])
    # print(matrix_registration.config.config.server_location)
    if args[0] == '%s/_matrix/client/api/v1/register' % "https://wronghs.org":
        return MockResponse(None, 404)
    elif args[0] == '%s/_matrix/client/api/v1/register' % matrix_registration.config.config.server_location:
        if kwargs:
            req = kwargs['json']
            access_token = ''.join(random.choices(string.ascii_lowercase +
                                                  string.digits, k=256))
            device_id = ''.join(random.choices(string.ascii_uppercase, k=8))
            home_server = matrix_registration.config.config.server_location
            user = req['user'].rsplit(":")[0].split("@")[-1]
            user_id = "@{}:{}".format(user, home_server)
            return MockResponse({
                                'access_token': access_token,
                                'device_id': device_id,
                                'home_server': home_server,
                                'user_id': user_id
                                }, 200)
    return MockResponse(None, 404)


class TokensTest(unittest.TestCase):
    def setUpClass():
        matrix_registration.config.config = Config(CONFIG_PATH)

    def tearDownClass():
        os.remove(matrix_registration.config.config.DB)

    def test_random_readable_string(self):
        for n in range(10):
            string = matrix_registration.tokens.random_readable_string(length=n)
            words = re.sub('([a-z])([A-Z])', r'\1 \2', string).split()
            self.assertEqual(len(words), n)

    def test_tokens_empty(self):
        test_tokens = matrix_registration.tokens.Tokens()

        self.assertFalse(test_tokens.valid(""))
        test_token = test_tokens.new()

        self.assertFalse(test_tokens.valid(""))

    def test_tokens_disable(self):
        test_tokens = matrix_registration.tokens.Tokens()
        test_token = test_tokens.new()

        self.assertFalse(test_token.is_expired())
        self.assertTrue(test_token.disable())
        self.assertTrue(test_token.is_expired())

        test_token2 = test_tokens.new()

        self.assertTrue(test_tokens.valid(test_token2.name))
        self.assertTrue(test_tokens.disable(test_token2.name))
        self.assertFalse(test_tokens.valid(test_token2.name))

        test_token3 = test_tokens.new(one_time=True)
        test_token3.use()

        self.assertFalse(test_tokens.valid(test_token2.name))
        self.assertFalse(test_tokens.disable(test_token2.name))
        self.assertFalse(test_tokens.valid(test_token2.name))

    @parameterized.expand([
        [None, False],
        ['2100-01-12', False],
        [None, True],
        ['2100-01-12', True]
    ])
    def test_tokens_new(self, expire, one_time):
        test_tokens = matrix_registration.tokens.Tokens()
        test_token = test_tokens.new(expire=expire, one_time=one_time)

        self.assertIsNotNone(test_token)
        if expire:
            self.assertIsNotNone(test_token.expire)
        else:
            self.assertIsNone(test_token.expire)
        if one_time:
            self.assertTrue(test_token.one_time)
        else:
            self.assertFalse(test_token.one_time)
        self.assertTrue(test_tokens.valid(test_token.name))

    @parameterized.expand([
        [None, False, 10, True],
        ['2100-01-12', False, 10, True],
        [None, True, 1, False],
        [None, True, 0, True],
        ['2100-01-12', True, 1, False],
        ['2100-01-12', True, 2, False],
        ['2100-01-12', True, 0, True]
    ])
    def test_tokens_valid_form(self, expire, one_time, times_used, valid):
        test_tokens = matrix_registration.tokens.Tokens()
        test_token = test_tokens.new(expire=expire, one_time=one_time)

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
        ['2100-01-12', False],
        ['2200-01-13', True],
    ])
    def test_tokens_expired(self, expire, valid):
        test_tokens = matrix_registration.tokens.Tokens()
        test_token = test_tokens.new(expire=expire)

        self.assertEqual(test_tokens.valid(test_token.name), True)
        # date changed to after expiration date
        with patch('matrix_registration.tokens.datetime') as mock_date:
            mock_date.now.return_value = parser.parse('2200-01-12')
            self.assertEqual(test_tokens.valid(test_token.name), valid)


class ApiTest(unittest.TestCase):
    def setUp(self):
        api.app.testing = True
        self.app = api.app.test_client()
        matrix_registration.config.config = Config(CONFIG_PATH)

    def tearDown(self):
        os.remove(matrix_registration.config.config.db)

    @parameterized.expand([
        ['test', 'test1234', 'test1234', True, 200],
        ['test', 'test1234', 'test1234', False, 401],
        ['@test:matrix.org', 'test1234', 'test1234', True, 200],
        ['test', 'test1234', 'tet1234', True, 401],
        ['teüst', 'test1234', 'test1234', True, 401],
        ['@test@matrix.org', 'test1234', 'test1234', True, 401],
        ['test@matrix.org', 'test1234', 'test1234', True, 401],
        ['', 'test1234', 'test1234', True, 401],
        ['aRGEZVYZ2YYxvIYVQITke24HurY4ZEMeXWSf2D2kx7rxtRhbO29Ksae0Uthc7m0dQTQBLCuHqdYHe101apCCotILLgqiRELqiRSSlZDT1UEG18ryg04kaCMjODOZXLwVOH78wZIpK4NreYEcpX00Wlkdo4qUfgH9Nlz3AEGZYluWuFeoo4PKj8hRplY9FPQLi5ACgfDgQpG1wrz9BEqtvd1KK5UvE8qLQnK6CZAnsjwNQq9UddvDFY2ngX1ftbqw', 'test1234', 'test1234', True, 401]
    ])
    @patch('matrix_registration.synapse_register.requests.post',
           side_effect=mocked_requests_post)
    def test_register_success(self, username, password, confirm, token,
                              status, mock_get):
        matrix_registration.config.config = Config(CONFIG_PATH)

        matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
        test_token = matrix_registration.tokens.tokens.new(expire=None,
                                                           one_time=True)

        if not token:
            test_token.name = ""
        rv = self.app.post('/register', data=dict(
            username=username,
            password=password,
            confirm=confirm,
            token=test_token.name
        ))
        if rv.status_code == 200:
            account_data = json.loads(rv.data.decode('utf8').replace("'", '"'))
            # print(account_data)
        self.assertEqual(rv.status_code, status)

    # @patch('matrix_registration.synapse_register.requests.post',
    #        side_effect=mocked_requests_post)
    # def test_register_wrong_hs(self, mock_get):
    #     matrix_registration.config.config = Config(CONFIG_PATH)
    #
    #     matrix_registration.tokens.tokens = matrix_registration.tokens.Tokens()
    #     test_token = matrix_registration.tokens.tokens.new(expire=None,
    #                                                        one_time=True)
    #     api.config.config.SERVER_LOCATION = "x"
    #     rv = self.app.post('/register', data=dict(
    #         username='username',
    #         password='password',
    #         confirm='password',
    #         token=test_token.name
    #     ))
    #     self.assertEqual(rv.status_code, 500)


class ConfigTest(unittest.TestCase):
    def test_config_update(self):
        matrix_registration.config.config = Config(CONFIG_PATH)
        self.assertEqual(matrix_registration.config.config.PORT, 5000)

        new_config = "tests/test_config.yaml"
        matrix_registration.config.config.update(new_config)
        self.assertEqual(matrix_registration.config.config.PORT, 1000)

    def test_config_wrong_path(self):
        bad_config = "x"
        with self.assertRaises(SystemExit) as cm:
            matrix_registration.config.config = Config(bad_config)

        matrix_registration.config.config = Config(CONFIG_PATH)
        with self.assertRaises(SystemExit) as cm:
            matrix_registration.config.config.update(bad_config)


if __name__ == '__main__':
    unittest.main()
