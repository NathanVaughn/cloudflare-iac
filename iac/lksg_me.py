import http

import pulumi_cloudflare as cloudflare

from iac.config import CLOUDFLARE_ACCOUNT_ID, INVALID_IP

# base resource name
BRN = "lksg-me"
ZONE = "lksg.me"


zone = cloudflare.Zone(
    f"{BRN}-zone", zone=ZONE, plan="free", account_id=CLOUDFLARE_ACCOUNT_ID
)

cloudflare.ZoneDnssec(f"{BRN}-dnssec", zone_id=zone.id)

cloudflare.Record(
    f"{BRN}-record-root",
    name=ZONE,
    type="AAAA",
    value=INVALID_IP,
    proxied=True,
    zone_id=zone.id,
)

# old CNAMES
old_cnames = ["www", "cdn", "dev-cdn", "dev", "status"]
for oc in old_cnames:
    cloudflare.Record(
        f"{BRN}-record-{oc}",
        name=oc,
        type="CNAME",
        value=ZONE,
        proxied=True,
        zone_id=zone.id,
    )

# github verification
cloudflare.Record(
    f"{BRN}-record-github-verification",
    name="_github-challenge-linkspring",
    type="TXT",
    value="45d26e5df8",
    zone_id=zone.id,
)

# email security
cloudflare.Record(
    f"{BRN}-record-dmarc",
    name="_dmarc",
    type="TXT",
    value="v=DMARC1; p=reject; sp=reject;",
    zone_id=zone.id,
)

cloudflare.Record(
    f"{BRN}-record-spf",
    name=ZONE,
    type="TXT",
    value="v=spf1 -all",
    zone_id=zone.id,
)

cloudflare.Record(
    f"{BRN}-record-domainkey",
    name="*._domainkey",
    type="TXT",
    value="v=DKIM1; p=",
    zone_id=zone.id,
)

# root redirect rule
cloudflare.Ruleset(
    f"{BRN}-root-redirect",
    name="Redirect all",
    kind="zone",
    phase="http_request_dynamic_redirect",
    rules=[
        cloudflare.RulesetRuleArgs(
            action="redirect",
            expression=f'(http.host eq "{ZONE}")',
            enabled=True,
            action_parameters=cloudflare.RulesetRuleActionParametersArgs(
                from_value=cloudflare.RulesetRuleActionParametersFromValueArgs(
                    status_code=http.HTTPStatus.PERMANENT_REDIRECT,
                    target_url=cloudflare.RulesetRuleActionParametersFromValueTargetUrlArgs(
                        value="https://links.nathanv.me"
                    ),
                    preserve_query_string=False,
                )
            ),
        ),
    ],
    zone_id=zone.id,
)
