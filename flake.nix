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

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
        lib = pkgs.lib;
      in
      {
        packages = {
          myapp = mkPoetryApplication { 
            projectDir = self;
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
          default = self.packages.${system}.myapp;
        };
      });
}