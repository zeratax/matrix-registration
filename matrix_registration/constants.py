# Standard library imports...
import os
import site
import sys

# Third-party imports...
from appdirs import user_config_dir

__location__ = os.path.realpath(os.path.join(os.getcwd(),
                                os.path.dirname(__file__)))
WORD_LIST_PATH = os.path.join(__location__, 'wordlist.txt')
# first check in current working dir
CONFIG_PATH1 = os.path.join(os.getcwd() + '/')
CONFIG_PATH2 = os.path.join(os.getcwd() + '/config/')
# then check in XDG_CONFIG_HOME
CONFIG_PATH3 = os.path.join(user_config_dir('matrix-registration') + '/')
# check at installed location
CONFIG_PATH4 = os.path.join(__location__, '../')
CONFIG_PATH5 = os.path.join(sys.prefix, 'config/')

