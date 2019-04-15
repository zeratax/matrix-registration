# Standard library imports...
# from collections import namedtuple
import logging
import os
import sys

# Third-party imports...
import yaml

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, data):
        self.data = data
        self.options = None
        self.load()

    def load(self):
        logger.debug('loading config...')
        dictionary = None
        if type(self.data) is dict:
            logger.debug('from dict...')
            dictionary = self.data
        else:
            logger.debug('from file...')
            try:
                with open(self.data, 'r') as stream:
                    dictionary = yaml.load(stream, Loader=yaml.SafeLoader)
            except IOError as e:
                sys.exit(e)

        logger.debug('setting config...')
        # recusively set dictionary to class properties
        for k, v in dictionary.items():
            setattr(self, k, v)
        logger.debug('config set!')
        # self.x = namedtuple('config',
        #                     dictionary.keys())(*dictionary.values())

    def update(self, data):
        logger.debug('updating config...')
        self.data = data
        self.options = None
        self.load()
        logger.debug('config updated!')


config = None
