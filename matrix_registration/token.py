import datetime
import random


def random_readable_string(length=3, wordlist='wordlist.txt'):
    lines = open(wordlist).read().splitlines()
    string = ""
    for n in range(length):
        string += random.choice(lines)
    return string

class Token(object):
    def __init__(self, expire=None, one_time=False):
        self.expire = expire
        self.one_time = one_time
        self.name = random_readable_string()
        self.used = 0

    def is_expired(self):
        return ((self.expire < datetime.datetime.now()) or
                    (self.one_time and self.used))

    def disable(self):
        self.expire = datetime.datetime(1, 1, 1)

