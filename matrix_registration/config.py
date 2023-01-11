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
    CONFIG_DIR1,
    CONFIG_DIR2,
    CONFIG_DIR3,
    CONFIG_DIR4,
    CONFIG_DIR5,
)

CONFIG_DIRS = [CONFIG_DIR1, CONFIG_DIR2, CONFIG_DIR3, CONFIG_DIR4, CONFIG_DIR5]

CONFIG_SAMPLE_NAME = "config.sample.yaml"
CONFIG_NAME = "config.yaml"
logger = logging.getLogger(__name__)


class Config:
    """
    Config

    loads a dict or a yaml file to be accessible by all files in the module
    """

    def __init__(self, path=None, data=None):
        self.secrets_dir = os.getenv("CREDENTIALS_DIRECTORY")
        self.data = data
        self.path = path
        self.default = True

        self.load()
        if self.secrets_dir:
            self.load_secrets()
        self.apply_options()

    def load(self):
        """
        loads the options
        """
        logger.debug("loading config...")
        if self.data:
            logger.debug("from dict...")
            config_default = False
            return

        logger.debug("from file...")
        self.load_from_file()

    def load_from_file(self):
        """
        loads the options from a file
        """
        options = None
        if not self.check_config_locations():
            sys.exit("could not find any configuration file!")
        logger.debug(f"config found!")

        try:
            with open(self.path, "r") as stream:
                options = yaml.load(stream, Loader=yaml.SafeLoader)
            with open(CONFIG_SCHEMA_PATH, "r") as schemafile:
                validate(options, yaml.safe_load(schemafile))
        except ValidationError as e:
            sys.exit(
                "Check you config and update it to the newest version! Do you have missing fields in your config.yaml?\n\nTraceback:\n"
                + str(e)
            )
        except yaml.YAMLError as e:
            sys.exit("Invalid YAML Syntax\n\nTraceback:\n" + str(e))
        except IOError as e:
            sys.exit(e)

        if not options:
            sys.exit("could not read file")

        if self.default:
            # ask for options that should not be set to default
            options = self.ask_for_options(options)

        self.data = options

    def load_secrets(self):
        """
        loads secret options, see https://systemd.io/CREDENTIALS/
        """
        with open(f"{self.secrets_dir}/secrets") as file:
            for line in file:
                try:
                    k, v = line.lower().split("=")
                except NameError:
                    logger.error(
                        f'secret "{line}" in wrong format, please use "key=value"'
                    )
                setattr(self, k.strip(), v.strip())

    def check_config_locations(self):
        """
        checks multiple locations for the config or config sample file
        """
        if self.path:
            logger.debug(f"checking {self.path} ...")
            if os.path.isfile(self.path):
                self.default = False
                return True
            else:
                sys.exit("no configuration file at specified location")

        # check possible locations for config file
        for directory in CONFIG_DIRS:
            logger.debug(f"checking {directory} ...")
            path = directory + CONFIG_SAMPLE_NAME
            if os.path.isfile(path):
                self.path = path
                self.default = False
                return True

        # no config exists, use sample config instead
        # check typical installation dirs for sample configs
        for directory in CONFIG_DIRS:
            path = directory + CONFIG_SAMPLE_NAME
            if os.path.isfile(directory + CONFIG_SAMPLE_NAME):
                self.path = path
                self.config_exists = True
                return True

        return False

    def apply_options(self):
        """
        applies options to the config object
        """
        logger.debug("applying options...")
        # recusively set dictionary to class properties
        for k, v in self.data.items():
            setattr(self, k, v)

    def ask_for_options(self, sample_options):
        """
        asks the user how to set the essential options

        Parameters
        ----------
        arg1 : dict
            with default values
        """
        # important keys that need to be changed
        keys = ["server_location", "server_name", "port", "registration_shared_secret"]
        for key in keys:
            temp = sample_options[key]
            sample_options[key] = input("enter {}, e.g. {}\n".format(key, temp))
            if not sample_options[key].strip():
                sample_options[key] = temp

        return sample_options

        # write to config file
        directory = os.path.dirname(os.path.realpath(self.path))
        new_path = f"{directory}/{CONFIG_NAME}"
        with open(new_path, "w") as stream:
            yaml.dump(self.data, stream, default_flow_style=False)
            print(f'config file written to "{os.path.relpath(new_path)}"')
            print()

    def update(self, data):
        """
        resets all options and loads the new config

        Parameters
        ----------
        arg1 : dict or path to config file
        """
        logger.debug("updating config...")
        self.data = data
        self.path = None
        self.load()
        if self.secrets_dir:
            self.load_secrets()
        self.apply_options()
        logger.debug("config updated!")


config = None
