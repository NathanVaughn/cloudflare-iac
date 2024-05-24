# CloudFlare Infrastructure As Code

## Get Started

Use the provided [devcontainer](https://containers.dev/)
or run the following for local development:

```bash
python -m pip install pipx --upgrade
pipx ensurepath
pipx install poetry
pipx install vscode-task-runner
# (Optionally) Add pre-commit plugin
poetry self add poetry-pre-commit-plugin
```

Create a `.env` file based on `.env.example`.

## Prevewing a Deployment

```bash
vtr preview
```

## Updating a Deployment

```bash
vtr update
```

## Import Resources

Follow Pulumi documentation, but usually like

```bash
python wrapper.py pulumi import cloudflare:index/<resource type> <resource name> <account_id>/<project_name>/<domain-name>
```

Alternatively, this can be done in [bulk](https://www.pulumi.com/learn/importing/bulk-importing/).

Use the [Cloudflare API](https://developers.cloudflare.com/api/) to find resource IDs.
