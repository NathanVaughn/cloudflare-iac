import pulumi_cloudflare as cloudflare

from iac.config import CLOUDFLARE_ACCOUNT_ID

# base resource name
BRN = "nathanv-me"
ZONE = "nathanv.me"


zone = cloudflare.Zone(
    f"{BRN}-zone", zone=ZONE, plan="free", account_id=CLOUDFLARE_ACCOUNT_ID
)

cloudflare.ZoneDnssec(f"{BRN}-dnssec", zone_id=zone.id)

# cloudflare pages
cloudflare.Record(
    f"{BRN}-record-homepage",
    name=ZONE,
    type="CNAME",
    value="nathanv-me.pages.dev",
    proxied=True,
    zone_id=zone.id,
)

cloudflare.Record(
    f"{BRN}-record-homepage-www",
    name="www",
    type="CNAME",
    value="nathanv-me.pages.dev",
    proxied=True,
    zone_id=zone.id,
)

other_pages = ["blog", "links", "pay"]
for op in other_pages:
    cloudflare.Record(
        f"{BRN}-record-{op}",
        name=op,
        type="CNAME",
        value=f"{op}-nathanv-me.pages.dev",
        proxied=True,
        zone_id=zone.id,
    )

    cloudflare.Record(
        f"{BRN}-record-{op}-www",
        name=f"www.{op}",
        type="CNAME",
        value=f"{op}-nathanv-me.pages.dev",
        proxied=True,
        zone_id=zone.id,
    )

# github verification
cloudflare.Record(
    f"{BRN}-record-github-pages-verification",
    name="_github-pages-challenge-nathanvaughn",
    type="TXT",
    value="61c0f594d3a99e1767d97f89802854",
    zone_id=zone.id,
)

# have i been pwned verification
cloudflare.Record(
    f"{BRN}-record-hibp-verification",
    name=ZONE,
    type="TXT",
    value="have-i-been-pwned-verification=dweb_ze91kvkz82u3kj0ejw0l1pla",
    zone_id=zone.id,
)

# google site verification
cloudflare.Record(
    f"{BRN}-record-google-verification",
    name=ZONE,
    type="TXT",
    value="google-site-verification=Z6heCb4QQucy-rAE6o7sRxZDry812WeO1u-ef5eY5Ys",
    zone_id=zone.id,
)

# keybase site verification
cloudflare.Record(
    f"{BRN}-record-keybase-verification",
    name=ZONE,
    type="TXT",
    value="keybase-site-verification=yVOcfmhiYwOvGp2TJwUamoeF-mht3WFhkZayPNahuhQ",
    zone_id=zone.id,
)

# link shortener
cloudflare.Record(
    f"{BRN}-record-dub-co",
    name="go",
    type="CNAME",
    value="cname.dub.co",
    proxied=False,
    zone_id=zone.id,
)

# R2 bucket
cloudflare.Record(
    f"{BRN}-record-r2",
    name="files",
    type="CNAME",
    value="public.r2.dev",
    proxied=True,
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


cloudflare.ZoneSettingsOverride(
    f"{BRN}-zone-settings",
    settings=cloudflare.ZoneSettingsOverrideSettingsArgs(
        always_online="on",
        always_use_https="on",
        automatic_https_rewrites="on",
        brotli="on",
        browser_cache_ttl=60 * 60 * 24 * 31,  # seconds in a month
        browser_check="on",
        cache_level="aggressive",
        challenge_ttl=60 * 60,  # seconds in an hour
        early_hints="on",
        email_obfuscation="on",
        hotlink_protection="off",
        http3="on",
        ipv6="on",
        minify=cloudflare.ZoneSettingsOverrideSettingsMinifyArgs(
            html="on", css="on", js="on"
        ),
        opportunistic_onion="on",
        rocket_loader="off",  # this caused problems in the past
        security_header=cloudflare.ZoneSettingsOverrideSettingsSecurityHeaderArgs(
            enabled=True,
            include_subdomains=True,
            preload=True,
            nosniff=True,
            max_age=60 * 60 * 24 * 30 * 6,
        ),  # seconds in 6 months
        security_level="low",  # just static sites
        ssl="flexible",
    ),
    zone_id=zone.id,
)
