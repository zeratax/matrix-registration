<img src="resources/logo.png" width="300">

[![Build Status](https://travis-ci.org/ZerataX/matrix-registration.svg?branch=master)](https://travis-ci.org/ZerataX/matrix-registration) [![Coverage Status](https://coveralls.io/repos/github/ZerataX/matrix-registration/badge.svg)](https://coveralls.io/github/ZerataX/matrix-registration) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/matrix-registration.svg) [![PyPI](https://img.shields.io/pypi/v/matrix-registration.svg)](https://pypi.org/project/matrix-registration/) [![Matrix](https://img.shields.io/matrix/matrix-registration:dmnd.sh.svg?server_fqdn=matrix.org)](https://matrix.to/#/#matrix-registration:dmnd.sh)

# matrix-registration

a simple python application to have a token based matrix registration

if you like me encountered the situation where you want to invite your friends to your homeserver, but neither wanted to open up public registration nor create accounts for every individual user yourself, this project should be the solution.

with this project you can just quickly generate tokens on the fly and share them with your friends to allow them to register to your homeserver.

<img src="https://matrix.org/_matrix/media/v1/download/dmnd.sh/UKGgpbHRdFXzKywxjjbfHAsI" width="500">


## setup

```bash
pip3 install matrix-registration
python3 -m matrix_registration
```
__INFO:__ 
- This only asks you for the most important options. 
You should definitely take a look at the actual configuration file.
- The `shared_secret` has to be the same as `registration_shared_secret` in your homeserver.yaml

### nginx reverse-proxy

an example nginx setup:
```nginx
location  ~ ^/(static|register) {
        proxy_pass http://localhost:5000;
}
```

If you already have a website and want to use your own register page, the [wiki](https://github.com/ZerataX/matrix-registration/wiki/reverse-proxy#advanced) describes a more advanced nginx setup.


## usage

```bash
$ python -m matrix_registration -h
usage: python -m matrix_registration [-h] {api,gen,status,config} ...

a token based matrix registration app

positional arguments:
  {api,gen,status,config}
                        sub-commands. for ex. 'gen -h' for additional help
    api                 start as api
    gen                 generate new token. -o onetime, -e expire date
    status              view status or disable token. -s status, -d disable,
                        -l list
    config              show config location

optional arguments:
  -h, --help            show this help message and exit

```

after you've started the api server and [generated a token](https://github.com/ZerataX/matrix-registration/wiki/api#creating-a-new-token) you can register an account with a simple post request, e.g.:
```bash
curl -X POST \
     -F 'username=test' \
     -F 'password=verysecure' \
     -F 'confirm=verysecure' \
     -F 'token=DoubleWizardSki' \
     http://localhost:5000/register
```
or by visiting http://localhost:5000/register?token=DoubleWizardSki


## resources

if you want to write your own registration page, you can take a look at the sample in [resources/example.html](resources/example.html)

the html page looks for the query paramater `token` and sets the token input field to it's value. this would allow you to directly share links with the token included, e.g.:
`https://homeserver.tld/register.html?token=DoubleWizardSki`


For more info check the [wiki](https://github.com/ZerataX/matrix-registration/wiki)
