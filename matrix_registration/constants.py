# Standard library imports...
import os
import site
import sys

# Third-party imports...
from appdirs import user_config_dir

__location__ = os.path.realpath(os.path.join(os.getcwd(),
                                os.path.dirname(__file__)))
WORD_LIST_PATH = os.path.join(__location__, 'wordlist.txt')
CONFIG_PATH1 = os.path.join(__location__, '../')
CONFIG_PATH2 = os.path.join(sys.prefix, 'config/')
CONFIG_PATH3 = os.path.join(user_config_dir('matrix-registration') + '/')
CONFIG_PATH4 = os.path.join(site.USER_BASE, 'config/')

