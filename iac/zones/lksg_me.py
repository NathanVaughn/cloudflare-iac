import pulumi_cloudflare as cloudflare

from iac import utils
from iac.config import CLOUDFLARE_ACCOUNT_ID

ZONE = "lksg.me"
BRN = utils.zone_to_name(ZONE)

zone = cloudflare.Zone(
    f"{BRN}-zone", name=ZONE, account={"id": CLOUDFLARE_ACCOUNT_ID}, type="full"
)

cloudflare.ZoneDnssec(f"{BRN}-dnssec", zone_id=zone.id)

# old CNAMES
old_cnames = ["www", "cdn", "dev-cdn", "dev", "status"]
for oc in old_cnames:
    cloudflare.DnsRecord(
        f"{BRN}-record-{oc}",
        name=oc,
        type="CNAME",
        content=ZONE,
        proxied=True,
        zone_id=zone.id,
    )

# github verification
cloudflare.DnsRecord(
    f"{BRN}-record-github-verification",
    name="_github-challenge-linkspring",
    type="TXT",
    content='"45d26e5df8"',
    zone_id=zone.id,
)

# email security
utils.reject_emails(zone.id, ZONE)

# root redirect rule
utils.create_root_redirect(zone.id, ZONE, "https://links.nathanv.me", all_traffic=True)
