with import <nixpkgs> {};
with pkgs.python3Packages;

buildPythonPackage rec {
  name = "matrix-registration";
  propagatedBuildInputs = [
    pkgs.libsndfile
    appdirs
    flask
    flask-cors
    flask-httpauth
    flask-limiter
    flask_sqlalchemy
    python-dateutil
    pytest
    pyyaml
    requests
    waitress
    wtforms
    setuptools
  ];
}