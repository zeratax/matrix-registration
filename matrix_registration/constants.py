# Standard library imports...
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(),
                                os.path.dirname(__file__)))
WORD_LIST_PATH = os.path.join(__location__, 'wordlist.txt')
CONFIG_SAMPLE_PATH = os.path.join(__location__, 'config.sample.yaml')
