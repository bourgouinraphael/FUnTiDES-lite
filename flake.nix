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
          llvmPackages.openmp
          (writeShellScriptBin "clean" ''
            rm build -rf
            rm compile_commands.json
          '')
          (writeShellScriptBin "configure" ''
            mkdir -p build
            cd build
            cmake .. -DENABLE_CUDA=ON -DUSE_KOKKOS=ON -DUSE_VECTOR=OFF -DKokkos_ARCH_ADA89=ON
            cd ..
            ln -s build/compile_commands.json .
          '')
          (writeShellScriptBin "compile" ''
            make -C ./build -j
          '')
        ];
        shellHook = ''
          export LD_LIBRARY_PATH="/run/opengl-driver/lib:$LD_LIBRARY_PATH"
          export CUDA_PATH=${pkgs.cudaPackages.cudatoolkit}

          cat > .clangd <<EOF
          CompileFlags:
            Add:
              - -xcuda
              - --cuda-gpu-arch=sm_89
              - --cuda-path=${pkgs.cudaPackages.cudatoolkit}
              - -Wno-unknown-cuda-version
            Remove:
              - -forward-unknown-to-host-compiler
              - -Xcudafe*
              - -Xcompiler*
              - --expt-*
              - --generate-code*
              - -arch=*
              - -gencode*
              - -extended-lambda
          EOF
        '';
      };
    };
}
