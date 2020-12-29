#!/bin/sh

docker run \
  -d \
  --user "$(id -u):$(id -g)" \
  --network matrix \
  --publish 5000:5000/tcp \
  --volume $(pwd)/data:/data \
  matrix-registration:latest \
  serve
