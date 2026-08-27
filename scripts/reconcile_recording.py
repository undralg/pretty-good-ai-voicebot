"""Privately transcribe each channel of a completed dual-channel recording.

This is an offline QA aid. The live ConversationRelay transcript remains the
timestamped submission artifact; these files help confirm what was actually
audible on each call leg.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CALL_SID_PATTERN = re.compile(r"^CA[0-9a-fA-F]{32}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe both channels of a private Twilio recording for QA."
    )
    parser.add_argument("call_sid", help="Twilio Call SID (CA followed by 32 hex characters)")
    parser.add_argument(
        "--confirm-external-upload",
        action="store_true",
        help="Acknowledge that both recorded audio channels will be uploaded to OpenAI.",
    )
    return parser.parse_args()


def split_channel(recording_path: Path, output_path: Path, channel: int) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(recording_path),
            "-af",
            f"pan=mono|c0=c{channel}",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(output_path),
        ],
        check=True,
    )


def transcribe(client: OpenAI, audio_path: Path) -> str:
    with audio_path.open("rb") as audio_file:
        result = client.audio.transcriptions.create(
            model="gpt-transcribe",
            file=audio_file,
            language="en",
        )
    if isinstance(result, str):
        return result.strip()
    return result.text.strip()


def main() -> None:
    args = parse_args()
    if not CALL_SID_PATTERN.fullmatch(args.call_sid):
        raise SystemExit("Invalid Call SID format.")
    if not args.confirm_external_upload:
        raise SystemExit(
            "Blocked: add --confirm-external-upload only after the recording owner "
            "approves uploading both audio channels to OpenAI."
        )

    load_dotenv(PROJECT_ROOT / ".env", override=False)
    call_dir = PROJECT_ROOT / "artifacts" / "private" / args.call_sid
    recording_path = call_dir / "recording.mp3"
    if not recording_path.is_file():
        raise SystemExit(f"Recording not found: {recording_path}")

    client = OpenAI()
    with tempfile.TemporaryDirectory(prefix="pgai-recording-qa-") as temp_dir:
        temp_path = Path(temp_dir)
        for channel in (0, 1):
            audio_path = temp_path / f"channel_{channel}.wav"
            split_channel(recording_path, audio_path, channel)
            transcript = transcribe(client, audio_path)
            output_path = call_dir / f"qa_channel_{channel}_transcript.txt"
            output_path.write_text(transcript + "\n", encoding="utf-8")
            print(f"Wrote private channel-{channel} QA transcript: {output_path}")


if __name__ == "__main__":
    main()
