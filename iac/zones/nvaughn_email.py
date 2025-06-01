import os

import pulumi_cloudflare as cloudflare

from iac import utils
from iac.config import CLOUDFLARE_ACCOUNT_ID

FILES_DIR = os.path.join(os.path.dirname(__file__), "..", "files")

ZONE = "nvaughn.email"
BRN = utils.zone_to_name(ZONE)

VANITY_EMAIL = f"nath@{ZONE}"
PERSONAL_EMAIL = "nvaughn51@gmail.com"

zone = cloudflare.Zone(
    f"{BRN}-zone", name=ZONE, account={"id": CLOUDFLARE_ACCOUNT_ID}, type="full"
)

zone_dnssec = cloudflare.ZoneDnssec(f"{BRN}-dnssec", zone_id=zone.id)

# sendgrid records
cloudflare.DnsRecord(
    f"{BRN}-record-sendgrid1",
    name="em2294",
    type="CNAME",
    content="u14911081.wl082.sendgrid.net",
    proxied=False,
    zone_id=zone.id,
)

cloudflare.DnsRecord(
    f"{BRN}-record-sendgrid2",
    name="s1._domainkey",
    type="CNAME",
    content="s1.domainkey.u14911081.wl082.sendgrid.net",
    proxied=False,
    zone_id=zone.id,
)

cloudflare.DnsRecord(
    f"{BRN}-record-sendgrid3",
    name="s2._domainkey",
    type="CNAME",
    content="s2.domainkey.u14911081.wl082.sendgrid.net",
    proxied=False,
    zone_id=zone.id,
)

# https://developers.cloudflare.com/email-routing/setup/mta-sts/
cloudflare.DnsRecord(
    f"{BRN}-record-_mta-sts",
    name="_mta-sts",
    type="CNAME",
    content="_mta-sts.mx.cloudflare.net",
    proxied=False,
    zone_id=zone.id,
)

# this record points to a worker
mta_sts_worker_record = utils.create_empty_record(zone.id, ZONE, "mta-sts")

# MX records
cloudflare.DnsRecord(
    f"{BRN}-record-mx1",
    name=zone.name,
    type="MX",
    content="route1.mx.cloudflare.net",
    priority=38,
    zone_id=zone.id,
)

cloudflare.DnsRecord(
    f"{BRN}-record-mx2",
    name=zone.name,
    type="MX",
    content="route2.mx.cloudflare.net",
    priority=70,
    zone_id=zone.id,
)

cloudflare.DnsRecord(
    f"{BRN}-record-mx3",
    name=zone.name,
    type="MX",
    content="route3.mx.cloudflare.net",
    priority=2,
    zone_id=zone.id,
)

# dmarc and spf
cloudflare.DnsRecord(
    f"{BRN}-record-dmarc",
    name="_dmarc",
    type="TXT",
    content='"v=DMARC1; p=reject; sp=reject; pct=100; rua=mailto:8f1ceab69df742f2a564c0a55b6eec75@dmarc-reports.cloudflare.net"',
    zone_id=zone.id,
)

cloudflare.DnsRecord(
    f"{BRN}-record-spf",
    name=ZONE,
    type="TXT",
    content='"v=spf1 include:_spf.mx.cloudflare.net -all"',
    zone_id=zone.id,
)

# BIMI
cloudflare.DnsRecord(
    f"{BRN}-record-bimi",
    name="default._bimi",
    type="TXT",
    content='"v=BIMI1; l=https://nathanv.me/img/theme-colors/red.svg"',
    zone_id=zone.id,
)

# TLS reporting
cloudflare.DnsRecord(
    f"{BRN}-record-smtp-tls",
    name="_smtp._tls",
    type="TXT",
    content=f'"v=TLSRPTv1; rua=mailto:{VANITY_EMAIL}"',
    zone_id=zone.id,
)

# have i been pwned verification
utils.create_hibp_verification(zone.id, ZONE, "dweb_r05p6qt6pohhgwdcxp96ufk7")

# MTA-STS worker
mta_sts_worker = cloudflare.WorkersScript(
    f"{BRN}-mta-sts-worker",
    account_id=zone.account_id,
    name="nvaughnemail-mta-sts",
    content=open(os.path.join(FILES_DIR, "nvaughnemail-mta-sts.js")).read(),
    module=True,
)

cloudflare.WorkersDomain(
    f"{BRN}-mta-sts-worker-domain",
    account_id=zone.account_id,
    hostname=mta_sts_worker_record.hostname,
    service=mta_sts_worker.name,
    zone_id=zone.id,
)

# email forwarding
cloudflare.EmailRoutingSettings(
    f"{BRN}-email-routing-settings",
    zone_id=zone.id,
    skip_wizard=True,
    enabled=True,
)

cloudflare.EmailRoutingAddress(
    f"{BRN}-email-routing-address",
    account_id=CLOUDFLARE_ACCOUNT_ID,
    email=PERSONAL_EMAIL,
)

cloudflare.EmailRoutingRule(
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
utils.create_root_redirect(zone.id, ZONE, "https://nathanv.me")
