from __future__ import annotations

import json

import pytest

from pgai_voicebot.artifacts import ArtifactStore
from pgai_voicebot.scenarios import ScenarioRepository


def test_artifact_store_writes_private_evidence(tmp_path, scenario_root) -> None:
    scenario = ScenarioRepository(scenario_root).get("S01")
    store = ArtifactStore(tmp_path / "private")

    call_dir = store.initialize_call(
        "CAtest123",
        scenario,
        source_number="+14155550123",
        destination_number="+18054398008",
    )
    store.append_event(
        "CAtest123",
        {"type": "turn", "speaker": "patient_bot", "text": "Hello there."},
    )
    store.save_recording("CAtest123", b"not-real-audio")
    transcript = store.render_transcript("CAtest123")

    metadata = json.loads((call_dir / "metadata.json").read_text(encoding="utf-8"))
    scenario_snapshot = json.loads(
        (call_dir / "scenario.json").read_text(encoding="utf-8")
    )
    assert metadata["scenario_id"] == "S01"
    assert scenario_snapshot["id"] == "S01"
    assert scenario_snapshot["title"] == scenario.title
    assert metadata["artifact_review_status"] == "private_unreviewed"
    assert metadata["recording_file"] == "recording.mp3"
    assert (call_dir / "recording.mp3").read_bytes() == b"not-real-audio"
    assert "patient_bot" in transcript.read_text(encoding="utf-8")


def test_artifact_store_rejects_path_traversal(tmp_path) -> None:
    store = ArtifactStore(tmp_path)

    with pytest.raises(ValueError, match="Unsafe call id"):
        store.append_event("../escape", {"type": "error", "description": "no"})


def test_initialize_call_repairs_metadata_created_by_an_early_callback(
    tmp_path, scenario_root
) -> None:
    scenario = ScenarioRepository(scenario_root).get("S01")
    store = ArtifactStore(tmp_path / "private")
    store.update_metadata("CArace123", status="ringing")

    store.initialize_call(
        "CArace123",
        scenario,
        source_number="+14155550123",
        destination_number="+18054398008",
    )

    metadata = json.loads(
        (tmp_path / "private" / "CArace123" / "metadata.json").read_text(
            encoding="utf-8"
        )
    )
    assert metadata["status"] == "ringing"
    assert metadata["scenario_id"] == "S01"
    assert metadata["destination_number"] == "+18054398008"


def test_initialize_call_does_not_rewrite_existing_scenario_snapshot(
    tmp_path, scenario_root
) -> None:
    scenario = ScenarioRepository(scenario_root).get("S01")
    store = ArtifactStore(tmp_path / "private")
    call_dir = store.initialize_call("CAstable123", scenario)
    snapshot_path = call_dir / "scenario.json"
    original = snapshot_path.read_text(encoding="utf-8")

    changed = scenario.model_copy(update={"title": "A later scenario revision"})
    store.initialize_call("CAstable123", changed)

    assert snapshot_path.read_text(encoding="utf-8") == original
