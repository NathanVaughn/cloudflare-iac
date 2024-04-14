import http
import os

import pulumi_cloudflare as cloudflare

from iac.config import CLOUDFLARE_ACCOUNT_ID

THIS_DIR = os.path.dirname(__file__)

# base resource name
BRN = "nvaughn-email"
ZONE = "nvaughn.email"
VANITY_EMAIL = f"nath@{ZONE}"
PERSONAL_EMAIL = "nvaughn51@gmail.com"
INVALID_IP = "10::"

zone = cloudflare.Zone(
    f"{BRN}-zone", zone=ZONE, plan="free", account_id=CLOUDFLARE_ACCOUNT_ID
)

zone_dnssec = cloudflare.ZoneDnssec(f"{BRN}-dnssec", zone_id=zone.id)

root_record = cloudflare.Record(
    f"{BRN}-record-root",
    name=ZONE,
    type="AAAA",
    value=INVALID_IP,
    proxied=True,
    zone_id=zone.id,
)

# sendgrid records
sendgrid_record1 = cloudflare.Record(
    f"{BRN}-record-sendgrid1",
    name="em2294",
    type="CNAME",
    value="u14911081.wl082.sendgrid.net",
    proxied=False,
    zone_id=zone.id,
)

sendgrid_record2 = cloudflare.Record(
    f"{BRN}-record-sendgrid2",
    name="s1._domainkey",
    type="CNAME",
    value="s1.domainkey.u14911081.wl082.sendgrid.net",
    proxied=False,
    zone_id=zone.id,
)

sendgrid_record3 = cloudflare.Record(
    f"{BRN}-record-sendgrid3",
    name="s2._domainkey",
    type="CNAME",
    value="s2.domainkey.u14911081.wl082.sendgrid.net",
    proxied=False,
    zone_id=zone.id,
)

# https://developers.cloudflare.com/email-routing/setup/mta-sts/
mta_sts_record = cloudflare.Record(
    f"{BRN}-record-mta-sts",
    name="_mta-sts",
    type="CNAME",
    value="_mta-sts.mx.cloudflare.net",
    proxied=False,
    zone_id=zone.id,
)

# this record points to a worker
mta_sts_worker_record = cloudflare.Record(
    f"{BRN}-record-mta-sts-worker",
    name="mta-sts",
    type="AAAA",
    value=INVALID_IP,
    proxied=True,
    zone_id=zone.id,
)

# MX records
mx_record1 = cloudflare.Record(
    f"{BRN}-record-mx1",
    name=zone.zone,
    type="MX",
    value="route1.mx.cloudflare.net",
    priority=38,
    zone_id=zone.id,
)

mx_record2 = cloudflare.Record(
    f"{BRN}-record-mx2",
    name=zone.zone,
    type="MX",
    value="route2.mx.cloudflare.net",
    priority=70,
    zone_id=zone.id,
)

mx_record3 = cloudflare.Record(
    f"{BRN}-record-mx3",
    name=zone.zone,
    type="MX",
    value="route3.mx.cloudflare.net",
    priority=2,
    zone_id=zone.id,
)

# dmarc and spf
dmarc_record = cloudflare.Record(
    f"{BRN}-record-dmarc",
    name="_dmarc",
    type="TXT",
    value="v=DMARC1; p=reject; sp=reject; pct=100; rua=mailto:8f1ceab69df742f2a564c0a55b6eec75@dmarc-reports.cloudflare.net",
    zone_id=zone.id,
)

spf_record = cloudflare.Record(
    f"{BRN}-record-spf",
    name=ZONE,
    type="TXT",
    value="v=spf1 include:_spf.mx.cloudflare.net -all",
    zone_id=zone.id,
)

# BIMI
bimi_record = cloudflare.Record(
    f"{BRN}-record-bimi",
    name="default._bimi",
    type="TXT",
    value="v=BIMI1; l=https://nathanv.me/img/theme-colors/red.svg",
    zone_id=zone.id,
)

# TLS reporting
smtp_tls_record = cloudflare.Record(
    f"{BRN}-record-smtp-tls",
    name="_smtp._tls",
    type="TXT",
    value=f"v=TLSRPTv1; rua=mailto:{VANITY_EMAIL}",
    zone_id=zone.id,
)

# have i been pwned verification
hibp_record = cloudflare.Record(
    f"{BRN}-record-hibp-verification",
    name=ZONE,
    type="TXT",
    value="have-i-been-pwned-verification=dweb_r05p6qt6pohhgwdcxp96ufk7",
    zone_id=zone.id,
)

# MTA-STS worker
mta_sts_worker = cloudflare.WorkerScript(
    f"{BRN}-mta-sts-worker",
    account_id=zone.account_id,
    name="nvaughnemail-mta-sts",
    content=open(os.path.join(THIS_DIR, "nvaughnemail-mta-sts.js")).read(),
    module=True,
)

mta_sts_worker_domain = cloudflare.WorkerDomain(
    f"{BRN}-mta-sts-worker-domain",
    account_id=zone.account_id,
    hostname=mta_sts_worker_record.hostname,
    service=mta_sts_worker.name,
    zone_id=zone.id,
)

# email forwarding
email_routing_settings = cloudflare.EmailRoutingSettings(
    f"{BRN}-email-routing-settings",
    zone_id=zone.id,
    skip_wizard=True,
    enabled=True,
)

email_routing_address = cloudflare.EmailRoutingAddress(
    f"{BRN}-email-routing-address",
    account_id=zone.account_id,
    email=PERSONAL_EMAIL,
)

email_routing_rule = cloudflare.EmailRoutingRule(
    f"{BRN}-vanity_email_forward",
    name="Vanity Email Forward",
    matchers=[
        cloudflare.EmailRoutingRuleMatcherArgs(
            field="to",
            type="literal",
            value=VANITY_EMAIL,
        )
    ],
    actions=[
        cloudflare.EmailRoutingRuleActionArgs(type="forward", values=[PERSONAL_EMAIL])
    ],
    enabled=True,
    zone_id=zone.id,
)


# root redirect rule
root_redirect = cloudflare.Ruleset(
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
                        value="https://nathanv.me"
                    ),
                    preserve_query_string=False,
                )
            ),
        ),
    ],
    zone_id=zone.id,
)
