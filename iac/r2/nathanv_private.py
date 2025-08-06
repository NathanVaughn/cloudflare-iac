import pulumi_cloudflare as cloudflare

from iac.config import CLOUDFLARE_ACCOUNT_ID

cloudflare.R2Bucket(
    "nathanv-private-r2-bucket",
    account_id=CLOUDFLARE_ACCOUNT_ID,
    name="nathanv-private",
    location="ENAM",
    storage_class="Standard",
    jurisdiction="default",
)
