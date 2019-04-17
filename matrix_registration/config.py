# Standard library imports...
# from collections import namedtuple
import logging
import os
import sys

# Third-party imports...
import yaml

# Local imports...
from .constants import (
    CONFIG_PATH1,
    CONFIG_PATH2,
    CONFIG_PATH3
)
CONFIG_SAMPLE_NAME = "config.sample.yaml"
CONFIG_NAME = 'config.yaml'
logger = logging.getLogger(__name__)


class Config:
    def __init__(self, data):
        self.data = data
        self.CONFIG_PATH = None
        self.location = None
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
            # check work dir and all other pip install locations for config
            if os.path.isfile(self.data):
                self.CONFIG_PATH = ""
            elif os.path.isfile(CONFIG_PATH1 + CONFIG_NAME):
                self.CONFIG_PATH = CONFIG_PATH1
            elif os.path.isfile(CONFIG_PATH2 + CONFIG_NAME):
                self.CONFIG_PATH = CONFIG_PATH2
            elif os.path.isfile(CONFIG_PATH3 + CONFIG_NAME):
                self.CONFIG_PATH = CONFIG_PATH3
            else:
                config_exists = False
            if not config_exists:
                # get config from config sample
                if os.path.isfile(CONFIG_PATH1 + CONFIG_SAMPLE_NAME):
                    self.CONFIG_PATH = CONFIG_PATH1
                elif os.path.isfile(CONFIG_PATH2 + CONFIG_SAMPLE_NAME):
                    self.CONFIG_PATH = CONFIG_PATH2
                elif os.path.isfile(CONFIG_PATH3 + CONFIG_SAMPLE_NAME):
                    self.CONFIG_PATH = CONFIG_PATH3
                else:
                    sys.exit("could not find any configuration file!")
                self.data = self.CONFIG_PATH + CONFIG_SAMPLE_NAME
            else:
                self.data = self.CONFIG_PATH + CONFIG_NAME
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
        self.CONFIG_PATH = None
        self.location = None
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
        # write to config file
        new_config_path = self.CONFIG_PATH + CONFIG_NAME
        relative_path = os.path.relpath(self.CONFIG_PATH + CONFIG_NAME)
        with open(new_config_path, 'w') as stream:
            yaml.dump(dictionary, stream, default_flow_style=False)
            print("config file written to '%s'" % relative_path)


config = None
