from __future__ import annotations

import json

from fastapi.testclient import TestClient
from twilio.request_validator import RequestValidator

from pgai_voicebot.app import create_app
from pgai_voicebot.llm import MockStreamingLLM


def test_signed_status_callback_is_accepted(live_settings, scenario_root) -> None:
    app = create_app(
        live_settings,
        llm_factory=lambda: MockStreamingLLM(),
        scenario_root=scenario_root,
    )
    url = "https://voice.example.test/calls/status"
    form = {"CallSid": "CAsigned123", "CallStatus": "completed", "CallDuration": "61"}
    signature = RequestValidator(live_settings.twilio_auth_token).compute_signature(url, form)

    with TestClient(app) as client:
        response = client.post(
            "/calls/status",
            data=form,
            headers={"X-Twilio-Signature": signature},
        )

    assert response.status_code == 200
    metadata = json.loads(
        (live_settings.artifact_root / "CAsigned123" / "metadata.json").read_text(
            encoding="utf-8"
        )
    )
    assert metadata["status"] == "completed"
    assert metadata["call_duration"] == "61"


def test_signed_websocket_handshake_streams_a_reply(live_settings, scenario_root) -> None:
    app = create_app(
        live_settings,
        llm_factory=lambda: MockStreamingLLM(["A short test reply."]),
        scenario_root=scenario_root,
    )
    signature = RequestValidator(live_settings.twilio_auth_token).compute_signature(
        "wss://voice.example.test/ws", {}
    )

    with TestClient(app) as client, client.websocket_connect(
        "/ws", headers={"X-Twilio-Signature": signature}
    ) as websocket:
        websocket.send_json(
            {
                "type": "setup",
                "callSid": "CAwebsocket123",
                "to": "+18054398008",
                "customParameters": {"scenario_id": "S01"},
            }
        )
        websocket.send_json(
            {
                "type": "prompt",
                "voicePrompt": "How may I help?",
                "last": True,
            }
        )
        messages = []
        while not messages or messages[-1]["last"] is not True:
            messages.append(websocket.receive_json())

    assert "".join(message["token"] for message in messages) == "A short test reply."
    assert messages[-1]["token"] == "reply."


def test_absent_recording_is_logged_without_downloading(dry_settings, scenario_root) -> None:
    app = create_app(
        dry_settings,
        llm_factory=lambda: MockStreamingLLM(),
        scenario_root=scenario_root,
    )

    with TestClient(app) as client:
        response = client.post(
            "/recordings/completed",
            data={
                "CallSid": "CAabsent123",
                "RecordingStatus": "absent",
                "RecordingErrorCode": "31005",
            },
        )

    assert response.status_code == 200
    metadata = json.loads(
        (dry_settings.artifact_root / "CAabsent123" / "metadata.json").read_text(
            encoding="utf-8"
        )
    )
    assert metadata["recording_status"] == "absent"
    assert metadata["recording_error_code"] == "31005"
    assert not (dry_settings.artifact_root / "CAabsent123" / "recording.mp3").exists()
