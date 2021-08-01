{ pkgs ? import <nixpkgs> {}, tag ? "latest" }:

let
  matrix-registration = import ./shell.nix { inherit pkgs; };

in pkgs.dockerTools.buildImage {
  name = "matrix-registration";
  tag = tag;
  created = "now";

  contents = [ matrix-registration ];

  config = { 
    Entrypoint = [
      "${matrix-registration}/bin/matrix-registration"
      "--config-path=/data/config.yaml"
      ];
    WorkingDir = "/data";
    Volumes = {
      "/data" = {};
    };
    ExposedPorts = {
      "5000/tcp" = {};
    };
    HealthCheck = {
      Interval    = 3000000000;
      Timeout     = 1000000000;
      StartPeriod = 3000000000;
      Test = [
        "CMD"
        "${pkgs.curl}/bin/curl"
        "-fSs"
        "http://localhost:5000/health"
      ];
    };
  };
}
