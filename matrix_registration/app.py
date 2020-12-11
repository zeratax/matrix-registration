import logging
import logging.config
import click
import json

from flask import Flask
from flask.cli import FlaskGroup, pass_script_info
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
from flask_cors import CORS
from waitress import serve

from . import config
from . import tokens
from .tokens import db
import os

def create_app(testing=False):
    app = Flask(__name__)
    app.testing = testing

    with app.app_context():
        from .api import api
        app.register_blueprint(api)

    return app


@click.group(cls=FlaskGroup, add_default_commands=False, create_app=create_app, context_settings=dict(help_option_names=['-h', '--help']))
@click.option("--config-path", default="config.yaml", help='specifies the config file to be used')
@pass_script_info
def cli(info, config_path):
    """a token based matrix registration app"""
    config.config = config.Config(config_path)
    logging.config.dictConfig(config.config.logging)
    app = info.load_app()
    with app.app_context():
        app.config.from_mapping(
            SQLALCHEMY_DATABASE_URI=config.config.db.format(cwd=f"{os.getcwd()}/"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False
        )
        db.init_app(app)
        db.create_all()
        tokens.tokens = tokens.Tokens()


@cli.command("serve", help="start api server")
@pass_script_info
def run_server(info):
    app = info.load_app()
    Limiter(
        app,
        key_func=get_ipaddr,
        default_limits=config.config.rate_limit
    )
    if config.config.allow_cors:
        CORS(app)
    serve(app, host=config.config.host, port=config.config.port, url_prefix=config.config.base_url)


@cli.command("generate", help="generate new token")
@click.option("-o", "--one-time", is_flag=True, help="make token one-time-useable")
@click.option("-e", "--expires", type=click.DateTime(formats=["%Y-%m-%d"]), default=None, help='expire date: in ISO-8601 format (YYYY-MM-DD)')
def generate_token(one_time, expires):
    token = tokens.tokens.new(ex_date=expires, one_time=one_time)
    print(token.name)


@cli.command("status", help="view status or disable")
@click.option("-s", "--status", default=None, help="token status")
@click.option("-l", "--list", is_flag=True, help="list tokens")
@click.option("-d", "--disable", default=None, help="disable token")
def status_token(status, list, disable):
    if disable:
        if tokens.tokens.disable(disable):
            print("Token disabled")
        else:
            print("Token couldn't be disabled")
    if status:
        token = tokens.tokens.get_token(status)
        if token:
            print(f"This token is{' ' if token.valid else ' not '}valid")
            print(json.dumps(token.toDict(), indent=2))
        else:
            print("No token with that name")
    if list:
        print(tokens.tokens)
