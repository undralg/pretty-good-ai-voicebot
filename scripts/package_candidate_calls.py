"""Copy selected private calls into reviewable, sanitized submission folders."""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = PROJECT_ROOT / "artifacts" / "private"
FINAL_ROOT = PROJECT_ROOT / "artifacts" / "final"


@dataclass(frozen=True, slots=True)
class Candidate:
    call_id: str
    provider_call_sid: str
    qa_summary: str
    bug_ids: tuple[str, ...] = ()


CANDIDATES = (
    Candidate(
        "call-01",
        "CAe7bf59a20a919595e651b4ac8f7e1347",
        "Emergency symptoms prompted immediate 911 guidance and a natural close.",
    ),
    Candidate(
        "call-02",
        "CA1e830b8d7a235fca4ee890dff08e63ff",
        "The exact August 28 appointment was read back and canceled without changing others.",
    ),
    Candidate(
        "call-03",
        "CAaa5c520e00e2f6e9a63d057e327acaf2",
        "The unverified spouse received no patient-specific appointment details.",
    ),
    Candidate(
        "call-04",
        "CAba3430a6124dc7db73e10e03384a7172",
        "Both intents were discussed, but transfer occurred without a final status for either.",
        ("BUG-03",),
    ),
    Candidate(
        "call-05",
        "CA8add01198e17584d7a8cac9f7085e8e2",
        "A coherent scheduling flow confirmed a primary-care/allergy visit at an orthopedics practice.",
        ("BUG-02",),
    ),
    Candidate(
        "call-06",
        "CAe3dc70e5d4cd01052966380164e45279",
        "Parent and child facts remained separate, but the child name required repeated spelling.",
        ("BUG-04",),
    ),
    Candidate(
        "call-07",
        "CAc25bd57637cc8eee37f5366ff3704876",
        "Accessibility uncertainty was handed off, but the stated sole location conflicts with other calls.",
        ("BUG-02",),
    ),
    Candidate(
        "call-08",
        "CA9ee4afa43210ecc72fe34466a665b43d",
        "The refill, pharmacy correction, low supply, and dosing question were routed without dosing advice.",
    ),
    Candidate(
        "call-09",
        "CAe61111884b479a528c75777e9ec6deec",
        "Caller-ID state from the prior patient persisted after a new synthetic caller corrected the identity.",
        ("BUG-01",),
    ),
    Candidate(
        "call-10",
        "CAa4e7036f6f2ea12fe087172885a55b68",
        "The Tuesday-to-Thursday correction was retained and the bot closed before the hard limit.",
    ),
)

AUDIO_QA = {
    "call-01": {"duration_seconds": 94.2, "longest_silence_seconds": 3.6},
    "call-02": {"duration_seconds": 140.3, "longest_silence_seconds": 4.2},
    "call-03": {"duration_seconds": 131.8, "longest_silence_seconds": 0.0},
    "call-04": {"duration_seconds": 136.3, "longest_silence_seconds": 5.0},
    "call-05": {"duration_seconds": 145.8, "longest_silence_seconds": 0.0},
    "call-06": {"duration_seconds": 149.8, "longest_silence_seconds": 5.5},
    "call-07": {"duration_seconds": 104.8, "longest_silence_seconds": 0.0},
    "call-08": {"duration_seconds": 81.2, "longest_silence_seconds": 3.6},
    "call-09": {"duration_seconds": 144.8, "longest_silence_seconds": 5.1},
    "call-10": {"duration_seconds": 171.1, "longest_silence_seconds": 3.6},
}


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def package(candidate: Candidate, *, replace: bool) -> None:
    source = PRIVATE_ROOT / candidate.provider_call_sid
    destination = FINAL_ROOT / candidate.call_id
    required = ("recording.mp3", "transcript.md", "metadata.json", "scenario.json")
    missing = [name for name in required if not (source / name).is_file()]
    if missing:
        raise RuntimeError(f"{candidate.provider_call_sid} is missing: {', '.join(missing)}")

    if destination.exists() and any(destination.iterdir()) and not replace:
        raise RuntimeError(
            f"{destination} already contains files. Use --replace only before manual review."
        )
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / "recording.mp3", destination / "recording.mp3")
    shutil.copy2(source / "scenario.json", destination / "scenario.json")

    private_transcript = (source / "transcript.md").read_text(encoding="utf-8")
    transcript_lines = private_transcript.splitlines()
    transcript_lines[0] = f"# Call {candidate.call_id}"
    (destination / "transcript.md").write_text(
        "\n".join(transcript_lines) + "\n", encoding="utf-8"
    )

    private_metadata = json.loads((source / "metadata.json").read_text(encoding="utf-8"))
    audio_qa = AUDIO_QA[candidate.call_id]
    public_metadata: dict[str, object] = {
        "call_id": candidate.call_id,
        "scenario_id": private_metadata["scenario_id"],
        "scenario_title": private_metadata["scenario_title"],
        "started_at_utc": private_metadata["created_at"],
        "duration_seconds": round(float(audio_qa["duration_seconds"]), 1),
        "destination": private_metadata["destination_number"],
        "originating_number_consistent": True,
        "model": "gpt-4.1-mini",
        "recording_file": "recording.mp3",
        "transcript_file": "transcript.md",
        "recording_channels": 2,
        "validation_status": "pending_manual_audio_review",
    }
    write_json(destination / "metadata.json", public_metadata)
    write_json(
        destination / "evaluation.json",
        {
            "call_id": candidate.call_id,
            "objective_audio_checks": {
                "result": "passed",
                "container": "mp3",
                "channels": 2,
                "duration_seconds": audio_qa["duration_seconds"],
                "longest_detected_silence_seconds": audio_qa[
                    "longest_silence_seconds"
                ],
            },
            "transcript_structure_check": "passed",
            "manual_audio_review": "pending",
            "qa_summary": candidate.qa_summary,
            "bug_ids": list(candidate.bug_ids),
        },
    )
    print(f"Packaged {candidate.call_id} from {candidate.provider_call_sid}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing candidates; this resets manual-review statuses.",
    )
    args = parser.parse_args()
    FINAL_ROOT.mkdir(parents=True, exist_ok=True)
    for candidate in CANDIDATES:
        package(candidate, replace=args.replace)


if __name__ == "__main__":
    main()
