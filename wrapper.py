# Pulumi config file is completely broken, so this is a workaround
# to run the given command with the contents of the `.env` file passed in

import os
import subprocess
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def read_env() -> dict:
    env = {}
    with open(os.path.join(THIS_DIR, ".env")) as f:
        for line in f:
            key, value = line.strip().split("=", 1)
            env[key] = value

    print(", ".join(list(env.keys())) + " loaded from .env")
    return env


def main():  # sourcery skip: dict-assign-update-to-union
    # copy existing environment
    new_env = os.environ.copy()

    # merge with .env file
    env = read_env()
    new_env.update(env)

    # run given command
    cmd = sys.argv[1:]
    print("> " + " ".join(cmd))

    # add poetry run to get python environment
    proc = subprocess.run(["poetry", "run"] + cmd, env=new_env)
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
