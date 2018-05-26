[![Build Status](https://travis-ci.org/ZerataX/matrix-registration.svg?branch=master)](https://travis-ci.org/ZerataX/matrix-registration) [![Coverage Status](https://coveralls.io/repos/github/ZerataX/matrix-registration/badge.svg)](https://coveralls.io/github/ZerataX/matrix-registration)
# matrix-registration

a simple python application to have a token based matrix registration

if you like me encountered the situation where you wanted to invite your friends to your homeserver, but neither wanted to open up public registration nor create accounts for every individual user this project should be your solution.

wwith this project you can just quickly generate tokens and share tthem with your friends to allow them to register to your hs.

## setup
```
  virtualenv -p /usr/bin/python3.6 .
  source ./bin/activate
  pip install -r requirements.txt
```

## usage
```
usage: python -m matrix_registration [-h] [-c <path>] [-o]
                                     [-e EXPIRATION_DATE] [-d DISABLE]
                                     [-i INFO] [-l]
                                     {api,token}

a token based matrix registration app

positional arguments:
  {api,token}           start as api server or generate new token

optional arguments:
  -h, --help            show this help message and exit
  -c <path>, --config <path>
                        the path to your config file
  -o, --one-time        one time use token
  -e EXPIRATION_DATE, --expiration-date EXPIRATION_DATE
                        expiration date for token
  -d DISABLE, --disable DISABLE
                        disable token
  -i INFO, --info INFO  get information of token
  -l, --list            list tokens
```

if you've started the api server and generated a token you can register an account with curl, e.g.:
```bash
curl -X POST \
     -F 'username=test' \
     -F 'password=verysecure' \
     -F 'confirm=verysecure' \
     -F "token=DoubleWizardSki" \
     http://localhost:5000/register
```
or a simple html form, see the sample [resources/example.html](resources/example.html)

the html page looks for the query paramater `token` and sets the token input field to it's value. this would allow you to directly share links with the token included, e.g.:
`http://localhost:5000/register?token=DoubleWizardSki`

easying the registration even further

### nginx reverse-proxy
an example nginx setup to expose the html form and the api endpoint on the same URL, based on whether a POST or GET request was made.
```
location /register {
    alias resources/example.html;

    limit_except POST {
        proxy_pass http://localhost:5000;
    }
}
```
