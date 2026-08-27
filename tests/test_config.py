from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from pgai_voicebot.config import ConfigurationError


def test_dry_configuration_fails_closed_for_live_calls(dry_settings) -> None:
    with pytest.raises(ConfigurationError, match="Live call blocked") as error:
        dry_settings.require_live_call_ready()

    message = str(error.value)
    assert "PGVOICE_ENABLE_LIVE_CALLS" in message
    assert "OPENAI_API_KEY" in message
    assert "TWILIO_ACCOUNT_SID" in message


def test_live_configuration_requires_signature_validation(live_settings) -> None:
    unsafe = replace(live_settings, validate_twilio_signatures=False)

    with pytest.raises(ConfigurationError, match="TWILIO_VALIDATE_SIGNATURES"):
        unsafe.require_live_call_ready()


def test_live_configuration_accepts_complete_settings(live_settings) -> None:
    live_settings.require_live_call_ready()


def test_provider_preflight_does_not_require_a_public_callback_url(live_settings) -> None:
    from dataclasses import replace

    settings = replace(live_settings, public_base_url=None)

    settings.require_provider_credentials_ready()


def test_callback_url_builders(live_settings) -> None:
    assert live_settings.http_url("calls/status") == "https://voice.example.test/calls/status"
    assert live_settings.websocket_url("/ws") == "wss://voice.example.test/ws"


def test_runtime_tunnel_url_is_used_when_env_url_is_blank(
    tmp_path: Path, monkeypatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("PUBLIC_BASE_URL=\n", encoding="utf-8")
    runtime_dir = tmp_path / ".runtime"
    runtime_dir.mkdir()
    (runtime_dir / "public_base_url").write_text(
        "https://temporary.trycloudflare.com\n", encoding="utf-8"
    )
    monkeypatch.delenv("PUBLIC_BASE_URL", raising=False)

    from pgai_voicebot.config import Settings

    settings = Settings.from_env(env_file=env_file)

    assert settings.public_base_url == "https://temporary.trycloudflare.com"
