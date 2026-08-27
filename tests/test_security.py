from __future__ import annotations

from dataclasses import replace

from twilio.request_validator import RequestValidator

from pgai_voicebot.security import validate_twilio_signature


def test_signature_validation_fails_closed_without_signature(live_settings) -> None:
    assert not validate_twilio_signature(
        live_settings,
        url="https://voice.example.test/calls/status",
        signature=None,
        params={"CallSid": "CA123"},
    )


def test_signature_validation_can_be_disabled_only_for_local_tests(live_settings) -> None:
    local = replace(live_settings, validate_twilio_signatures=False)

    assert validate_twilio_signature(
        local,
        url="http://testserver/calls/status",
        signature=None,
        params={},
    )


def test_valid_twilio_signature_is_accepted(live_settings) -> None:
    url = "https://voice.example.test/calls/status"
    params = {"CallSid": "CA123", "CallStatus": "completed"}
    signature = RequestValidator(live_settings.twilio_auth_token).compute_signature(url, params)

    assert validate_twilio_signature(
        live_settings,
        url=url,
        signature=signature,
        params=params,
    )
