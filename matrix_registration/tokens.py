from datetime import datetime
import random
import sqlite3

from .config import Config


def random_readable_string(length=3, wordlist='wordlist.txt'):
    lines = open(wordlist).read().splitlines()
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

    def usuable(self, token_name):
        # self.c.execute('SELECT * FROM tokens WHERE name = {}'.format(token))
        for token in self.tokens:
            if token.name == token_name:
                return token.is_expired()

    def add(token):
        self.c.execute('INSERT INTO tokens VALUE ("{}", "{}", {})'.format(token.name,
                                                                          token.expire,
                                                                          token.one_time))
        tokens.append(token)
