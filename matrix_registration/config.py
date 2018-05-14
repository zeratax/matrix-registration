# Standard library imports...
import os
import sys

# Third-party imports...
import yaml


class Config:
    def __init__(self, data):
        self.data = data
        self.options = None
        self.load()

    def load(self):
        dictionary = None
        if type(self.data) is dict:
            dictionary = self.data
        else:
            try:
                with open(self.data, 'r') as stream:
                    dictionary = yaml.load(stream)
            except IOError as e:
                sys.exit(e)

        # recusively set dictionary to class properties
        for k, v in dictionary.items():
            setattr(self, k, v)

    def update(self, data):
        self.data = data
        self.options = None
        self.load()


config = None
