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
matrix-registration
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
$ matrix-registration -h
Usage: matrix-registration [OPTIONS] COMMAND [ARGS]...

  a token based matrix registration app

Options:
  --config-path TEXT  specifies the config file to be used
  --version           Show the flask version
  -h, --help          Show this message and exit.

Commands:
  generate  generate new token
  serve     start api server
  status    view status or disable

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

### troubleshooting

#### SQLAlchemy complains that a value isn't in a DateTime value

Before #17 introduced SQLAlchemy support the sqlite database incorrectly stored the expire dates, to fix this you have to manually run:
```sql
update tokens set ex_date=null where ex_date='None';
```
on your database once, or just delete your current database.

### similar projects

  - [matrix-invite](https://gitlab.com/reivilibre/matrix-invite) live at https://librepush.net/matrix/registration/
  - [matrix-register-bot](https://github.com/krombel/matrix-register-bot) using a bot to review accounts before sending out invite links
  - [MatrixRegistration](https://gitlab.com/olze/matrixregistration/) similar java project using my webui

For more info check the [wiki](https://github.com/ZerataX/matrix-registration/wiki)
