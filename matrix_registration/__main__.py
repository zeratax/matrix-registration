# standard library imports...
import argparse
import logging
import logging.config

# third party imports...
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
from flask_cors import CORS

# local imports...
from . import config
from . import tokens
from .api import app


config.config = config.Config('config.yaml')
logging.config.dictConfig(config.config.logging)
tokens.tokens = tokens.Tokens()

logger = logging.getLogger(__name__)


def run_api(args):
    Limiter(
        app,
        key_func=get_ipaddr,
        default_limits=config.config.rate_limit
    )
    if config.config.allow_cors:
        CORS(app)
    app.run(host='0.0.0.0', port=config.config.port)


def generate_token(args):
    token = tokens.tokens.new(ex_date=args.expire, one_time=args.one_time)
    print(token.name)


def status_token(args):
    if args.disable:
        print(tokens.tokens.disable(args.disable))
    if args.status:
        print(tokens.tokens.get_token(args.status))
    if args.list:
        # print(json.dumps(tokens.tokens.__dict__,
        #                  sort_keys=True,
        #                  indent=4,
        #                  default=str))
        print(tokens.tokens)
def main():
    parser = argparse.ArgumentParser(
        description='a token based matrix registration app',
        prog='python -m matrix_registration')

    # subparser
    subparsers = parser.add_subparsers(
                            help='sub-commands. for ex. \'gen -h\' ' +
                            'for additional help')

    # api-parser
    parser_a = subparsers.add_parser('api', help='start as api')
    parser_a.set_defaults(func=run_api)

    # generate-parser
    parser_g = subparsers.add_parser('gen',
                                     help='generate new token. ' +
                                     '-o onetime, -e expire date')
    parser_g.add_argument('-o', '--one-time', action='store_true',
                          help='make token one-time-useable')
    parser_g.add_argument('-e', '--expire', type=str, default=None,
                          help='expire date: DD.MM.YYYY')
    parser_g.set_defaults(func=generate_token)

    # status-parser
    parser_s = subparsers.add_parser('status',
                                     help='view status or disable ' +
                                     'token. -s status, -d disable, -l list')
    parser_s.add_argument('-s', '--status', type=str, default=None,
                          help='token status')
    parser_s.add_argument('-l', '--list', action='store_true',
                          help='list tokens')
    parser_s.add_argument('-d', '--disable', type=str, default=None,
                          help='disable token')
    parser_s.set_defaults(func=status_token)

    args = parser.parse_args()
    logger.debug('called with args: %s' % args)
    if 'func' in args:
        args.func(args)

if __name__ == '__main__':
    main()
