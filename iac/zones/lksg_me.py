import pulumi_cloudflare as cloudflare

from iac import utils
from iac.config import CLOUDFLARE_ACCOUNT_ID, ZONE_TYPE

ZONE_NAME = "lksg.me"
BRN = utils.zone_to_name(ZONE_NAME)

zone = cloudflare.Zone(
    f"{BRN}-zone", name=ZONE_NAME, account={"id": CLOUDFLARE_ACCOUNT_ID}, type=ZONE_TYPE
)

cloudflare.ZoneDnssec(f"{BRN}-dnssec", zone_id=zone.id)

# old CNAMES
old_cnames = ["www", "cdn", "dev-cdn", "dev", "status"]
for oc in old_cnames:
    cloudflare.Record(
        f"{BRN}-record-{oc}",
        name=oc,
        type="CNAME",
        content=ZONE_NAME,
        proxied=True,
        zone_id=zone.id,
    )

# github verification
cloudflare.Record(
    f"{BRN}-record-github-verification",
    name="_github-challenge-linkspring",
    type="TXT",
    content='"45d26e5df8"',
    zone_id=zone.id,
)

# email security
utils.reject_emails(zone.id, ZONE_NAME)

# root redirect rule
utils.create_root_redirect(
    zone.id, ZONE_NAME, "https://links.nathanv.me", all_traffic=True
)
