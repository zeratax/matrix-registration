# Standard library imports...
from datetime import datetime
import logging
import random

from flask_sqlalchemy import SQLAlchemy

# Local imports...
from .constants import WORD_LIST_PATH


logger = logging.getLogger(__name__)

db = SQLAlchemy()


def random_readable_string(length=3, wordlist=WORD_LIST_PATH):
    with open(wordlist) as f:
        lines = f.read().splitlines()
        string = ''
        for _ in range(length):
            string += random.choice(lines).title()
    return string


class Token(db.Model):
    __tablename__ = 'tokens'
    name = db.Column(db.String(255), primary_key=True)
    ex_date = db.Column(db.DateTime, nullable=True)
    one_time = db.Column(db.Boolean, default=False)
    used = db.Column(db.Integer, default=0)

    def __init__(self, **kwargs):
        super(Token, self).__init__(**kwargs)
        if not self.name:
            self.name = random_readable_string()
        if self.used is None:
            self.used = 0
        if self.one_time is None:
            self.one_time = False

    def __repr__(self):
        return self.name

    def toDict(self):
        _token = {
            'name': self.name,
            'used': self.used,
            'ex_date': str(self.ex_date) if self.ex_date else None,
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
        self.tokens = {}

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

    def load(self):
        logger.debug('loading tokens from db...')
        self.tokens = {}
        for token in Token.query.all():
            logger.debug(token)
            self.tokens[token.name] = token

        logger.debug('token loaded!')

    def get_token(self, token_name):
        logger.debug('getting token by name: %s' % token_name)
        try:
            token = Token.query.filter_by(name=token_name).first()
        except KeyError:
            return False
        return token

    def valid(self, token_name):
        logger.debug('checking if "%s" is valid' % token_name)
        token = self.get_token(token_name)
        if token:
            return token.valid()
        return False

    def use(self, token_name):
        logger.debug('using token: %s' % token_name)
        token = self.get_token(token_name)
        if token:
            if token.use():
                db.session.commit()
                return True
        return False

    def disable(self, token_name):
        logger.debug('disabling token: %s' % token_name)
        token = self.get_token(token_name)
        if token:
            if token.disable():
                db.session.commit()
                return True
        return False

    def new(self, ex_date=None, one_time=False):
        logger.debug(('creating new token, with options: one_time: {},' +
                     'ex_dates: {}').format(one_time, ex_date))
        token = Token(ex_date=ex_date, one_time=one_time)
        self.tokens[token.name] = token
        db.session.add(token)
        db.session.commit()

        return token


tokens = None
