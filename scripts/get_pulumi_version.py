import tomllib
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

with open(ROOT_DIR.joinpath("uv.lock"), "rb") as fp:
    data = tomllib.load(fp)
print(next(p["version"] for p in data["package"] if p["name"] == "pulumi"))
