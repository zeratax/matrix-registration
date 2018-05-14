[![Build Status](https://travis-ci.org/ZerataX/matrix-registration.svg?branch=master)](https://travis-ci.org/ZerataX/matrix-registration) [![Coverage Status](https://coveralls.io/repos/github/ZerataX/matrix-registration/badge.svg)](https://coveralls.io/github/ZerataX/matrix-registration)
# matrix-registration

a simple python application to have a token based matrix registration

## setup
```
  virtualenv -p /usr/bin/python3.6 .
  source ./bin/activate
  pip install -r requirements.txt
```

## usage
```
usage: python -m matrix_registration [-h] [-c <path>] [-o ONE_TIME]
                                     [-e EXPIRE] [-d DISABLE]
                                     {api,token}

a token based Matrix-registration api

positional arguments:
  {api,token}           start as api server or generate new token

optional arguments:
  -h, --help            show this help message and exit
  -c <path>, --config <path>
                        the path to your config file
  -o ONE_TIME, --one-time ONE_TIME
                        one time use token
  -e EXPIRE, --expire EXPIRE
                        expiration date for token
  -d DISABLE, --disable DISABLE
                        disable token
```

if you've started the api server and generated a token you can register an account with curl, e.g.:
```bash
curl -X POST \
     -F 'username=test' \
     -F 'password=verysecure' \
     -F 'confirm=verysecure' \
     -F "token=CarmenHopeMaster" \
     http://localhost:5000/register
```
or a simple html form, see the sample [resources/example.html](resources/example.html)

## contribute

if you want to contribute please install the pre-commit script, execute the following scripts in the root of the repository
```
  ln -s ../../scripts/pre-commit.sh .git/hooks/pre-commit
  chmod +x scripts/pre-commit.sh
```

now everytime you commit the project will be linted and tested.
