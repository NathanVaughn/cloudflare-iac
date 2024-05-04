# CloudFlare Infrastructure As Code

## Get Started

Create a `.env` file based on `.env.example`.

## Import Resources

Follow Pulumi documentation, but usually like

```bash
pulumi import cloudflare:index/pagesDomain:PagesDomain <resource name> <account_id>/<project_name>/<domain-name>
```
