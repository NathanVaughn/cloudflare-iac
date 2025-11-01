import http
from typing import NamedTuple

import pulumi_cloudflare as cloudflare

from iac import utils
from iac.config import CLOUDFLARE_ACCOUNT_ID
from iac.constants import AUTO_TTL, ZONE_TYPE

ZONE_NAME = "nathanv.me"
BRN = utils.zone_to_name(ZONE_NAME)


class PagesConfig(NamedTuple):
    subdomain: str
    name: str


pages_configs = [
    PagesConfig("", "homepage"),
    PagesConfig("blog", "blog"),
    PagesConfig("links", "links"),
    PagesConfig("pay", "pay"),
    PagesConfig("go", "go"),
]

# https://github.com/pulumi/pulumi-cloudflare/issues/1306
zone = cloudflare.Zone(
    f"{BRN}-zone", name=ZONE_NAME, account={"id": CLOUDFLARE_ACCOUNT_ID}, type=ZONE_TYPE
)

# https://github.com/pulumi/pulumi-cloudflare/issues/1232
cloudflare.ZoneDnssec(f"{BRN}-dnssec", zone_id=zone.id)


# cloudflare pages
for pc in pages_configs:
    domain = ZONE_NAME

    # build the domain name of the page
    if pc.subdomain:
        domain = f"{pc.subdomain}.{ZONE_NAME}"

    project_name = utils.zone_to_name(domain)

    # create the pages domains and DNS records

    # root
    cloudflare.PagesDomain(
        f"{BRN}-pages-domain-{pc.name}",
        account_id=CLOUDFLARE_ACCOUNT_ID,
        name=domain,
        project_name=project_name,
    )

    cloudflare.DnsRecord(
        f"{BRN}-record-{pc.name}",
        name=domain,
        type="CNAME",
        content=f"{project_name}.pages.dev",
        proxied=True,
        ttl=AUTO_TTL,
        zone_id=zone.id,
    )

    # www
    cloudflare.PagesDomain(
        f"{BRN}-pages-domain-www-{pc.name}",
        account_id=CLOUDFLARE_ACCOUNT_ID,
        name=f"www.{domain}",
        project_name=project_name,
    )

    cloudflare.DnsRecord(
        f"{BRN}-record-{pc.name}-www",
        name=f"www.{domain}",
        type="CNAME",
        content=f"{project_name}.pages.dev",
        proxied=True,
        ttl=AUTO_TTL,
        zone_id=zone.id,
    )

    # create the project

    # url shortener doesn't need a build command
    cmd = "npm run build"
    if pc.name == "go":
        cmd = ""

    branch = "main"
    cloudflare.PagesProject(
        f"{BRN}-pages-project-{pc.name}",
        account_id=CLOUDFLARE_ACCOUNT_ID,
        name=project_name,
        build_config=cloudflare.PagesProjectBuildConfigArgs(
            build_caching=True, build_command=cmd, destination_dir="public"
        ),
        production_branch=branch,
        source=cloudflare.PagesProjectSourceArgs(
            type="github",
            config=cloudflare.PagesProjectSourceConfigArgs(
                owner="NathanVaughn",
                repo_name=domain,
                production_branch=branch,
                pr_comments_enabled=True,
                preview_deployment_setting="all",
                production_deployments_enabled=True,
            ),
        ),
    )

# github verification
cloudflare.DnsRecord(
    f"{BRN}-record-github-pages-verification",
    name="_github-pages-challenge-nathanvaughn",
    type="TXT",
    content='"61c0f594d3a99e1767d97f89802854"',
    ttl=AUTO_TTL,
    zone_id=zone.id,
)

# have i been pwned verification
utils.create_hibp_verification(zone.id, ZONE_NAME, "dweb_ze91kvkz82u3kj0ejw0l1pla")

# google site verification
cloudflare.DnsRecord(
    f"{BRN}-record-google-verification",
    name=ZONE_NAME,
    type="TXT",
    content='"google-site-verification=Z6heCb4QQucy-rAE6o7sRxZDry812WeO1u-ef5eY5Ys"',
    ttl=AUTO_TTL,
    zone_id=zone.id,
)

# keybase site verification
cloudflare.DnsRecord(
    f"{BRN}-record-keybase-verification",
    name=ZONE_NAME,
    type="TXT",
    content='"keybase-site-verification=yVOcfmhiYwOvGp2TJwUamoeF-mht3WFhkZayPNahuhQ"',
    ttl=AUTO_TTL,
    zone_id=zone.id,
)

# discord domain verification
cloudflare.DnsRecord(
    f"{BRN}-record-discord-verification",
    name="_discord",
    type="TXT",
    content='"dh=f320e6ec6a011d45b30580e2810e76df02c29824"',
    ttl=AUTO_TTL,
    zone_id=zone.id,
)

# bluesky domain verification
cloudflare.DnsRecord(
    f"{BRN}-record-bluesky-verification",
    name="_atproto",
    type="TXT",
    content='"did=did:plc:w5ao3j763odkgrb6d3drjebv"',
    ttl=AUTO_TTL,
    zone_id=zone.id,
)

# link shortener
# cloudflare.DnsRecord(
#     f"{BRN}-record-dub-co",
#     name="go",
#     type="CNAME",
#     content="cname.dub.co",
#     proxied=False,
#     ttl=AUTO_TTL,
#     zone_id=zone.id,
# )

# R2 bucket
cloudflare.DnsRecord(
    f"{BRN}-record-r2",
    name="files.nathanv.me",
    type="CNAME",
    content="public.r2.dev",
    proxied=True,
    ttl=AUTO_TTL,
    zone_id=zone.id,
)

# email security
utils.reject_emails(zone.id, ZONE_NAME)

# overall zone settings
# https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/data-sources/zone_setting#id-7
settings = {
    "automatic_https_rewrites": "on",
    "brotli": "on",
    "browser_cache_ttl": 60 * 60 * 24 * 31,  # seconds in a month
    "cache_level": "aggressive",
    "email_obfuscation": "on",
    "hotlink_protection": "off",
    "http3": "on",
    "ipv6": "on",
    "rocket_loader": "off",  # this caused problems in the past
    "security_level": "low",  # just static sites
    "security_header": {
        "enabled": True,
        "include_subdomains": True,
        "preload": True,
        "nosniff": True,
        "max_age": 60 * 60 * 24 * 30 * 6,  # seconds in 6 months
    },
    "ssl": "flexible",  # github didn't have SSL, could maybe upgrade to strict
}

for setting_id, value in settings.items():
    cloudflare.ZoneSetting(
        f"{BRN}-zone-setting-{setting_id}",
        setting_id=setting_id,
        value=value,
        zone_id=zone.id,
    )


# prevent AI bot scraping
cloudflare.BotManagement(
    f"{BRN}-bot-management", ai_bots_protection="block", zone_id=zone.id
)

# redirect kubernetes api name to github repo
utils.create_empty_record(zone.id, ZONE_NAME, "dnsconfigs")

# redirect git.nathanv.me to github
utils.create_empty_record(zone.id, ZONE_NAME, "git")

# redirect certain http requests
cloudflare.Ruleset(
    f"{BRN}-http-redirects",
    name="HTTP redirects",
    kind="zone",
    phase="http_request_dynamic_redirect",
    rules=[
        cloudflare.RulesetRuleArgs(
            action="redirect",
            expression=f'(http.host eq "dnsconfigs.{ZONE_NAME}")',
            enabled=True,
            action_parameters=cloudflare.RulesetRuleActionParametersArgs(
                from_value=cloudflare.RulesetRuleActionParametersFromValueArgs(
                    status_code=http.HTTPStatus.PERMANENT_REDIRECT,
                    target_url=cloudflare.RulesetRuleActionParametersFromValueTargetUrlArgs(
                        value="https://git.nathanv.me/k8s-dns"
                    ),
                    preserve_query_string=False,
                )
            ),
        ),
        cloudflare.RulesetRuleArgs(
            action="redirect",
            expression=f'(http.host eq "git.{ZONE_NAME}")',
            enabled=True,
            action_parameters=cloudflare.RulesetRuleActionParametersArgs(
                from_value=cloudflare.RulesetRuleActionParametersFromValueArgs(
                    status_code=http.HTTPStatus.PERMANENT_REDIRECT,
                    target_url=cloudflare.RulesetRuleActionParametersFromValueTargetUrlArgs(
                        expression='concat("https://github.com/NathanVaughn", http.request.uri.path)'
                    ),
                    preserve_query_string=False,
                )
            ),
        ),
    ],
    zone_id=zone.id,
)
