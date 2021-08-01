{ pkgs ? import <nixpkgs> {}}:
with pkgs.python3Packages;

let
  # officially supported database drivers
  dbDrivers = [
    psycopg2
    # sqlite driver is already shipped with python by default
  ];

in buildPythonPackage {
  name = "matrix-registration";
  src = ./.;
  propagatedBuildInputs = [
    pkgs.libsndfile
    alembic
    appdirs
    flask
    flask-cors
    flask-httpauth
    flask-limiter
    flask_sqlalchemy
    jsonschema
    python-dateutil
    pyyaml
    requests
    waitress
    wtforms
    setuptools
  ]++ dbDrivers;

  checkInputs = [
    flake8
    parameterized
  ];
}
