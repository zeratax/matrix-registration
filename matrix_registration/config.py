# Standard library imports...
# from collections import namedtuple
import logging
import os
import sys

# Third-party imports...
import yaml

# Local imports...
from .constants import CONFIG_SAMPLE_PATH

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, data):
        self.data = data
        self.options = None
        self.load()

    def load(self):
        logger.debug('loading config...')
        dictionary = None
        config_exists = True
        if type(self.data) is dict:
            logger.debug('from dict...')
            dictionary = self.data
        else:
            logger.debug('from file...')
            if not os.path.isfile(self.data):
                config_exists = False
                self.data = CONFIG_SAMPLE_PATH
            try:
                with open(self.data, 'r') as stream:
                    dictionary = yaml.load(stream, Loader=yaml.SafeLoader)
            except IOError as e:
                sys.exit(e)
        if not config_exists:
            self.read_config(dictionary)

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

    def read_config(self, dictionary):
        # important keys that need to be changed
        keys = ['server_location', 'server_name', 'shared_secret', 'port']
        for key in keys:
            temp = dictionary[key]
            dictionary[key] = input("enter {}, e.g. {}\n".format(key, temp))
            if not dictionary[key].strip():
                dictionary[key] = temp
        with open('config.yaml', 'w') as stream:
            yaml.dump(dictionary, stream, default_flow_style=False)



config = None
