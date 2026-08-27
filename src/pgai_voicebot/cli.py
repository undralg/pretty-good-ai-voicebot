"""Command-line interface. Live calling is intentionally difficult to trigger accidentally."""

from __future__ import annotations

import argparse
from pathlib import Path

from .artifacts import ArtifactStore
from .config import Settings
from .constants import ASSESSMENT_NUMBER
from .prompts import build_patient_instructions
from .scenarios import ScenarioRepository
from .telephony import place_assessment_call
from .twiml import build_conversation_relay_twiml
from .validation import validate_project

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pgai-voicebot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-scenarios", help="List validated scenario definitions.")
    subparsers.add_parser("validate", help="Validate project structure without API calls.")

    dry_run = subparsers.add_parser("dry-run", help="Preview one call without API calls.")
    dry_run.add_argument("--scenario", required=True)

    live_call = subparsers.add_parser("live-call", help="Place the authorized assessment call.")
    live_call.add_argument("--scenario", required=True)
    live_call.add_argument(
        "--execute",
        action="store_true",
        help="Second live-call acknowledgement; still requires the environment gate.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings.from_env(env_file=PROJECT_ROOT / ".env")
    scenarios = ScenarioRepository(PROJECT_ROOT / "scenarios")

    if args.command == "list-scenarios":
        for scenario in scenarios.load_all():
            print(f"{scenario.id}: {scenario.title} ({scenario.max_duration_seconds}s max)")
        return 0

    if args.command == "validate":
        report = validate_project(PROJECT_ROOT)
        for warning in report.warnings:
            print(f"WARNING: {warning}")
        for error in report.errors:
            print(f"ERROR: {error}")
        print("Validation passed." if report.ok else "Validation failed.")
        return 0 if report.ok else 1

    scenario = scenarios.get(args.scenario)
    if args.command == "dry-run":
        print("DRY RUN ONLY — no API call will be made")
        print(f"Scenario: {scenario.id} — {scenario.title}")
        print(f"Immutable destination: {ASSESSMENT_NUMBER}")
        print(
            "Effective time limit: "
            f"{min(settings.call_time_limit_seconds, scenario.max_duration_seconds)} seconds"
        )
        if settings.public_base_url:
            print("\nTwiML preview:\n" + build_conversation_relay_twiml(settings, scenario))
        else:
            print("\nTwiML preview unavailable until PUBLIC_BASE_URL is set.")
        print("\nPatient instructions:\n" + build_patient_instructions(scenario))
        return 0

    store_root = (
        settings.artifact_root
        if settings.artifact_root.is_absolute()
        else PROJECT_ROOT / settings.artifact_root
    )
    started = place_assessment_call(
        settings,
        scenario,
        ArtifactStore(store_root),
        execute=args.execute,
    )
    print(
        f"Started {started.call_sid}: {started.scenario_id} -> {started.destination}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
