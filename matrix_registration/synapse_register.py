import hashlib
import hmac
import requests

def create_account(user, password, server_location, shared_secret, admin=False):
    mac = hmac.new(
        key=str.encode(shared_secret),
        digestmod=hashlib.sha1,
    )

    mac.update(user.encode())
    mac.update(b'\x00')
    mac.update(password.encode())
    mac.update(b'\x00')
    mac.update(b'admin' if admin else b'notadmin')

    mac = mac.hexdigest()

    data = {
        'user': user,
        'password': password,
        'mac': mac,
        'type': 'org.matrix.login.shared_secret',
        'admin': admin,
    }

    server_location = server_location.rstrip('/')

    r = requests.post('%s/_matrix/client/api/v1/register' % (server_location,),
                      json=data)
    r.raise_for_status()
    return r.json()
