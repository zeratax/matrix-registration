# Standard library imports...
from datetime import datetime
import os
import random
import sqlite3

# Third-party imports...
from dateutil import parser

# Local imports...
from . import config
from .constants import __location__
from .constants import WORD_LIST

WORD_LIST_PATH = os.path.join(__location__, WORD_LIST)

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
    def __init__(self, name=False, expire=None, one_time=False):
        if not expire or expire == "None":
            self.expire = None
        else:
            self.expire = parser.parse(expire)
        self.one_time = one_time
        if name:
            self.name = name
        else:
            self.name = random_readable_string()
        self.used = 0

    def is_expired(self):
        expired = False
        if self.expire:
            expired = self.expire < datetime.now()
        used = self.one_time and self.used >= 1

        return expired or used

    def disable(self):
        self.expire = datetime(1, 1, 1)


class Tokens():
    def __init__(self):
        DATABASE_PATH = os.path.join(__location__, "../" + config.config.DB)
        self.conn = sqlite3.connect(DATABASE_PATH)
        print(DATABASE_PATH)
        self.c = self.conn.cursor()
        self.tokens = []

        # Create table
        self.c.execute('''CREATE TABLE IF NOT EXISTS tokens
                          (name TEXT UNIQUE, expire TEXT, one_time BOOLEAN)''')
        self.conn.commit()

        self.load()

    def load(self):
        self.tokens = []
        # Get tokens
        self.c.execute('SELECT * FROM tokens')
        for token in self.c.fetchall():
            self.tokens.append(Token(name=token[0],
                                     expire=str(token[1]),
                                     one_time=token[2]))

    def valid(self, token_name):
        # self.c.execute('SELECT * FROM tokens WHERE name = {}'.format(token))
        # self.load()
        for token in self.tokens:
            if token.name == token_name:
                return not token.is_expired()
                break
        return True

    def use(self, token_name):
        if self.valid(token_name):
            for token in self.tokens:
                if token.name == token_name:
                    token.used += 1
                    return True
        return False

    def new(self, expire=None, one_time=False):
        token = Token(expire=expire, one_time=one_time)
        sql = '''INSERT INTO tokens (name, expire, one_time)
                     VALUES (?, ?, ?)'''

        self.c.execute(sql, (token.name, token.expire, token.one_time))
        self.tokens.append(token)
        self.conn.commit()

        return token


tokens = None
