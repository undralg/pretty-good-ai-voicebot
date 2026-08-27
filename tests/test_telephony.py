from __future__ import annotations

import json

import pytest
import twilio.rest

from pgai_voicebot.artifacts import ArtifactStore
from pgai_voicebot.scenarios import ScenarioRepository
from pgai_voicebot.telephony import LiveCallBlocked, place_assessment_call


def test_call_is_blocked_without_explicit_execute(dry_settings, scenario_root, tmp_path) -> None:
    scenario = ScenarioRepository(scenario_root).get("S01")

    with pytest.raises(LiveCallBlocked, match="pass --execute"):
        place_assessment_call(
            dry_settings,
            scenario,
            ArtifactStore(tmp_path),
            execute=False,
        )


def test_call_client_receives_only_the_immutable_destination(
    monkeypatch, live_settings, scenario_root, tmp_path
) -> None:
    captured: dict[str, object] = {}

    class FakeCalls:
        def create(self, **kwargs):
            captured.update(kwargs)
            return type("FakeCall", (), {"sid": "CAmocked123"})()

    class FakeClient:
        def __init__(self, api_key_sid, api_key_secret, *, account_sid):
            assert api_key_sid == live_settings.twilio_api_key_sid
            assert api_key_secret == live_settings.twilio_api_key_secret
            assert account_sid == live_settings.twilio_account_sid
            self.calls = FakeCalls()

    monkeypatch.setattr(twilio.rest, "Client", FakeClient)
    scenario = ScenarioRepository(scenario_root).get("S01")
    store = ArtifactStore(tmp_path / "private")

    started = place_assessment_call(live_settings, scenario, store, execute=True)

    assert started.destination == "+18054398008"
    assert captured["to"] == "+18054398008"
    assert captured["from_"] == "+14155550123"
    assert captured["record"] is True
    assert captured["recording_channels"] == "dual"
    assert captured["recording_track"] == "both"
    assert captured["recording_status_callback_method"] == "POST"
    assert captured["recording_status_callback_event"] == ["completed", "absent"]
    assert captured["trim"] == "do-not-trim"
    metadata = json.loads(
        (tmp_path / "private" / "CAmocked123" / "metadata.json").read_text(
            encoding="utf-8"
        )
    )
    assert metadata["destination_number"] == "+18054398008"
