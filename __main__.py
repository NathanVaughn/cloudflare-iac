from iac.r2 import (
    nathanv_private,  # noqa: F401
    nathanv_public,  # noqa: F401
)
from iac.zones.lksg_me import ZONE_NAME as lksg_me_zone
from iac.zones.nathanv_app import ZONE_NAME as nathanv_app_zone
from iac.zones.nathanv_me import ZONE_NAME as nathanv_me_zone
from iac.zones.nvaughn_email import ZONE_NAME as nvaughn_email_zone

print(f"Imported configuration for {lksg_me_zone}")
print(f"Imported configuration for {nathanv_app_zone}")
print(f"Imported configuration for {nathanv_me_zone}")
print(f"Imported configuration for {nvaughn_email_zone}")
