{ pkgs, lib, config, inputs, ... }:
{
    # O SQLite fica isolado apenas para este projeto
    packages = [
        pkgs.pyright
        pkgs.sqlite
        pkgs.pkg-config

        # Rust: adaptador de debug (fornece o binário "codelldb")
        pkgs.lldb
        pkgs.vscode-extensions.vadimcn.vscode-lldb.adapter
    ];

    languages.python = {
        enable = true;
        package = pkgs.python313.withPackages (p: with p; [
            # Basic python
            pip
            python-dotenv
            requests

            # Project Libs
            numpy
            pandas
            pytest
            questionary
            typer

            # JPNotebook
            ipykernel
            ipython
            nbformat
            pyqt5

            # NVIM
            jedi
            jedi-language-server
            black
            flake8
            sentinel
            python-lsp-server
            virtualenv
            pyflakes
            isort
            debugpy
            nltk
        ]);

        venv.enable = true;
        venv.requirements = ''
            apyori==1.1.2
            tensorflow
        '';
    };

    languages.rust = {
        enable = true;
        components = [
            "rustc"
            "cargo"
            "clippy"
            "rustfmt"
            "rust-analyzer"
        ];
    };

    enterShell = ''
      echo "$(python --version) — venv ativo"
      echo "$(rustc --version) — toolchain rust ativa"
    '';
}
