# Standard library imports...
import hashlib
import hmac
import requests

import logging

logger = logging.getLogger(__name__)


def create_account(user, password, server_location, shared_secret,
                   admin=False):
    """
    creates account
    https://github.com/matrix-org/synapse/blob/master/synapse/_scripts/register_new_matrix_user.py

    Parameters
    ----------
    arg1 : str
        local part of the new user
    arg2 : str
        password
    arg3 : str
        url to homeserver
    arg4 : str
        Registration Shared Secret as set in the homeserver.yaml
    arg5 : bool
        register new user as an admin.
    Raises
    -------
    requests.exceptions.ConnectionError:
        can't connect to homeserver
    requests.exceptions.HTTPError:
        something with the communciation to the homeserver failed
    """
    nonce = _get_nonce(server_location)

    mac = hmac.new(
        key=str.encode(shared_secret),
        digestmod=hashlib.sha1,
    )

    mac.update(nonce.encode())
    mac.update(b'\x00')
    mac.update(user.encode())
    mac.update(b'\x00')
    mac.update(password.encode())
    mac.update(b'\x00')
    mac.update(b'admin' if admin else b'notadmin')

    mac = mac.hexdigest()

    data = {
        'nonce': nonce,
        'username': user,
        'password': password,
        'admin': admin,
        'mac': mac,
    }

    server_location = server_location.rstrip('/')

    r = requests.post('%s/_synapse/admin/v1/register' % (server_location),
                      json=data)
    r.raise_for_status()
    return r.json()


def _get_nonce(server_location):
    r = requests.get('%s/_synapse/admin/v1/register' % (server_location))
    r.raise_for_status()
    return r.json()['nonce']
