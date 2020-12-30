#!/bin/sh

docker run \
  -it --rm \
  --user "$(id -u):$(id -g)" \
  --volume $(pwd)/data:/data  \
  matrix-registration:latest  \
  "$@"
