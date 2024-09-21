# Cloudflare Infrastructure As Code

## Get Started

Use the provided [devcontainer](https://containers.dev/)
or run the following for local development:

```bash
# Install uv
# https://docs.astral.sh/uv/getting-started/installation/
uv tool install vscode-task-runner
vtr install
```

Create a `.env` file based on `.env.example`.

## Previewing a Deployment

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

Use the [Cloudflare API](https://developers.cloudflare.com/api/) to find
resource IDs.
