## matrix-registration

a simple python application to have a token based matrix registration

if you like me encountered the situation where you want to invite your friends to your homeserver, but neither wanted to open up public registration nor create accounts for every individual user yourself, this project should be the solution.

with this project you can just quickly generate tokens on the fly and share them with your friends to allow them to register to your homeserver.
### Examples

To try the project out you can play around with the [demo page](./demo.html) for an implemented example registration page using the demo api or

perform a [curl](https://github.com/ZerataX/matrix-registration/wiki/api#curl) against the demo api, e.g.:
```bash
curl -H "Authorization: SharedSecret demopagesecret" \
     -H "Content-Type: application/json" \
     -D '{"one_time": true, "ex_date": "24.12.2020"}' \
     https://dmnd.sh/test-token
```

### Support or Contact

Having trouble with the application? Check out the [wiki page](https://github.com/ZerataX/matrix-registration/wiki/) or join [#matrix-registration:dmnd.sh](https://matrix.to/#/#matrix-registration:dmnd.sh) and we’ll help you sort it out.
