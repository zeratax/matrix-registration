## matrix-registration

A simple python application to have a token based matrix registration

If you like me encountered the situation where you want to invite your friends to your homeserver, but neither wanted to open up public registration nor create accounts for every individual user yourself, this project should be the solution.

With this project you can just quickly generate tokens on the fly and share them with your friends to allow them to register to your homeserver.
### Example Usage
  - Create a new one time usable token directly with python:
```console
$ python -m matrix_registration gen -o
JargonGingerYankee
```
  - or make use of the api:
```console
$ curl -X POST \
       -H "Authorization: SharedSecret demopagesecret" \
       -H "Content-Type: application/json" \
       -d '{"one_time": true}' \
       https://dmnd.sh/test-token
name: 'JargonGingerYankee', used: '0', one_time: 'True', expiration_date: 'None', valid: 'True'%
```
  - now  you can share an invite link to your registration page, with your friends:
[https://zeratax.github.io/matrix-registration/demo.html?token=JargonGingerYankee](https://zeratax.github.io/matrix-registration/demo.html?token=JargonGingerYankee)


### Demo

To try the project out you can play around with the [demo page](./demo.html) for an implemented example registration page using the demo api or

perform a [cURL](https://github.com/ZerataX/matrix-registration/wiki/api#curl) against the demo api, e.g.:
```console
$ curl -H "Authorization: SharedSecret demopagesecret" \
       -H "Content-Type: application/json" \
       -D '{"one_time": true, "ex_date": "24.12.2020"}' \
       https://dmnd.sh/test-token
```

### Support or Contact

Having trouble with the application? Check out the [wiki page](https://github.com/ZerataX/matrix-registration/wiki/) or join [#matrix-registration:dmnd.sh](https://matrix.to/#/#matrix-registration:dmnd.sh) and we’ll help you sort it out.
