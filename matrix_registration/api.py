# Standard library imports...
import hashlib
import hmac
import yaml
import requests
import re
import sys
from urllib.parse import urlparse

# Third-party imports...
from flask import Flask, abort, jsonify, request
from wtforms import Form, BooleanField, StringField, PasswordField, validators

# Local imports...
from .matrix_api import create_account
from . import config
from . import tokens


app = Flask(__name__)


def validate_token(form, token):
    tokens.tokens.load()
    if not tokens.tokens.valid(token.data):
        raise validators.ValidationError('this token is not valid')


def validate_username(form, username):
    domain = urlparse(config.config.server_location).hostname
    re_mxid = re.compile(r"^@?[a-zA-Z_\-=\.\/0-9]+(:" +
                         re.escape(domain) +
                         ")?$")
    if not re_mxid.match(username.data):
        raise validators.ValidationError('this username is not valid')


class RegistrationForm(Form):
    username = StringField('Username', [
        validators.Length(min=1, max=200),
        validate_username
    ])
    password = PasswordField('New Password', [
        validators.Length(min=1 if not config.config else config.config.password.min_length),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    token = StringField('Token', [validate_token])


@app.route('/register', methods=['POST'])
def register():
    app.logger.debug('an account registration was requested...')
    form = RegistrationForm(request.form)
    if form.validate():
        tokens.tokens.use(form.token.data)
        username = form.username.data.rsplit(":")[0].split("@")[-1]
        app.logger.debug('creating account %s...' % username)
        try:
            account_data = create_account(form.username.data,
                                          form.password.data,
                                          config.config.server_location,
                                          config.config.shared_secret)
        except requests.exceptions.ConnectionError as e:
            app.logger.error('no HS at SERVER_LOCATION',
                             exc_info=True)
            abort(500)
        except requests.exceptions.HTTPError as e:
            resp = e.response
            error = resp.json()
            status_code = resp.status_code
            if status_code == 400:
                app.logger.debug('malformed user registration data')
                return jsonify(errcode=error['errcode'],
                               error=error['error'],
                               status_code=400)
            elif status_code == 404:
                app.logger.error('no HS found at SERVER_LOCATION')
            elif status_code == 403:
                app.logger.error('wrong registration secret')
            else:
                app.logger.error('failure communicating with HS',
                                 exc_info=True)
            abort(500)
        if not account_data:
            app.logger.error('no account data was returned')
            abort(500)
        app.logger.debug('account creation succeded!')
        return jsonify(access_token=account_data['access_token'],
                       device_id=account_data['device_id'],
                       home_server=account_data['home_server'],
                       user_id=account_data['user_id'],
                       status_code=200)
    else:
        app.logger.debug('account creation failed!')
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print()  # return error to user
    abort(400)
