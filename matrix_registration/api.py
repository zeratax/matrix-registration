# Standard library imports...
import hashlib
import hmac
import yaml
import requests
import sys

# Third-party imports...
from flask import Flask, abort, jsonify, request
from wtforms import Form, BooleanField, StringField, PasswordField, validators

# Local imports...
from .synapse_register import create_account
from . import config
from . import tokens


app = Flask(__name__)

SHARED_SECRET = config.config.SHARED_SECRET
SERVER_LOCATION = config.config.SERVER_LOCATION


def validate_token(form, token):
    tokens.tokens.load()
    if not tokens.tokens.valid(token.data):
        raise ValidationError('this token is not valid')


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
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
        app.logger.debug('creating account %s...' % form.username.data)
        try:
            account_data = create_account(form.username.data,
                                          form.password.data,
                                          SERVER_LOCATION,
                                          SHARED_SECRET)
        except requests.exceptions.HTTPError as e:
            app.logger.error('Failure communicating with HS',
                             exc_info=True)
            abort(500)
        app.logger.debug('account creation succeded!')
        return jsonify(account_data)
    app.logger.debug('account creation failed!')
    abort(401)
