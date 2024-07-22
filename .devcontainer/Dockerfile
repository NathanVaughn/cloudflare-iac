FROM ghcr.io/nathanvaughn/devcontainers/python:latest

COPY poetry.lock poetry.lock
RUN pulumi_version=$(python -c "import tomllib; fp = open('poetry.lock', 'rb'); data = tomllib.load(fp); fp.close(); print(next(p['version'] for p in data['package'] if p['name'] == 'pulumi'))") \
 && echo "Installing pulumi version $pulumi_version" \
 && curl -fsSL https://get.pulumi.com | sh -s -- --version $pulumi_version \
 && rm poetry.lock