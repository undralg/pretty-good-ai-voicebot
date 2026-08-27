from __future__ import annotations

from pathlib import Path

import pytest

from pgai_voicebot.config import Settings
from pgai_voicebot.constants import LIVE_CALL_ACKNOWLEDGEMENT

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture
def scenario_root(project_root: Path) -> Path:
    return project_root / "scenarios"


@pytest.fixture
def dry_settings(tmp_path: Path) -> Settings:
    return Settings(
        openai_api_key=None,
        openai_model="gpt-4.1-mini",
        twilio_account_sid=None,
        twilio_auth_token=None,
        twilio_api_key_sid=None,
        twilio_api_key_secret=None,
        twilio_from_number=None,
        public_base_url="https://voice.example.test",
        live_call_acknowledgement="NO",
        validate_twilio_signatures=False,
        call_time_limit_seconds=180,
        artifact_root=tmp_path / "artifacts",
    )


@pytest.fixture
def live_settings(tmp_path: Path) -> Settings:
    return Settings(
        openai_api_key="test-openai-key",
        openai_model="gpt-4.1-mini",
        twilio_account_sid="test-account-sid",
        twilio_auth_token="test-twilio-token",
        twilio_api_key_sid="test-api-key-sid",
        twilio_api_key_secret="test-api-key-secret",
        twilio_from_number="+14155550123",
        public_base_url="https://voice.example.test",
        live_call_acknowledgement=LIVE_CALL_ACKNOWLEDGEMENT,
        validate_twilio_signatures=True,
        call_time_limit_seconds=180,
        artifact_root=tmp_path / "artifacts",
    )
