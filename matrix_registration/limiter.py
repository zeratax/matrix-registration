from flask import request
from flask_limiter import Limiter

from . import config


def get_real_user_ip() -> str:
    """ratelimit the users original ip instead of (optional) reverse proxy"""
    return next(iter(request.headers.getlist("X-Forwarded-For")), request.remote_addr)


def get_default_rate_limit() -> str:
    """return limit_string"""
    return "; ".join(config.config.rate_limit)


limiter = Limiter(key_func=get_real_user_ip)
