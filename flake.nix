{
  description = "jiratui - A TUI for interacting with Atlassian Jira from your terminal";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
      ...
    }:
    let
      inherit (nixpkgs) lib;

      version = (builtins.fromTOML (builtins.readFile ./pyproject.toml)).project.version;

      forAllSystems = lib.genAttrs [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

      overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel";
      };

      # Overrides for packages that need native dependencies when built from source.
      # With sourcePreference = "wheel" these are only needed as sdist fallback,
      # but they ensure the flake works even when no wheel is available for the platform.
      pyprojectOverrides = pkgs: final: prev: {
        pillow = prev.pillow.overrideAttrs (old: {
          nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [
            pkgs.pkg-config
          ];
          buildInputs = (old.buildInputs or [ ]) ++ [
            pkgs.zlib
            pkgs.libjpeg
            pkgs.libpng
            pkgs.libtiff
            pkgs.freetype
            pkgs.lcms2
            pkgs.libwebp
            pkgs.openjpeg
          ];
        });

        aiohttp = prev.aiohttp.overrideAttrs (old: {
          nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [
            final.cython
          ];
        });
      };

      mkPkgs =
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          python = pkgs.python313;

          pythonSet =
            (pkgs.callPackage pyproject-nix.build.packages {
              inherit python;
            }).overrideScope
              (
                lib.composeManyExtensions [
                  pyproject-build-systems.overlays.default
                  overlay
                  (pyprojectOverrides pkgs)
                ]
              );

          venv = pythonSet.mkVirtualEnv "jiratui-env" workspace.deps.default;

          # python-magic loads libmagic at runtime via ctypes.
          # On Linux ctypes uses LD_LIBRARY_PATH, on macOS DYLD_LIBRARY_PATH.
          libPathVar = if pkgs.stdenv.isDarwin then "DYLD_LIBRARY_PATH" else "LD_LIBRARY_PATH";

          wrapped =
            pkgs.runCommand "jiratui-${version}"
              {
                nativeBuildInputs = [ pkgs.makeWrapper ];
                meta = {
                  description = "A TUI for interacting with Atlassian Jira from your terminal";
                  homepage = "https://jiratui.sh";
                  license = lib.licenses.mit;
                  mainProgram = "jiratui";
                };
              }
              ''
                mkdir -p $out/bin
                makeWrapper ${venv}/bin/jiratui $out/bin/jiratui \
                  --prefix PATH : ${lib.makeBinPath [ pkgs.git ]} \
                  --prefix ${libPathVar} : ${pkgs.file}/lib
              '';
        in
        {
          inherit pkgs venv wrapped;
        };
    in
    {
      packages = forAllSystems (system: {
        jiratui = (mkPkgs system).wrapped;
        default = self.packages.${system}.jiratui;
      });

      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          libmagicPath = lib.makeLibraryPath [ pkgs.file ];
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.uv
              pkgs.python313
              pkgs.git
              pkgs.file
            ];
            # python-magic loads libmagic via ctypes at runtime
            env =
              lib.optionalAttrs pkgs.stdenv.isLinux {
                LD_LIBRARY_PATH = libmagicPath;
              }
              // lib.optionalAttrs pkgs.stdenv.isDarwin {
                DYLD_LIBRARY_PATH = libmagicPath;
              };
            shellHook = ''
              unset PYTHONPATH
              export UV_PYTHON_DOWNLOADS=never
            '';
          };
        }
      );

      overlays.default = final: prev: {
        jiratui = self.packages.${prev.stdenv.hostPlatform.system}.jiratui;
      };
    };
}
