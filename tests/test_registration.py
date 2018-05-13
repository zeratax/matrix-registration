# Standard library imports...
from datetime import date
import json
import unittest
from unittest.mock import Mock, patch
import os
import re

# Third-party imports...
from parameterized import parameterized
from dateutil import parser

# Local imports...
import matrix_registration
from matrix_registration.config import Config

api = matrix_registration.api

CONFIG_PATH = "tests/config.yaml"


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            return self.status_code

    if args[0] == '%s/_matrix/client/api/v1/register' % matrix_registration.config.config.SERVER_LOCATION:
        return MockResponse({
                            'access_token': 'abc123',
                            'device_id': 'GHTYAJCE',
                            'home_server': 'matrix.org',
                            'user_id': '@cheeky_monkey:matrix.org',
                            }, 200)
    return MockResponse(None, 404)


class TokensTest(unittest.TestCase):
    def setUpClass():
        matrix_registration.config.config = Config(CONFIG_PATH)
        print(matrix_registration.config.config.DB)

    def tearDownClass():
        os.remove(matrix_registration.config.config.DB)

    def test_random_readable_string(self):
        for n in range(10):
            string = matrix_registration.tokens.random_readable_string(length=n)
            words = re.sub('([a-z])([A-Z])', r'\1 \2', string).split()
            self.assertEqual(len(words), n)

    @parameterized.expand([
        [None, False],
        ["2100-01-12", False],
        [None, True],
        ["2100-01-12", True]
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
        ["2100-01-12", False, 10, True],
        [None, True, 1, False],
        [None, True, 0, True],
        ["2100-01-12", True, 1, False],
        ["2100-01-12", True, 2, False],
        ["2100-01-12", True, 0, True]
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
        ["2100-01-12", False],
        ["2100-01-12", False],
        ["2100-01-12", False]
    ])
    def test_tokens_expired(self, expire, valid):
        test_tokens = matrix_registration.tokens.Tokens()
        test_token = test_tokens.new(expire=expire)

        self.assertEqual(test_tokens.valid(test_token.name), True)
        # date changed to after expiration date
        with patch('matrix_registration.tokens.datetime') as mock_date:
            mock_date.now.return_value = parser.parse("2200-01-12")
            self.assertEqual(test_tokens.valid(test_token.name), valid)


class ApiTest(unittest.TestCase):
    def setUp(self):
        api.app.testing = True
        self.app = api.app.test_client()
        matrix_registration.config.config = Config(CONFIG_PATH)

    def tearDown(self):
        os.remove(matrix_registration.config.config.DB)

    @patch('matrix_registration.synapse_register.requests.post',
           side_effect=mocked_requests_post)
    def test_register_success(self, mock_get):
        matrix_registration.config.config = Config(CONFIG_PATH)

        matrix_registration.tokens.tokens =  matrix_registration.tokens.Tokens()
        test_token = matrix_registration.tokens.tokens.new(expire=None,
                                                           one_time=True)
        rv = self.app.post('/register', data=dict(
            username='test',
            password='test1234',
            confirm='test1234',
            token=test_token.name
        ))
        # account_data = json.loads(rv.data.decode('utf8').replace("'", '"'))
        self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()
