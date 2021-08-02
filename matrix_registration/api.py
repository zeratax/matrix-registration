# Standard library imports...
import logging
from requests import exceptions
import re
from urllib.parse import urlparse
import os

# Third-party imports...
from datetime import datetime
from flask import (
    Blueprint,
    abort,
    jsonify,
    request,
    make_response,
    render_template,
    send_file,
)
from flask_httpauth import HTTPTokenAuth
from werkzeug.exceptions import BadRequest
from wtforms import Form, StringField, PasswordField, validators

# Local imports...
from .matrix_api import create_account
from . import config
from . import tokens
from .constants import __location__
from .translation import get_translations


auth = HTTPTokenAuth(scheme="SharedSecret")
logger = logging.getLogger(__name__)

api = Blueprint("api", __name__)


def validate_token(form, token):
    """
    validates token

    Parameters
    ----------
    arg1 : Form object
    arg2 : str
        token name, e.g. 'DoubleWizardSki'

    Raises
    -------
    ValidationError
        Token is invalid

    """
    tokens.tokens.load()
    if not tokens.tokens.active(token.data):
        raise validators.ValidationError("Token is invalid")


def validate_username(form, username):
    """
    validates username

    Parameters
    ----------
    arg1 : Form object
    arg2 : str
        username name, e.g: '@user:matrix.org' or 'user'
        https://github.com/matrix-org/matrix-doc/blob/master/specification/appendices/identifier_grammar.rst#user-identifiers
    Raises
    -------
    ValidationError
        Username doesn't follow mxid requirements
    """
    re_mxid = f"^(?P<at>@)?(?P<username>[a-zA-Z_\-=\.\/0-9]+)(?P<server_name>:{ re.escape(config.config.server_name) })?$"
    match = re.search(re_mxid, username.data)
    if not match:
        raise validators.ValidationError(
            f"Username doesn't follow mxid pattern: /{re_mxid}/"
        )
    username = match.group("username")
    for e in [
        validators.ValidationError(f"Username does not follow custom pattern /{x}/")
        for x in config.config.username["validation_regex"]
        if not re.search(x, username)
    ]:
        raise e
    for e in [
        validators.ValidationError(f"Username must not follow custom pattern /{x}/")
        for x in config.config.username["invalidation_regex"]
        if re.search(x, username)
    ]:
        raise e


def validate_password(form, password):
    """
    validates username

    Parameters
    ----------
    arg1 : Form object
    arg2 : str
        password
    Raises
    -------
    ValidationError
        Password doesn't follow length requirements
    """
    min_length = config.config.password["min_length"]
    err = "Password should be between %s and 255 chars long" % min_length
    if len(password.data) < min_length or len(password.data) > 255:
        raise validators.ValidationError(err)


class RegistrationForm(Form):
    """
    Registration Form

    validates user account registration requests
    """

    username = StringField(
        "Username",
        [
            validators.Length(min=1, max=200),
            # validators.Regexp(re_mxid)
            validate_username,
        ],
    )
    password = PasswordField(
        "New Password",
        [
            # validators.Length(min=8),
            validate_password,
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Repeat Password")
    token = StringField(
        "Token", [validators.Regexp(r"^([A-Z][a-z]+)+$"), validate_token]
    )


@auth.verify_token
def verify_token(token):
    return (
        token != "APIAdminPassword" and token == config.config.admin_api_shared_secret
    )


@auth.error_handler
def unauthorized():
    resp = {"errcode": "MR_BAD_SECRET", "error": "wrong shared secret"}
    return make_response(jsonify(resp), 401)


@api.route("/static/replace/images/element-logo.png")
def element_logo():
    return send_file(
        config.config.client_logo.replace("{cwd}", f"{os.getcwd()}/"),
        mimetype="image/jpeg",
    )


@api.route("/register", methods=["GET", "POST"])
def register():
    """
    main user account registration endpoint
    to register an account you need to send a
    application/x-www-form-urlencoded request with
      - username
      - password
      - confirm
      - token
    as described in the RegistrationForm
    """
    if request.method == "POST":
        logger.debug("an account registration started...")
        form = RegistrationForm(request.form)
        logger.debug("validating request data...")
        if form.validate():
            logger.debug("request valid")
            # remove sigil and the domain from the username
            username = form.username.data.rsplit(":")[0].split("@")[-1]
            logger.debug("creating account %s..." % username)
            # send account creation request to the hs
            try:
                account_data = create_account(
                    form.username.data,
                    form.password.data,
                    config.config.server_location,
                    config.config.registration_shared_secret,
                )
            except exceptions.ConnectionError:
                logger.error(
                    "can not connect to %s" % config.config.server_location,
                    exc_info=True,
                )
                abort(500)
            except exceptions.HTTPError as e:
                resp = e.response
                error = resp.json()
                status_code = resp.status_code
                if status_code == 404:
                    logger.error("no HS found at %s" % config.config.server_location)
                elif status_code == 403:
                    logger.error("wrong shared registration secret or not enabled")
                elif status_code == 400:
                    # most likely this should only be triggered if a userid
                    # is already in use
                    return make_response(jsonify(error), 400)
                else:
                    logger.error("failure communicating with HS", exc_info=True)
                abort(500)

            logger.debug("using token %s" % form.token.data)
            ip = request.remote_addr if config.config.ip_logging else False
            tokens.tokens.use(form.token.data, ip)

            logger.debug("account creation succeded!")
            return jsonify(
                access_token=account_data["access_token"],
                home_server=account_data["home_server"],
                user_id=account_data["user_id"],
                status="success",
                status_code=200,
            )
        else:
            logger.debug("account creation failed!")
            resp = {"errcode": "MR_BAD_USER_REQUEST", "error": form.errors}
            return make_response(jsonify(resp), 400)
            # for fieldName, errorMessages in form.errors.items():
            #     for err in errorMessages:
            #         # return error to user
    else:
        server_name = config.config.server_name
        pw_length = config.config.password["min_length"]
        uname_regex = config.config.username["validation_regex"]
        uname_regex_inv = config.config.username["invalidation_regex"]
        lang = request.args.get("lang") or request.accept_languages.best
        replacements = {"server_name": server_name, "pw_length": pw_length}
        translations = get_translations(lang, replacements)
        return render_template(
            "register.html",
            server_name=server_name,
            pw_length=pw_length,
            uname_regex=uname_regex,
            uname_regex_inv=uname_regex_inv,
            client_redirect=config.config.client_redirect,
            base_url=config.config.base_url,
            translations=translations,
        )


@api.route("/health")
def health():
    return make_response("OK", 200)


@api.route("/api/version")
@auth.login_required
def version():
    with open(os.path.join(__location__, "__init__.py"), "r") as file:
        version_file = file.read()
        version_match = re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
        )
        resp = {"version": version_match.group(1)}
        return make_response(jsonify(resp), 200)


@api.route("/api/token", methods=["GET", "POST"])
@auth.login_required
def token():
    tokens.tokens.load()

    data = False
    max_usage = False
    expiration_date = None
    if request.method == "GET":
        return jsonify(tokens.tokens.toList())
    elif request.method == "POST":
        data = request.get_json()
        try:
            if data:
                if "expiration_date" in data and data["expiration_date"] is not None:
                    expiration_date = datetime.fromisoformat(data["expiration_date"])
                if "max_usage" in data:
                    max_usage = data["max_usage"]
                token = tokens.tokens.new(
                    expiration_date=expiration_date, max_usage=max_usage
                )
        except ValueError:
            resp = {
                "errcode": "MR_BAD_DATE_FORMAT",
                "error": "date wasn't in YYYY-MM-DD format",
            }
            return make_response(jsonify(resp), 400)
        return jsonify(token.toDict())
    resp = {"errcode": "MR_BAD_USER_REQUEST", "error": "malformed request"}
    return make_response(jsonify(resp), 400)


@api.route("/api/token/<token>", methods=["GET", "PATCH"])
@auth.login_required
def token_status(token):
    tokens.tokens.load()
    data = False
    if request.method == "GET":
        if tokens.tokens.get_token(token):
            return jsonify(tokens.tokens.get_token(token).toDict())
        else:
            resp = {"errcode": "MR_TOKEN_NOT_FOUND", "error": "token does not exist"}
            return make_response(jsonify(resp), 404)
    elif request.method == "PATCH":
        try:
            data = request.get_json(force=True)
        except BadRequest as e:
            # empty request means use default values
            if len(request.get_data()) == 0:
                data = None
            else:
                raise e
        if data:
            if "ips" not in data and "active" not in data and "name" not in data:
                if tokens.tokens.update(token, data):
                    return jsonify(tokens.tokens.get_token(token).toDict())
            else:
                resp = {
                    "errcode": "MR_BAD_USER_REQUEST",
                    "error": "you're not allowed to change this property",
                }
                return make_response(jsonify(resp), 400)
            resp = {"errcode": "MR_TOKEN_NOT_FOUND", "error": "token does not exist"}
            return make_response(jsonify(resp), 404)
    resp = {"errcode": "MR_BAD_USER_REQUEST", "error": "malformed request"}
    return make_response(jsonify(resp), 400)
