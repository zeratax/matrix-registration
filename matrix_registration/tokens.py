# Standard library imports...
from datetime import datetime
import logging
import random
import sqlite3

# Third-party imports...
from dateutil import parser

# Local imports...
from . import config
from .constants import WORD_LIST_PATH

sqlite3.register_adapter(bool, int)
sqlite3.register_converter('BOOLEAN', lambda v: bool(int(v)))


logger = logging.getLogger(__name__)


def random_readable_string(length=3, wordlist=WORD_LIST_PATH):
    with open(wordlist) as f:
        lines = f.read().splitlines()
        string = ''
        for _ in range(length):
            string += random.choice(lines).title()
    return string


class Token(object):
    def __init__(self, name=False, ex_date=None, one_time=False, used=0):
        if not ex_date or ex_date == 'None':
            self.ex_date = None
        else:
            self.ex_date = parser.parse(ex_date)
        if name:
            self.name = name
        else:
            self.name = random_readable_string()
        self.one_time = one_time
        self.used = used

    def __repr__(self):
        return self.name

    def toDict(self):
        _token = {
            'name': self.name,
            'used': self.used,
            'ex_date': self.ex_date,
            'one_time': bool(self.one_time),
            'valid': self.valid()
        }
        return _token

    def valid(self):
        expired = False
        if self.ex_date:
            expired = self.ex_date < datetime.now()
        used = bool(self.one_time and self.used > 0)

        return (not expired) and (not used)

    def use(self):
        if self.valid():
            self.used += 1
            return True
        return False

    def disable(self):
        if self.valid():
            self.ex_date = datetime(1, 1, 1)
            return True
        return False


class Tokens():
    def __init__(self):
        logger.info('connecting to %s' % config.config.db)
        self.conn = sqlite3.connect(config.config.db, check_same_thread=False)
        self.c = self.conn.cursor()
        self.tokens = {}

        logger.debug('creating table')
        self.c.execute('''CREATE TABLE IF NOT EXISTS tokens
                          (name TEXT UNIQUE,
                          ex_date TEXT,
                          one_time BOOLEAN,
                          used INT)''')
        self.conn.commit()

        self.load()

    def __repr__(self):
        result = ''
        for tokens_key in self.tokens:
            result += '%s, ' % tokens_key
        return result[:-2]

    def toList(self):
        _tokens = []
        for tokens_key in self.tokens:
            _tokens.append(self.tokens[tokens_key].toDict())
        return _tokens

    def update(self, token):
        sql = 'UPDATE tokens SET used=?, ex_date=? WHERE name=?'
        self.c.execute(sql, (token.used, str(token.ex_date), token.name))
        self.conn.commit()

    def load(self):
        logger.debug('loading tokens from db...')
        self.tokens = {}
        # Get tokens
        self.c.execute('SELECT * FROM tokens')
        for token in self.c.fetchall():
            logger.debug(token)
            # token[0]=name
            self.tokens[token[0]] = Token(name=token[0],
                                          ex_date=str(token[1]),
                                          one_time=token[2],
                                          used=token[3])
        logger.debug('token loaded!')

    def get_token(self, token_name):
        logger.debug('getting token by name: %s' % token_name)
        try:
            token = self.tokens[token_name]
        except KeyError:
            return False
        return token

    def valid(self, token_name):
        logger.debug('checking if "%s" is valid' % token_name)
        token = self.get_token(token_name)
        # if token exists
        if token:
            return token.valid()
        return False

    def use(self, token_name):
        logger.debug('using token: %s' % token_name)
        token = self.get_token(token_name)
        if token:
            if token.use():
                self.update(token)
                return True
        return False

    def disable(self, token_name):
        logger.debug('disabling token: %s' % token_name)
        token = self.get_token(token_name)
        if token:
            if token.disable():
                self.update(token)
                return True
            self.update(token)
        return False

    def new(self, ex_date=None, one_time=False):
        logger.debug(('creating new token, with options: one_time: {},' +
                     'ex_dates: {}').format(one_time, ex_date))
        token = Token(ex_date=ex_date, one_time=one_time)
        sql = '''INSERT INTO tokens (name, ex_date, one_time, used)
                     VALUES (?, ?, ?, ?)'''

        self.c.execute(sql, (token.name,
                             str(token.ex_date),
                             token.one_time,
                             token.used))
        self.tokens[token.name] = token
        self.conn.commit()

        return token


tokens = None
