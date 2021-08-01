# Standard library imports...
# from collections import namedtuple
import logging
import os
import sys

# Third-party imports...
import yaml
from jsonschema import validate, ValidationError

# Local imports...
from .constants import (
    CONFIG_SCHEMA_PATH,
    CONFIG_PATH1,
    CONFIG_PATH2,
    CONFIG_PATH3,
    CONFIG_PATH4,
    CONFIG_PATH5
)
CONFIG_PATHS = [
    CONFIG_PATH1,
    CONFIG_PATH2,
    CONFIG_PATH3,
    CONFIG_PATH4,
    CONFIG_PATH5
]

CONFIG_SAMPLE_NAME = "config.sample.yaml"
CONFIG_NAME = 'config.yaml'
logger = logging.getLogger(__name__)


class Config:
    """
    Config

    loads a dict or a yaml file to be accessible by all files in the module
    """
    def __init__(self, data):
        self.secrets_dir = os.getenv("CREDENTIALS_DIRECTORY")
        self.data = data
        self.CONFIG_PATH = None
        self.location = None
        self.load()

    def load(self):
        """
        loads the dict/the yaml file and recursively sets dictionary to class properties
        """
        logger.debug('loading config...')
        dictionary = None
        config_default = True
        if type(self.data) is dict:
            logger.debug('from dict...')
            dictionary = self.data
            config_default = False 
        else:
            logger.debug('from file...')
            # check work dir and all other pip install locations for config
            if os.path.isfile(self.data):
                config_default = False
            else:
                # provided file not found checking typical installation dirs
                config_exists = False
                for path in CONFIG_PATHS:
                    if os.path.isfile(path + CONFIG_NAME):
                        self.CONFIG_PATH = path
                        config_exists = True
                        config_default = False
                if not config_exists:
                    # no config exists, use sample config instead
                    # check typical installation dirs for sample configs
                    for path in CONFIG_PATHS:
                        if os.path.isfile(path + CONFIG_SAMPLE_NAME):
                            self.CONFIG_PATH = path
                            config_exists = True
                    # check if still no config found
                    if not config_exists:
                        sys.exit('could not find any configuration file!')
                    self.data = os.path.join(self.CONFIG_PATH, CONFIG_SAMPLE_NAME)
                else:
                    self.data = os.path.join(self.CONFIG_PATH, CONFIG_NAME)
            try:
                with open(self.data, 'r') as stream:
                    dictionary = yaml.load(stream, Loader=yaml.SafeLoader)
                with open(CONFIG_SCHEMA_PATH, 'r') as schemafile:
                    validate(dictionary, yaml.safe_load(schemafile))               
            except ValidationError as e:
                sys.exit("Check you config and update it to the newest version! Do you have missing fields in your config.yaml?\n\nTraceback:\n"+str(e))
            except yaml.YAMLError as e:
                sys.exit("Invalid YAML Syntax\n\nTraceback:\n"+str(e))
            except IOError as e:
                sys.exit(e)
        if config_default:
            self.read_config(dictionary)

        logger.debug('setting config...')
        # recusively set dictionary to class properties
        for k, v in dictionary.items():
            setattr(self, k, v)

        logger.debug('checking for secrets...')
        if self.secrets_dir:
            self.get_secrets()
        logger.debug('config set!')
        # self.x = namedtuple('config',
        #                     dictionary.keys())(*dictionary.values())

    def update(self, data):
        """
        resets all options and loads the new config

        Parameters
        ----------
        arg1 : dict or path to config file
        """
        logger.debug('updating config...')
        self.data = data
        self.CONFIG_PATH = None
        self.location = None
        self.load()
        logger.debug('config updated!')

    def read_config(self, dictionary):
        """
        asks the user how to set the essential options

        Parameters
        ----------
        arg1 : dict
            with sample values
        """
        # important keys that need to be changed
        keys = ['server_location', 'server_name', 'port', 'registration_shared_secret']
        for key in keys:
            temp = dictionary[key]
            dictionary[key] = input('enter {}, e.g. {}\n'.format(key, temp))
            if not dictionary[key].strip():
                dictionary[key] = temp
        # write to config file
        new_config_path = self.CONFIG_PATH + CONFIG_NAME
        relative_path = os.path.relpath(self.CONFIG_PATH + CONFIG_NAME)
        with open(new_config_path, 'w') as stream:
            yaml.dump(dictionary, stream, default_flow_style=False)
            print('config ile written to "%s"' % relative_path)

    def get_secrets(self):
        with open(f"{self.secrets_dir}/secrets") as file:
            for line in file:
                try:
                    k, v = line.lower().split('=')
                except NameError:
                    logger.error(f'secret "{line}" in wrong format, please use "key=value"')  
                setattr(self, k.strip(), v.strip())


config = None
