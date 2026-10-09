{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs =
    { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };
    in
    {
      devShells.${system}.default = pkgs.mkShell.override { stdenv = pkgs.gcc14Stdenv; } {
        buildInputs = with pkgs; [
          cmake
          gnumake
          clang-tools
          gdb
          valgrind
          cudaPackages.cudatoolkit
        ];
        shellHook = ''
          export LD_LIBRARY_PATH="/run/opengl-driver/lib:$LD_LIBRARY_PATH"
        '';
      };
    };
}
