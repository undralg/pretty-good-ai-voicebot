"""Static validation for scenarios and submission structure."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .scenarios import ScenarioRepository


@dataclass(slots=True)
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_project(project_root: Path) -> ValidationReport:
    report = ValidationReport()
    try:
        scenarios = ScenarioRepository(project_root / "scenarios").load_all()
    except Exception as exc:  # noqa: BLE001 - aggregate all validation failures for the CLI
        report.errors.append(f"Scenario validation failed: {exc}")
        scenarios = []

    if len(scenarios) < 10:
        report.errors.append(f"Expected at least 10 scenarios; found {len(scenarios)}.")
    if any("sunday" in scenario.title.lower() for scenario in scenarios):
        report.warnings.append(
            "A title mentions Sunday; do not present the brief's supplied example as a finding."
        )

    required_files = [
        "README.md",
        "ARCHITECTURE.md",
        "BUG_REPORT.md",
        "CALL_INDEX.md",
        ".env.example",
    ]
    for name in required_files:
        if not (project_root / name).exists():
            report.errors.append(f"Missing required project file: {name}")

    private_root = project_root / "artifacts" / "private"
    if any(path.name != ".gitkeep" for path in private_root.glob("*")):
        report.warnings.append("Private call artifacts exist and require manual review.")

    final_root = project_root / "artifacts" / "final"
    final_calls = sorted(path for path in final_root.glob("call-*") if path.is_dir())
    if final_calls and len(final_calls) < 10:
        report.errors.append(
            f"Expected at least 10 packaged final calls; found {len(final_calls)}."
        )
    required_artifacts = {
        "recording.mp3",
        "transcript.md",
        "metadata.json",
        "evaluation.json",
        "scenario.json",
    }
    pending_manual_review = 0
    for call_dir in final_calls:
        present = {path.name for path in call_dir.iterdir() if path.is_file()}
        missing = required_artifacts - present
        if missing:
            report.errors.append(
                f"{call_dir.name} is missing: {', '.join(sorted(missing))}."
            )
            continue
        metadata = json.loads((call_dir / "metadata.json").read_text(encoding="utf-8"))
        if metadata.get("validation_status") == "pending_manual_audio_review":
            pending_manual_review += 1
    if pending_manual_review:
        report.warnings.append(
            f"{pending_manual_review} packaged calls still require manual audio review."
        )
    return report
