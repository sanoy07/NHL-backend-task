{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "quiz-wallet-backend-env";

  buildInputs = [
    pkgs.python3                    # use the default Python 3 interpreter
    pkgs.python3Packages.pip        # pip for that interpreter
    pkgs.postgresql_14              # psql client, if needed
    pkgs.git
    pkgs.nodejs
                       # optional, front-end work
  ];

  nativeBuildInputs = [
    pkgs.python3Packages.virtualenv # virtualenv to isolate dependencies
  ];

  shellHook = ''
    # Create and activate .venv if missing
    if [ ! -d .venv ]; then
      virtualenv --python=$(which python) .venv
    fi
    source .venv/bin/activate

    # Sync dependencies
    pip install --upgrade pip
    if [ -f requirements.txt ]; then
      pip install -r requirements.txt
    fi
  '';
}

