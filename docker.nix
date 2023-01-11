{ pkgs ? import <nixpkgs> { }, tag ? "latest" }:

let
  matrix-registration-config = "/data/config.yaml";

  python3 = let
    packageOverrides = self: super: rec {
      alembic = super.alembic.overridePythonAttrs (old: {
        makeWrapperArgs = [
          "--chdir '${matrix-registration}'"
          ''--add-flags "-x config='${matrix-registration-config}'"''
        ];
      });
      matrix-registration =
        (import ./default.nix { inherit pkgs; }).overridePythonAttrs (old: {
          makeWrapperArgs =
            [ ''--add-flags "--config-path='${matrix-registration-config}'"'' ];
        });
    };
  in pkgs.python3.override {
    inherit packageOverrides;
    # enableOptimizations = true;
    # reproducibleBuild = false;
    self = python3;
  };

  python-packages = ps: with ps; [ matrix-registration alembic ];

in pkgs.dockerTools.buildImage {
  name = "matrix-registration";
  tag = tag;
  created = "now";

  copyToRoot = python3.withPackages python-packages;

  config = {
    CMD = [ "matrix-registration" "serve"];
    WorkingDir = "/data";
    Volumes = { "/data" = { }; };
    ExposedPorts = { "5000/tcp" = { }; };
    HealthCheck = {
      Interval = 3000000000;
      Timeout = 1000000000;
      StartPeriod = 3000000000;
      Test =
        [ "CMD" "${pkgs.curl}/bin/curl" "-fSs" "http://localhost:5000/health" ];
    };
  };
}
