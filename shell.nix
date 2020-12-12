with import <nixpkgs> {};
with pkgs.python3Packages;

buildPythonPackage rec {
  name = "matrix-registration";
  # src = ./.;
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
  checkInputs = [
    flake8
    parameterized
  ];
  # shellHook = ''
  #   unset SOURCE_DATE_EPOCH
  # '';
}
