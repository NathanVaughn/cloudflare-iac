import http
from typing import NamedTuple

import pulumi_cloudflare as cloudflare

from iac import utils
from iac.config import CLOUDFLARE_ACCOUNT_ID

ZONE = "nathanv.me"
BRN = utils.zone_to_name(ZONE)


class PagesConfig(NamedTuple):
    subdomain: str
    name: str


pages_configs = [
    PagesConfig("", "homepage"),
    PagesConfig("blog", "blog"),
    PagesConfig("links", "links"),
    PagesConfig("pay", "pay"),
]

zone = cloudflare.Zone(
    f"{BRN}-zone", zone=ZONE, plan="free", account_id=CLOUDFLARE_ACCOUNT_ID
)

cloudflare.ZoneDnssec(f"{BRN}-dnssec", zone_id=zone.id)


# cloudflare pages
for pc in pages_configs:
    domain = ZONE

    # build the domain name of the page
    if pc.subdomain:
        domain = f"{pc.subdomain}.{ZONE}"

    project_name = utils.zone_to_name(domain)

    # create the pages domains and DNS records

    # root
    cloudflare.PagesDomain(
        f"{BRN}-pages-domain-{pc.name}",
        account_id=zone.account_id,
        domain=domain,
        project_name=project_name,
    )

    cloudflare.Record(
        f"{BRN}-record-{pc.name}",
        name=domain,
        type="CNAME",
        content=f"{project_name}.pages.dev",
        proxied=True,
        zone_id=zone.id,
    )

    # www
    cloudflare.PagesDomain(
        f"{BRN}-pages-domain-www-{pc.name}",
        account_id=zone.account_id,
        domain=f"www.{domain}",
        project_name=project_name,
    )

    cloudflare.Record(
        f"{BRN}-record-{pc.name}-www",
        name=f"www.{domain}",
        type="CNAME",
        content=f"{project_name}.pages.dev",
        proxied=True,
        zone_id=zone.id,
    )

    # create the project
    branch = "main"
    cloudflare.PagesProject(
        f"{BRN}-pages-project-{pc.name}",
        account_id=zone.account_id,
        name=project_name,
        build_config=cloudflare.PagesProjectBuildConfigArgs(
            build_caching=True, build_command="npm run build", destination_dir="public"
        ),
        production_branch=branch,
        source=cloudflare.PagesProjectSourceArgs(
            type="github",
            config=cloudflare.PagesProjectSourceConfigArgs(
                owner="NathanVaughn",
                repo_name=domain,
                production_branch=branch,
                pr_comments_enabled=True,
                deployments_enabled=True,
                production_deployment_enabled=True,
            ),
        ),
    )

# github verification
cloudflare.Record(
    f"{BRN}-record-github-pages-verification",
    name="_github-pages-challenge-nathanvaughn",
    type="TXT",
    content='"61c0f594d3a99e1767d97f89802854"',
    zone_id=zone.id,
)

# have i been pwned verification
utils.create_hibp_verification(zone.id, ZONE, "dweb_ze91kvkz82u3kj0ejw0l1pla")

# google site verification
cloudflare.Record(
    f"{BRN}-record-google-verification",
    name=ZONE,
    type="TXT",
    content='"google-site-verification=Z6heCb4QQucy-rAE6o7sRxZDry812WeO1u-ef5eY5Ys"',
    zone_id=zone.id,
)

# keybase site verification
cloudflare.Record(
    f"{BRN}-record-keybase-verification",
    name=ZONE,
    type="TXT",
    content='"keybase-site-verification=yVOcfmhiYwOvGp2TJwUamoeF-mht3WFhkZayPNahuhQ"',
    zone_id=zone.id,
)

# discord domain verification
cloudflare.Record(
    f"{BRN}-record-discord-verification",
    name="_discord",
    type="TXT",
    content='"dh=f320e6ec6a011d45b30580e2810e76df02c29824"',
    zone_id=zone.id,
)

# bluesky domain verification
cloudflare.Record(
    f"{BRN}-record-bluesky-verification",
    name="_atproto",
    type="TXT",
    content='"did=did:plc:w5ao3j763odkgrb6d3drjebv"',
    zone_id=zone.id,
)

# link shortener
cloudflare.Record(
    f"{BRN}-record-dub-co",
    name="go",
    type="CNAME",
    content="cname.dub.co",
    proxied=False,
    zone_id=zone.id,
)

# R2 bucket
cloudflare.Record(
    f"{BRN}-record-r2",
    name="files",
    type="CNAME",
    content="public.r2.dev",
    proxied=True,
    zone_id=zone.id,
)

# email security
utils.reject_emails(zone.id, ZONE)

# overall zone settings
cloudflare.ZoneSettingsOverride(
    f"{BRN}-zone-settings",
    settings=cloudflare.ZoneSettingsOverrideSettingsArgs(
        always_online="on",
        always_use_https="on",
        automatic_https_rewrites="on",
        brotli="on",
        browser_cache_ttl=60 * 60 * 24 * 31,  # seconds in a month
        browser_check="on",
        cache_level="aggressive",
        challenge_ttl=60 * 60,  # seconds in an hour
        early_hints="on",
        email_obfuscation="on",
        hotlink_protection="off",
        http3="on",
        ipv6="on",
        # updating this was causing errors with "__default" field schema changes
        # minify=cloudflare.ZoneSettingsOverrideSettingsMinifyArgs(
        #     html="on", css="on", js="on"
        # ),
        opportunistic_onion="on",
        rocket_loader="off",  # this caused problems in the past
        security_header=cloudflare.ZoneSettingsOverrideSettingsSecurityHeaderArgs(
            enabled=True,
            include_subdomains=True,
            preload=True,
            nosniff=True,
            max_age=60 * 60 * 24 * 30 * 6,
        ),  # seconds in 6 months
        security_level="low",  # just static sites
        ssl="flexible",
    ),
    zone_id=zone.id,
)

# prevent AI bot scraping
cloudflare.BotManagement(
    f"{BRN}-bot-management", ai_bots_protection="block", zone_id=zone.id
)

# redirect kubernetes api name to github repo
utils.create_empty_record(zone.id, ZONE, "dnsconfigs")

# redirect git.nathanv.me to github
utils.create_empty_record(zone.id, ZONE, "git")

# redirect certain http requests
cloudflare.Ruleset(
    f"{BRN}-http-redirects",
    name="HTTP redirects",
    kind="zone",
    phase="http_request_dynamic_redirect",
    rules=[
        cloudflare.RulesetRuleArgs(
            action="redirect",
            expression=f'(http.host eq "dnsconfigs.{ZONE}")',
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
            expression=f'(http.host eq "git.{ZONE}")',
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
