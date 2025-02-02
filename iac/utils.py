import http

import pulumi
import pulumi_cloudflare as cloudflare

from iac.config import INVALID_IP


def zone_to_name(zone: str) -> str:
    """
    Transform a zone name into a resource name.
    Example: `nathanv.me` -> `nathanv-me`
    """
    return zone.replace(".", "-")


def create_empty_record(
    zone_id: pulumi.Input[str], zone_name: str, name: str
) -> cloudflare.Record:
    """
    Create a record that is intended to be handled by other Cloudflare services.
    """
    brn = zone_to_name(zone_name)
    label = name or "root"

    return cloudflare.Record(
        f"{brn}-record-{label}",
        name=name,
        type="AAAA",
        content=INVALID_IP,
        proxied=True,
        zone_id=zone_id,
    )


def reject_emails(zone_id: pulumi.Input[str], zone_name: str) -> None:
    """
    Create DMARC, SPF, and domain key records to reject all emails.
    """
    brn = zone_to_name(zone_name)

    cloudflare.Record(
        f"{brn}-record-dmarc",
        name="_dmarc",
        type="TXT",
        content="v=DMARC1; p=reject; sp=reject;",
        zone_id=zone_id,
    )

    cloudflare.Record(
        f"{brn}-record-spf",
        name=zone_name,
        type="TXT",
        content="v=spf1 -all",
        zone_id=zone_id,
    )

    cloudflare.Record(
        f"{brn}-record-domainkey",
        name="*._domainkey",
        type="TXT",
        content="v=DKIM1; p=",
        zone_id=zone_id,
    )


def create_root_redirect(
    zone_id: pulumi.Input[str], zone_name: str, target: str, all_traffic: bool = False
) -> None:
    """
    Create a root redirect rule.
    """
    brn = zone_to_name(zone_name)

    create_empty_record(zone_id, zone_name, "")

    expression = f'(http.host eq "{zone_name}")'
    if all_traffic:
        expression = "true"

    cloudflare.Ruleset(
        f"{brn}-root-redirect",
        name="Redirect all",
        kind="zone",
        phase="http_request_dynamic_redirect",
        rules=[
            cloudflare.RulesetRuleArgs(
                action="redirect",
                expression=expression,
                enabled=True,
                action_parameters=cloudflare.RulesetRuleActionParametersArgs(
                    from_value=cloudflare.RulesetRuleActionParametersFromValueArgs(
                        status_code=http.HTTPStatus.PERMANENT_REDIRECT,
                        target_url=cloudflare.RulesetRuleActionParametersFromValueTargetUrlArgs(
                            value=target
                        ),
                        preserve_query_string=False,
                    )
                ),
            ),
        ],
        zone_id=zone_id,
    )


def create_hibp_verification(
    zone_id: pulumi.Input[str], zone_name: str, verification_id: str
) -> None:
    """
    Create a have i been pwned verification record.
    """
    brn = zone_to_name(zone_name)

    cloudflare.Record(
        f"{brn}-record-hibp-verification",
        name=zone_name,
        type="TXT",
        content=f"have-i-been-pwned-verification={verification_id}",
        zone_id=zone_id,
    )
