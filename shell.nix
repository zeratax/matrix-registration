{ pkgs ? import <nixpkgs> { } }:

(let matrix-registration = pkgs.callPackage ./default.nix { inherit pkgs; };
in pkgs.python3.withPackages
(ps: [ matrix-registration pkgs.black ps.alembic ps.parameterized ps.flake8 ])).env
