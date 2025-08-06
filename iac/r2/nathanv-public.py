import pulumi_cloudflare as cloudflare

from iac.config import CLOUDFLARE_ACCOUNT_ID

public_r2_bucket = cloudflare.R2Bucket(
    "nathanv-public-r2-bucket",
    account_id=CLOUDFLARE_ACCOUNT_ID,
    name="nathanv-public",
    location="ENAM",
    storage_class="Standard",
    jurisdiction="default",
)

# https://github.com/pulumi/pulumi-cloudflare/issues/1174
# can't import
# cloudflare.R2CustomDomain(
#     "nathanv-public-r2-domain",
#     account_id=CLOUDFLARE_ACCOUNT_ID,
#     bucket_name=public_r2_bucket.name,
#     domain="files.nathanv.me",
#     enabled=True,
# )
