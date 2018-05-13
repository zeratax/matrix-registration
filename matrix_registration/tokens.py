# Standard library imports...
from datetime import datetime
import os
import random
import sqlite3

# Third-party imports...
from dateutil import parser

# Local imports...
from .config import config
from .constants import __location__
from .constants import WORD_LIST

WORD_LIST_PATH = os.path.join(__location__, WORD_LIST)
DATABASE_PATH = os.path.join(__location__, "../" + config.DB)

sqlite3.register_adapter(bool, int)
sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))


def random_readable_string(length=3, wordlist=WORD_LIST_PATH):
    with open(wordlist) as f:
        lines = f.read().splitlines()
        string = ""
        
        for n in range(length):
            string += random.choice(lines).title()
    
    return string


class Token(object):
    def __init__(self, expire=None, one_time=False):
        self.expire = expire
        self.one_time = one_time
        self.name = random_readable_string()
        self.used = 0

    def is_expired(self):
        return ((self.expire < datetime.now()) or
                    (self.one_time and self.used))

    def disable(self):
        self.expire = datetime(1, 1, 1)


class Tokens():
    def __init__(self):
        conn = sqlite3.connect(Config['db'])
        self.c = conn.cursor()

        # Create table
        self.c.execute('''CREATE TABLE IF NOT EXISTS tokens
                          (name text UNIQUE, expire text, one_time bool)''')
        # Get tokens
        self.c.execute('SELECT * FROM tokens')

        for token in self.c.fetchall():
            self.tokens.append(Token(token.name,
                                     datetime.time(token.expire), 
                                     token.one_time))

    def verify(self, token_name):
        # self.c.execute('SELECT * FROM tokens WHERE name = {}'.format(token))
        for token in self.tokens:
            if token.name == token_name:
                return not token.is_expired()
                break

    def add(token):
        self.c.execute('INSERT INTO tokens VALUE ("{}", "{}", {})'.format(token.name,
                                                                          token.expire,
                                                                          token.one_time))
        tokens.append(token)
tokens = None
