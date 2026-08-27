from pgai_voicebot.validation import validate_project


def test_project_structure_validates(project_root) -> None:
    report = validate_project(project_root)

    assert report.ok, report.errors
    assert not report.errors
    assert any("manual audio review" in warning for warning in report.warnings)
