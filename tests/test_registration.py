import re
import unittest

from .context import matrix_registration

class TokensTest(unittest.TestCase):
    def test_random_readable_string(self):
        for n in range(10):
            string = tokens.random_readable_string(length=n)
            words = re.sub('([a-z])([A-Z])', r'\1 \2', string).split()
            self.assertEqual(len(words), n)

