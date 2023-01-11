{ pkgs ? import <nixpkgs> { } }:

(let matrix-registration = pkgs.callPackage ./default.nix { inherit pkgs; };
in pkgs.python3.withPackages
(ps: [ matrix-registration ps.alembic ps.black ])).env
