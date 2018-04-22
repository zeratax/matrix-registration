import argparse
import sys
import logging

from .config import Config
from .tokens import Tokens
from .tokens import Token
from .api import app

log = logging.getLogger('m_reg')
time_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s@%(name)s] %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(time_formatter)
log.addHandler(handler)

parser = argparse.ArgumentParser(
    description='a token based Matrix-registration api',
    prog='python -m matrtrix_registration')
parser.add_argument('-c', '--config', type=str, default='config.yaml',
                    metavar='<path>', help='the path to your config file')
parser.add_argument('mode', choices=['api', 'token'], 
                    help='start as api server or generate new token')
parser.add_argument('-o', '--one-time', type=bool, default=False, 
                    help='one time use token')
parser.add_argument('-e', '--expire', type=str, default=False, 
                        help='expiration date for token')
args = parser.parse_args()

config = Config(arg.config)
config.load()
config.update()

tokens = Tokens()

if args.mode == 'api':
    app.run(host='0.0.0.0', port=config['PORT'])
elif args.mode == 'token':
    tokens.add(Token(expire=args.expire, one_time=args.one_time))
