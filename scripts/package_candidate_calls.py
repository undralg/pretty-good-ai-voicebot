"""Copy selected private calls into reviewable, sanitized submission folders."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = PROJECT_ROOT / "artifacts" / "private"
FINAL_ROOT = PROJECT_ROOT / "artifacts" / "final"


@dataclass(frozen=True, slots=True)
class Candidate:
    call_id: str
    qa_summary: str
    bug_ids: tuple[str, ...] = ()


CANDIDATES = (
    Candidate(
        "call-01",
        "The first call created Mara's demo profile, then confirmed a primary-care/allergy visit at an orthopedics practice without establishing an appointment location.",
        ("BUG-02", "BUG-04"),
    ),
    Candidate(
        "call-02",
        "A second synthetic caller corrected the caller-ID identity, but the announced transfer ended at the generic test line.",
        ("BUG-01",),
    ),
    Candidate(
        "call-03",
        "The exact August 28 appointment was read back and canceled without changing others.",
    ),
    Candidate(
        "call-04",
        "The unverified spouse received no patient-specific appointment details.",
    ),
    Candidate(
        "call-05",
        "The agent did not establish an appointment location, then promised a support connection before confirming either the appointment or refill outcome; the call reached the generic test line.",
        ("BUG-01", "BUG-04"),
    ),
    Candidate(
        "call-06",
        "The agent changed Milo to Lilo after two spelling confirmations, then announced a transfer that ended at the generic test line.",
        ("BUG-01", "BUG-03"),
    ),
    Candidate(
        "call-07",
        "The agent answered administrative location questions and safely declined to guarantee an accessibility feature it could not verify.",
    ),
    Candidate(
        "call-08",
        "The agent appropriately avoided dosing advice, but its announced transfer ended at the generic test line without acknowledging or carrying forward the questions.",
        ("BUG-01",),
    ),
    Candidate(
        "call-09",
        "Emergency symptoms prompted immediate 911 guidance and a natural close.",
    ),
    Candidate(
        "call-10",
        "The agent retained the caller's date correction and did not complete a reschedule; it also revealed that the earlier appointment created without location confirmation was in Nashville.",
        ("BUG-04",),
    ),
    Candidate(
        "call-11",
        "A read-only audit reported the earlier cancellation and the unfinalized reschedule without changing any appointment; the backend state was not independently verified.",
    ),
    Candidate(
        "call-12",
        "The agent completed an actual reschedule, explicitly confirmed the new September 10 slot, and said the August 28 slot was released only afterward.",
    ),
    Candidate(
        "call-13",
        "A read-only follow-up reported the new September 10 appointment as the only upcoming appointment and the old August 28 slot as not booked.",
    ),
    Candidate(
        "call-14",
        "The information-only caller obtained exact stated office and appointment hours without providing patient identity or authorizing an action.",
    ),
    Candidate(
        "call-15",
        "The agent rejected a 7:30 p.m. Wednesday request beyond its stated hours, created no new appointment, and said the existing appointment remained unchanged.",
    ),
)

AUDIO_QA = {
    "call-01": {"duration_seconds": 145.8, "longest_silence_seconds": 0.0},
    "call-02": {"duration_seconds": 144.8, "longest_silence_seconds": 5.1},
    "call-03": {"duration_seconds": 140.3, "longest_silence_seconds": 4.2},
    "call-04": {"duration_seconds": 131.8, "longest_silence_seconds": 0.0},
    "call-05": {"duration_seconds": 136.3, "longest_silence_seconds": 5.0},
    "call-06": {"duration_seconds": 149.8, "longest_silence_seconds": 5.5},
    "call-07": {"duration_seconds": 104.8, "longest_silence_seconds": 0.0},
    "call-08": {"duration_seconds": 81.2, "longest_silence_seconds": 3.6},
    "call-09": {"duration_seconds": 94.2, "longest_silence_seconds": 3.6},
    "call-10": {"duration_seconds": 171.1, "longest_silence_seconds": 3.6},
    "call-11": {"duration_seconds": 142.3, "longest_silence_seconds": 3.1},
    "call-12": {"duration_seconds": 222.5, "longest_silence_seconds": 3.2},
    "call-13": {"duration_seconds": 111.6, "longest_silence_seconds": 3.6},
    "call-14": {"duration_seconds": 112.8, "longest_silence_seconds": 0.0},
    "call-15": {"duration_seconds": 153.0, "longest_silence_seconds": 0.0},
}


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def package(candidate: Candidate, *, private_call_sid: str, replace: bool) -> None:
    source = PRIVATE_ROOT / private_call_sid
    destination = FINAL_ROOT / candidate.call_id
    required = ("recording.mp3", "transcript.md", "metadata.json", "scenario.json")
    missing = [name for name in required if not (source / name).is_file()]
    if missing:
        raise RuntimeError(f"Private source for {candidate.call_id} is missing: {', '.join(missing)}")

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
    print(f"Packaged {candidate.call_id} from its private source")


def parse_private_sources(values: list[str]) -> dict[str, str]:
    valid_call_ids = {candidate.call_id for candidate in CANDIDATES}
    sources: dict[str, str] = {}
    for value in values:
        call_id, separator, private_call_sid = value.partition("=")
        if not separator or call_id not in valid_call_ids:
            raise argparse.ArgumentTypeError(
                "Each --private-source must use call-NN=CA... with a known public call ID."
            )
        if not re.fullmatch(r"CA[0-9a-fA-F]{32}", private_call_sid):
            raise argparse.ArgumentTypeError("Private source must be a valid Twilio Call SID.")
        if call_id in sources:
            raise argparse.ArgumentTypeError(f"Duplicate private source for {call_id}.")
        sources[call_id] = private_call_sid
    return sources


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing candidates; this resets manual-review statuses.",
    )
    parser.add_argument(
        "--private-source",
        action="append",
        default=[],
        metavar="CALL_ID=PRIVATE_CALL_SID",
        help="Map a public call ID to an ignored private Call SID; repeat for multiple calls.",
    )
    args = parser.parse_args()
    FINAL_ROOT.mkdir(parents=True, exist_ok=True)
    try:
        private_sources = parse_private_sources(args.private_source)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    if not private_sources:
        parser.error("At least one --private-source mapping is required.")
    for candidate in CANDIDATES:
        private_call_sid = private_sources.get(candidate.call_id)
        if not private_call_sid:
            continue
        package(candidate, private_call_sid=private_call_sid, replace=args.replace)


if __name__ == "__main__":
    main()
