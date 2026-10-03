import pulumi_cloudflare as cloudflare

from iac import utils
from iac.config import CLOUDFLARE_ACCOUNT_ID
from iac.constants import SECONDS_IN_A_YEAR, ZONE_TYPE

ZONE_NAME = "nathanv.app"
BRN = utils.zone_to_name(ZONE_NAME)

# https://github.com/pulumi/pulumi-cloudflare/issues/1306
zone = cloudflare.Zone(
    f"{BRN}-zone", name=ZONE_NAME, account={"id": CLOUDFLARE_ACCOUNT_ID}, type=ZONE_TYPE
)

# https://github.com/pulumi/pulumi-cloudflare/issues/1232
cloudflare.ZoneDnssec(f"{BRN}-dnssec", zone_id=zone.id)

# have i been pwned verification
utils.create_hibp_verification(zone.id, ZONE_NAME, "dweb_sxmvyzv0drozr5fspuu67cxg")

# email security
utils.reject_emails(zone.id, ZONE_NAME)

# overall zone settings
# https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs/data-sources/zone_setting#id-7
settings = {
    "automatic_https_rewrites": "on",
    "brotli": "on",
    "browser_cache_ttl": 60 * 60 * 4,  # seconds in 4 hours
    "cache_level": "aggressive",
    "email_obfuscation": "on",
    "hotlink_protection": "off",
    "http3": "on",
    "ipv6": "on",
    "rocket_loader": "off",  # this caused problems in the past
    "security_level": "medium",
    "security_header": {
        "strict_transport_security": {
            "enabled": True,
            "include_subdomains": True,
            "preload": True,
            "nosniff": True,
            "max_age": 60 * 60 * 24 * 30 * 6,  # seconds in 6 months
        }
    },
    "ssl": "strict",
}

for setting_id, value in settings.items():
    cloudflare.ZoneSetting(
        f"{BRN}-zone-setting-{setting_id}",
        setting_id=setting_id,
        value=value,
        zone_id=zone.id,
    )

# root redirect rule
utils.create_root_redirect(zone.id, ZONE_NAME, "https://nathanv.me")

# cache immutable assets for 1 year
cloudflare.Ruleset(
    f"{BRN}-cache-packages-rule",
    name="Cache package assets",
    kind="zone",
    phase="http_request_cache_settings",
    rules=[
        cloudflare.RulesetRuleArgs(
            action="set_cache_settings",
            description="Cache Docker blobs for 1 year",
            expression=(
                '(http.host eq "cr.nathanv.app" and http.request.method eq "GET" and http.request.uri.path wildcard r"/v2/*/blobs/*")'
            ),
            enabled=True,
            action_parameters=cloudflare.RulesetRuleActionParametersArgs(
                cache=True,
                edge_ttl=cloudflare.RulesetRuleActionParametersEdgeTtlArgs(
                    mode="override_origin", default=SECONDS_IN_A_YEAR
                ),
                browser_ttl=cloudflare.RulesetRuleActionParametersBrowserTtlArgs(
                    mode="override_origin", default=SECONDS_IN_A_YEAR
                ),
            ),
        ),
        cloudflare.RulesetRuleArgs(
            action="set_cache_settings",
            description="Cache package assets for 1 year",
            expression=(
                '(http.host eq "pkgs.nathanv.app" and http.request.uri.path.extension in {"whl" "zip" "gz" "tgz"})'
            ),
            enabled=True,
            action_parameters=cloudflare.RulesetRuleActionParametersArgs(
                cache=True,
                edge_ttl=cloudflare.RulesetRuleActionParametersEdgeTtlArgs(
                    mode="override_origin", default=SECONDS_IN_A_YEAR
                ),
                browser_ttl=cloudflare.RulesetRuleActionParametersBrowserTtlArgs(
                    mode="override_origin", default=SECONDS_IN_A_YEAR
                ),
            ),
        ),
    ],
    zone_id=zone.id,
)
