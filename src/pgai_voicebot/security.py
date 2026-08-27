"""Twilio request-signature validation helpers."""

from __future__ import annotations

from collections.abc import Mapping

from .config import Settings


def validate_twilio_signature(
    settings: Settings,
    *,
    url: str,
    signature: str | None,
    params: Mapping[str, str] | None = None,
) -> bool:
    if not settings.validate_twilio_signatures:
        return True
    if not settings.twilio_auth_token or not signature:
        return False

    from twilio.request_validator import RequestValidator

    validator = RequestValidator(settings.twilio_auth_token)
    payload = dict(params or {})
    candidates = [url]
    if url.endswith("/"):
        candidates.append(url.rstrip("/"))
    else:
        candidates.append(url + "/")
    return any(validator.validate(candidate, payload, signature) for candidate in candidates)
