# zone type, since we don't have DNS only zones
ZONE_TYPE = "full"

# what cloudflare uses for Workers domains
INVALID_IP = "100::"

# how long to cache DNS records
AUTO_TTL = 1

SECONDS_IN_A_YEAR = (60 * 60 * 24 * 365,)  # seconds in 1 year
