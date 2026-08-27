from __future__ import annotations

import pytest

from pgai_voicebot.cli import build_parser, main


def test_live_call_cli_has_no_destination_argument() -> None:
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(
            ["live-call", "--scenario", "S01", "--to", "+14155550199", "--execute"]
        )


def test_dry_run_never_requires_credentials(monkeypatch, capsys) -> None:
    for name in (
        "OPENAI_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_FROM_NUMBER",
        "PUBLIC_BASE_URL",
    ):
        monkeypatch.delenv(name, raising=False)

    assert main(["dry-run", "--scenario", "S01"]) == 0
    output = capsys.readouterr().out
    assert "DRY RUN ONLY" in output
    assert "Immutable destination: +18054398008" in output
    assert "Patient instructions:" in output
