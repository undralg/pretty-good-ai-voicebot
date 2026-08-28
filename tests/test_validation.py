import json

from pgai_voicebot.validation import validate_project


def test_project_structure_validates(project_root) -> None:
    report = validate_project(project_root)

    assert report.ok, report.errors
    assert not report.errors
    assert not report.warnings


def test_packaged_calls_follow_actual_start_time(project_root) -> None:
    call_dirs = sorted((project_root / "artifacts" / "final").glob("call-*"))
    metadata = [
        json.loads((call_dir / "metadata.json").read_text(encoding="utf-8"))
        for call_dir in call_dirs
    ]

    started_at = [item["started_at_utc"] for item in metadata]
    assert started_at == sorted(started_at)
    assert metadata[0]["scenario_id"] == "S01"
