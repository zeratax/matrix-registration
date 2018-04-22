from flask import Flask, abort, jsonify, request

import hashlib
import hmac
import yaml
import requests
import sys

from .synapse_register import create_account 
from .config import Config 
from .tokens import Tokens


app = Flask(__name__)

SHARED_SECRET = Config['SHARED_SECRET']
SERVER_LOCATION = Config['SERVER_LOCATION']


@app.route('/register', methods=['POST'])
def register():
    app.logger.debug('an account registration was requested...')
    if all(req in request.form for req in ('username', 
                                           'password',
                                           'token')):
        username = request.form['username'].rsplit(":")[0].split("@")[-1]
        password = request.form['password']
        token = request.form['token']

        app.logger.debug('checking token')
        if not Tokens.verify(token):
            app.logger.debug('token is expired/incorrect')
            abort(403)
        app.logger.debug('token accepted')

        if username and password:
            app.logger.debug('creating account %s...' % username)
            try:
                account_data = create_account(username,
                                              password,
                                              SERVER_LOCATION,
                                              SHARED_SECRET)
            except requests.exceptions.HTTPError as e:
                app.logger.error('Failure communicating with HS',
                                 exc_info=True)
                abort(400)
            app.logger.debug('account creation succeded!')
            return jsonify(account_data)

    app.logger.debug('account creation failed!')
    abort(400)

