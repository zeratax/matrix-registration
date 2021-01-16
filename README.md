<img src="resources/logo.png" width="300">

[![Build Status](https://travis-ci.org/ZerataX/matrix-registration.svg?branch=master)](https://travis-ci.org/ZerataX/matrix-registration) [![Coverage Status](https://coveralls.io/repos/github/ZerataX/matrix-registration/badge.svg)](https://coveralls.io/github/ZerataX/matrix-registration) [![Translation status](https://l10n.dmnd.sh/widgets/matrix-registration/-/svg-badge.svg)](http://l10n.dmnd.sh/engage/matrix-registration/) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/matrix-registration.svg) [![PyPI](https://img.shields.io/pypi/v/matrix-registration.svg)](https://pypi.org/project/matrix-registration/) [![Matrix](https://img.shields.io/matrix/matrix-registration:dmnd.sh.svg?server_fqdn=matrix.org)](https://matrix.to/#/#matrix-registration:dmnd.sh)

# matrix-registration

A simple Python application enabling token-based registration for matrix servers.

You may have, like me, encountered the situation where you want to invite your friends to create an account on your homeserver, but neither want to open up public registration nor create accounts for every individual user yourself. This project aims to solve this problem.

With matrix-registration, you can quickly generate tokens on the fly and share them with your friends to allow them to register on your homeserver.

<img src="https://matrix.org/_matrix/media/v1/download/dmnd.sh/UKGgpbHRdFXzKywxjjbfHAsI" width="500">


## Setup
Install using pip:

```bash
pip3 install matrix-registration
matrix-registration
```

### First start
To start, execute `matrix-registration`.

A configuration file should be generated for you on first start.

If this fails, you can create a configuration for your matrix homeserver by copying [config.sample.yaml](/config.sample.yaml) to your server and editing it:
```bash
wget https://raw.githubusercontent.com/ZerataX/matrix-registration/master/config.sample.yaml
cp config.sample.yaml config.yaml
nano config.yaml
```

Then pass the path to this configuration to the application on startup using `--config-path /path/to/config.yaml`.

__INFO:__ 
- This only asks you for the most important options. 
You should definitely take a look at the actual configuration file. The path to the file will be printed by `matrix-registration` the first time it runs.
- The `shared_secret` has to be the same as `registration_shared_secret` in your homeserver.yaml



## Usage

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

After you've started the API server and [generated a token](https://github.com/ZerataX/matrix-registration/wiki/api#creating-a-new-token) you can register an account either:
- with a simple post request, e.g.:
```bash
curl -X POST \
     -F 'username=test' \
     -F 'password=verysecure' \
     -F 'confirm=verysecure' \
     -F 'token=DoubleWizardSki' \
     http://localhost:5000/register
```
- or by visiting http://localhost:5000/register?token=DoubleWizardSki


## Further Resources

### Nginx reverse-proxy

If you'd like to run matrix-registration behind a reverse-proxy, here is an example nginx setup:

```nginx
location  ~ ^/(static|register) {
        proxy_pass http://localhost:5000;
}
```


### Custom registration page

If you want to write your own registration page, you can take a look at the sample in [resources/example.html](resources/example.html)

The html page looks for the query paramater `token` and sets the token input field to it's value. this would allow you to directly share links with the token included, e.g.:

`https://homeserver.tld/register.html?token=DoubleWizardSki`

If you already have a website and want to use your own register page, the [wiki](https://github.com/ZerataX/matrix-registration/wiki/reverse-proxy#advanced) describes a more advanced nginx setup.



### Troubleshooting

#### SQLAlchemy complains that a value isn't in a DateTime value

Before #17 introduced SQLAlchemy support the sqlite database incorrectly stored the expire dates, to fix this you have to manually run:
```sql
update tokens set ex_date=null where ex_date='None';
```
on your database once, or just delete your current database.

### Similar projects

  - [matrix-invite](https://gitlab.com/reivilibre/matrix-invite) live at https://librepush.net/matrix/registration/
  - [matrix-register-bot](https://github.com/krombel/matrix-register-bot) using a bot to review accounts before sending out invite links
  - [MatrixRegistration](https://gitlab.com/olze/matrixregistration/) similar java project using my webui

For more info check the [wiki](https://github.com/ZerataX/matrix-registration/wiki)

### Artwork attribution

- The valley cover photo on the registration page is photo by [Jesús Roncero](https://www.flickr.com/golan)
used under the terms of [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). No warranties are given.
- The font used on the registration page is [Nunito](https://fonts.google.com/specimen/Nunito) which is licensed under [SIL Open Font License, Version 1.1](./matrix_registration/static/fonts/NUNITO-LICENSE).
