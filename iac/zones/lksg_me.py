import pulumi_cloudflare as cloudflare

from iac import utils
from iac.config import CLOUDFLARE_ACCOUNT_ID
from iac.constants import AUTO_TTL, ZONE_TYPE

ZONE_NAME = "lksg.me"
BRN = utils.zone_to_name(ZONE_NAME)

# https://github.com/pulumi/pulumi-cloudflare/issues/1306
zone = cloudflare.Zone(
    f"{BRN}-zone", name=ZONE_NAME, account={"id": CLOUDFLARE_ACCOUNT_ID}, type=ZONE_TYPE
)

# https://github.com/pulumi/pulumi-cloudflare/issues/1232
cloudflare.ZoneDnssec(f"{BRN}-dnssec", zone_id=zone.id)

# old CNAMES
old_cnames = ["www", "cdn", "dev-cdn", "dev", "status"]
for oc in old_cnames:
    cloudflare.DnsRecord(
        f"{BRN}-record-{oc}",
        name=oc,
        type="CNAME",
        content=ZONE_NAME,
        proxied=True,
        ttl=AUTO_TTL,
        zone_id=zone.id,
    )

# github verification
cloudflare.DnsRecord(
    f"{BRN}-record-github-verification",
    name="_github-challenge-linkspring",
    type="TXT",
    content='"45d26e5df8"',
    ttl=AUTO_TTL,
    zone_id=zone.id,
)

# email security
utils.reject_emails(zone.id, ZONE_NAME)

# root redirect rule
utils.create_root_redirect(
    zone.id, ZONE_NAME, "https://links.nathanv.me", all_traffic=True
)
