# Standard library imports...
import hashlib
import hmac
import yaml
import requests
import re
import sys

# Third-party imports...
from flask import Flask, abort, jsonify, request
from wtforms import Form, BooleanField, StringField, PasswordField, validators

# Local imports...
from .synapse_register import create_account
from . import config
from . import tokens


app = Flask(__name__)

re_mxid = re.compile(r"^@?[a-zA-Z_\-=\.\/0-9]+(:[a-zA-Z\-\.:\/0-9]+)?$")


def validate_token(form, token):
    tokens.tokens.load()
    if not tokens.tokens.valid(token.data):
        raise validators.ValidationError('this token is not valid')


def validate_username(form, username):
    if not re_mxid.match(username.data):
        raise validators.ValidationError('this username is not valid')


class RegistrationForm(Form):
    username = StringField('Username', [
        validators.Length(min=1, max=200),
        validate_username
    ])
    password = PasswordField('New Password', [
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
                                          config.config.SERVER_LOCATION,
                                          config.config.SHARED_SECRET)
        except requests.exceptions.HTTPError as e:
            app.logger.error('Failure communicating with HS',
                             exc_info=True)
            abort(500)
        app.logger.debug('account creation succeded!')
        return jsonify(account_data)
    app.logger.debug('account creation failed!')
    abort(401)
