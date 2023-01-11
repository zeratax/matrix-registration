{ pkgs ? import <nixpkgs> { } }:
with pkgs.python3.pkgs;

buildPythonPackage rec {
  name = "matrix-registration";
  src = builtins.path {
    inherit name;
    path = ./.;
  };

  postPatch = ''
    sed -i -e '/alembic>/d' setup.py
  '';

  propagatedBuildInputs = [
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
    psycopg2
  ];

  checkInputs = [ flake8 parameterized ];
}
