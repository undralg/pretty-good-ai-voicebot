"""Private call-artifact persistence and transcript rendering."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .scenarios import Scenario

SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{2,80}$")


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class ArtifactStore:
    def __init__(self, root: Path):
        self.root = root

    def _call_dir(self, call_sid: str) -> Path:
        if not SAFE_ID.fullmatch(call_sid):
            raise ValueError(f"Unsafe call id: {call_sid!r}")
        return self.root / call_sid

    def initialize_call(
        self,
        call_sid: str,
        scenario: Scenario,
        *,
        source_number: str | None = None,
        destination_number: str | None = None,
    ) -> Path:
        call_dir = self._call_dir(call_sid)
        call_dir.mkdir(parents=True, exist_ok=True)
        metadata_path = call_dir / "metadata.json"
        metadata: dict[str, Any] = {}
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        defaults = {
            "call_sid": call_sid,
            "scenario_id": scenario.id,
            "scenario_title": scenario.title,
            "created_at": utc_now(),
            "source_number": source_number,
            "destination_number": destination_number,
            "status": "initialized",
            "artifact_review_status": "private_unreviewed",
        }
        for key, value in defaults.items():
            if key not in metadata or metadata[key] is None:
                metadata[key] = value
        self._write_json(metadata_path, metadata)
        scenario_path = call_dir / "scenario.json"
        if not scenario_path.exists():
            self._write_json(scenario_path, scenario.model_dump(mode="json"))
        return call_dir

    def append_event(self, call_sid: str, event: dict[str, Any]) -> None:
        call_dir = self._call_dir(call_sid)
        call_dir.mkdir(parents=True, exist_ok=True)
        payload = {"timestamp": utc_now(), **event}
        with (call_dir / "transcript.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def update_metadata(self, call_sid: str, **updates: Any) -> None:
        metadata_path = self._call_dir(call_sid) / "metadata.json"
        metadata: dict[str, Any] = {}
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata.update(updates)
        metadata["updated_at"] = utc_now()
        self._write_json(metadata_path, metadata)

    def save_recording(self, call_sid: str, audio: bytes) -> Path:
        destination = self._call_dir(call_sid) / "recording.mp3"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(audio)
        self.update_metadata(call_sid, recording_file=destination.name)
        return destination

    def render_transcript(self, call_sid: str) -> Path:
        call_dir = self._call_dir(call_sid)
        source = call_dir / "transcript.jsonl"
        destination = call_dir / "transcript.md"
        lines = [f"# Call {call_sid}", ""]
        if source.exists():
            for raw_line in source.read_text(encoding="utf-8").splitlines():
                event = json.loads(raw_line)
                if event.get("type") not in {"turn", "error"}:
                    continue
                timestamp = event.get("timestamp", "")
                speaker = event.get("speaker", event.get("type", "event"))
                text = event.get("text", event.get("description", ""))
                qualifier = " (interrupted)" if event.get("interrupted") else ""
                lines.append(f"- **{timestamp} — {speaker}{qualifier}:** {text}")
        destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return destination

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        temporary.replace(path)
