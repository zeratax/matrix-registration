# Standard library imports...
import os
import sys

# Third-party imports...
import yaml

# Local imports...
from .constants import __location__


class Config:
    def __init__(self, path):
        self.path = path
        self.options = None
        self.load()

    def load(self):
        try:
            with open((os.path.join(__location__, "../" + self.path)),
                      'r') as stream:
                dictionary = yaml.load(stream)
                for k, v in dictionary.items():
                    setattr(self, k, v)
        except IOError as e:
            sys.exit(e)

    def update(self, path):
        self.path = path
        self.options = None
        self.load()


config = None
