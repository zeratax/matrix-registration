# Standard library imports...
import os
import site
import sys

# Third-party imports...
from appdirs import user_config_dir

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
WORD_LIST_PATH = os.path.join(__location__, "wordlist.txt")
CONFIG_SCHEMA_PATH = os.path.join(__location__, "config.schema.json")
# first check in current working dir
CONFIG_DIR1 = os.path.join(os.getcwd() + "/")
CONFIG_DIR2 = os.path.join(os.getcwd() + "/config/")
# then check in XDG_CONFIG_HOME
CONFIG_DIR3 = os.path.join(user_config_dir("matrix-registration") + "/")
# check at installed location
CONFIG_DIR4 = os.path.join(__location__, "../")
CONFIG_DIR5 = os.path.join(sys.prefix, "config/")
