# Standard library imports...
import hashlib
import hmac
import logging
import yaml
from requests import exceptions
import re
import sys
from urllib.parse import urlparse

# Third-party imports...
from flask import Flask, abort, jsonify, request, make_response
from wtforms import Form, BooleanField, StringField, PasswordField, validators


# Local imports...
from .matrix_api import create_account
from . import config
from . import tokens

app = Flask(__name__)
logger = logging.getLogger(__name__)


re_mxid = re.compile(r"^@?[a-zA-Z_\-=\.\/0-9]+(:[a-zA-Z\-\.:\/0-9]+)?$")


def validate_token(form, token):
    tokens.tokens.load()
    if not tokens.tokens.valid(token.data):
        raise validators.ValidationError('Token is invalid')


def validate_username(form, username):
    domain = urlparse(config.config.server_location).hostname
    re_mxid = r"^@?[a-zA-Z_\-=\.\/0-9]+(:" + \
              re.escape(domain) + \
              r")?$"
    err = "Username doesn't follow pattern: '%s'" % re_mxid
    if not re.search(re_mxid, username.data):
        raise validators.ValidationError(err)


def validate_password(form, password):
    min_length = config.config.password['min_length']
    err = 'Password should be between %s and 255 chars long' % min_length
    if len(password.data) < min_length or len(password.data) > 255:
        raise validators.ValidationError(err)


class RegistrationForm(Form):
    username = StringField('Username', [
        validators.Length(min=1, max=200),
        # validators.Regexp(re_mxid)
        validate_username
    ])
    password = PasswordField('New Password', [
        # validators.Length(min=8),
        validate_password,
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    token = StringField('Token', [
        validators.Regexp(r"^([A-Z][a-z]+)+$"),
        validate_token
    ])


@app.route('/register', methods=['POST'])
def register():
    logger.debug('an account registration started...')
    form = RegistrationForm(request.form)
    logger.debug('validating request data...')
    if form.validate():
        logger.debug('request valid')
        tokens.tokens.use(form.token.data)
        username = form.username.data.rsplit(":")[0].split("@")[-1]
        logger.debug('creating account %s...' % username)
        try:
            account_data = create_account(form.username.data,
                                          form.password.data,
                                          config.config.server_location,
                                          config.config.shared_secret)
        except exceptions.ConnectionError as e:
            logger.error('can not connect to SERVER_LOCATION',
                         exc_info=True)
            abort(500)
        except exceptions.HTTPError as e:
            resp = e.response
            error = resp.json()
            status_code = resp.status_code
            print(status_code)
            if status_code == 404:
                logger.error('no HS found at SERVER_LOCATION')
            elif status_code == 403:
                logger.error('wrong registration secret')
            else:
                logger.error('failure communicating with HS',
                             exc_info=True)
            abort(500)
        logger.debug('account creation succeded!')
        return jsonify(access_token=account_data['access_token'],
                       device_id=account_data['device_id'],
                       home_server=account_data['home_server'],
                       user_id=account_data['user_id'],
                       status_code=200)
    else:
        logger.debug('account creation failed!')
        return make_response(jsonify(form.errors), 400)
        # for fieldName, errorMessages in form.errors.items():
        #     for err in errorMessages:
        #         # return error to user
