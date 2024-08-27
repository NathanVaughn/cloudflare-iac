import pulumi_cloudflare as cloudflare

from iac import utils
from iac.config import CLOUDFLARE_ACCOUNT_ID

# base resource name
ZONE = "nathanv.app"
BRN = utils.zone_to_name(ZONE)


zone = cloudflare.Zone(
    f"{BRN}-zone", zone=ZONE, plan="free", account_id=CLOUDFLARE_ACCOUNT_ID
)

cloudflare.ZoneDnssec(f"{BRN}-dnssec", zone_id=zone.id)


# have i been pwned verification
utils.create_hibp_verification(zone.id, ZONE, "dweb_sxmvyzv0drozr5fspuu67cxg")

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
        browser_cache_ttl=60 * 60 * 4,  # seconds in 4 hours
        browser_check="off",
        cache_level="aggressive",
        challenge_ttl=60 * 60,  # seconds in an hour
        early_hints="on",
        email_obfuscation="on",
        hotlink_protection="off",
        http3="on",
        ipv6="on",
        # updating this was causing errors with "__default" field schema changes
        # minify=cloudflare.ZoneSettingsOverrideSettingsMinifyArgs(
        #     html="on",
        #     css="on",
        #     js="on",
        #     # was off for JS and CSS, need to monitor
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
        security_level="medium",
        ssl="strict",
    ),
    zone_id=zone.id,
)

# root redirect rule
utils.create_root_redirect(zone.id, ZONE, "https://nathanv.me")
