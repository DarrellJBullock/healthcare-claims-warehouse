"""
Identifier masking for HIPAA-aware display of synthetic claims data.

Synthetic data only. No real PHI is used in this portfolio project.

Masking pattern for structured identifiers (member_id, subscriber_id,
claim_id, payment_id, ...):

    MBR-10039281      -> MBR-••••9281
    CLM-2026-000938   -> CLM-••••0938

The prefix before the first hyphen is kept, the remaining segments are
concatenated and only the last 4 characters are shown.
"""

MASK_CHAR = "•"  # •


def mask_identifier(value: str) -> str:
    if not value:
        return value
    parts = value.split("-")
    if len(parts) < 2:
        return f"{MASK_CHAR * 4}{value[-4:]}" if len(value) > 4 else MASK_CHAR * len(value)
    prefix = parts[0]
    remainder = "".join(parts[1:])
    suffix = remainder[-4:] if len(remainder) >= 4 else remainder
    return f"{prefix}-{MASK_CHAR * 4}{suffix}"


def mask_date_of_birth(value) -> str:
    """Reduces a date of birth to just the birth year, e.g. 1985-**-**"""
    if not value:
        return value
    year = value.year if hasattr(value, "year") else str(value)[:4]
    return f"{year}-**-**"


def mask_address(value: str) -> str:
    if not value:
        return value
    tokens = value.split(",")
    if len(tokens) > 1:
        return f"{MASK_CHAR * 6}, {tokens[-1].strip()}"
    return MASK_CHAR * 8


def mask_phone(value: str) -> str:
    if not value:
        return value
    digits = "".join(ch for ch in value if ch.isdigit())
    last4 = digits[-4:] if len(digits) >= 4 else digits
    return f"{MASK_CHAR * 3}-{MASK_CHAR * 3}-{last4}"


def mask_email(value: str) -> str:
    if not value or "@" not in value:
        return MASK_CHAR * 8
    local, domain = value.split("@", 1)
    visible = local[0] if local else ""
    return f"{visible}{MASK_CHAR * 3}@{domain}"


def mask_claim_payload(data: dict, *, mask: bool = True) -> dict:
    """Applies masking to a serialized claim dict's sensitive fields."""
    if not mask:
        return data
    masked = dict(data)
    for field in ("claim_id", "member_id", "subscriber_id"):
        if masked.get(field):
            masked[field] = mask_identifier(masked[field])
    return masked


def mask_member_payload(data: dict, *, mask: bool = True) -> dict:
    """Applies masking to a serialized member dict's sensitive fields."""
    if not mask:
        return data
    masked = dict(data)
    if masked.get("member_id"):
        masked["member_id"] = mask_identifier(masked["member_id"])
    if masked.get("subscriber_id"):
        masked["subscriber_id"] = mask_identifier(masked["subscriber_id"])
    if masked.get("date_of_birth"):
        masked["date_of_birth"] = mask_date_of_birth(masked["date_of_birth"])
    if masked.get("address"):
        masked["address"] = mask_address(masked["address"])
    if masked.get("phone"):
        masked["phone"] = mask_phone(masked["phone"])
    if masked.get("email"):
        masked["email"] = mask_email(masked["email"])
    return masked
