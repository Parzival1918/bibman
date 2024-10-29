{
  description = "Flake for bibman cli app";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        pkgs = nixpkgs.legacyPackages.${system};
        #inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
        poetry2nix = inputs.poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
        inherit (pkgs) lib;
        src = pkgs.fetchFromGitHub {
          owner = "Parzival1918";
          repo = "bibman";
          rev = "v0.3.4";
          sha256 = "";
        };
      in
      {
        packages = {
          bibman = poetry2nix.mkPoetryApplication { 
            projectDir = src;
            python = pkgs.python312;
            meta = {
              description = "Simple CLI tool to manage BibTeX files.";
              longDescription = ''
                bibman is a simple CLI tool to manage BibTeX files.

                It allows to manage bibliography by saving it in .bib files in a library.
                Multiple libraries can be created and managed.
              '';
              license = lib.licenses.mit;
              homepage = "https://github.com/Parzival1918/bibman";
              platforms = lib.platforms.all;
            };
            overrides = poetry2nix.overrides.withDefaults (self: super: {
              pyfzf-iter = super.pyfzf-iter.overridePythonAttrs (old: {
                buildInputs = (old.buildInputs or [ ]) ++ [ super.setuptools ];
              });
              urllib3 = super.urllib3.overridePythonAttrs (old: {
                buildInputs = (old.buildInputs or [ ]) ++ [ super.hatch-vcs ];
              });
              mkdocs-get-deps = super.mkdocs-get-deps.overridePythonAttrs (old: {
                buildInputs = (old.buildInputs or [ ]) ++ [ super.hatchling ];
              });
              bs4 = super.bs4.overridePythonAttrs (old: {
                buildInputs = (old.buildInputs or [ ]) ++ [ super.hatchling ];
              });
            });
          };

          default = self.packages.${system}.bibman;
        };
      }
    );
}
