"""Create, verify, and store a restricted Twilio key without printing its secret."""

from __future__ import annotations

import os
from pathlib import Path

import httpx
from dotenv import dotenv_values
from twilio.rest import Client

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
NONEXISTENT_RECORDING_SID = "RE" + "0" * 32
POLICY = {
    "allow": [
        "/twilio/voice/calls/create",
        "/twilio/voice/recordings/read",
    ]
}


def replace_env_values(path: Path, updates: dict[str, str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    remaining = dict(updates)
    output: list[str] = []
    for line in lines:
        key = line.split("=", 1)[0] if "=" in line else None
        if key in remaining:
            output.append(f"{key}={remaining.pop(key)}")
        else:
            output.append(line)
    output.extend(f"{key}={value}" for key, value in remaining.items())
    temporary = path.with_suffix(".env.tmp")
    temporary.write_text("\n".join(output) + "\n", encoding="utf-8")
    os.chmod(temporary, 0o600)
    temporary.replace(path)


def main() -> int:
    values = dotenv_values(ENV_PATH)
    account_sid = values.get("TWILIO_ACCOUNT_SID")
    auth_token = values.get("TWILIO_AUTH_TOKEN")
    old_key_sid = values.get("TWILIO_API_KEY_SID")
    if not account_sid or not auth_token:
        raise RuntimeError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are required.")

    management_client = Client(account_sid, auth_token)
    created = management_client.iam.v1.new_api_key.create(
        account_sid=account_sid,
        friendly_name="pgai-voicebot-runtime",
        key_type="restricted",
        policy=POLICY,
    )
    if not created.sid or not created.secret:
        raise RuntimeError("Twilio did not return the new key's one-time credentials.")

    recording_url = (
        f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/"
        f"Recordings/{NONEXISTENT_RECORDING_SID}.json"
    )
    response = httpx.get(recording_url, auth=(created.sid, created.secret), timeout=20)
    if response.status_code != 404:
        management_client.iam.v1.api_key(created.sid).delete()
        raise RuntimeError(
            "New restricted key failed verification with HTTP "
            f"{response.status_code}; it was deleted and .env was not changed."
        )

    replace_env_values(
        ENV_PATH,
        {
            "TWILIO_API_KEY_SID": created.sid,
            "TWILIO_API_KEY_SECRET": created.secret,
        },
    )
    if old_key_sid and old_key_sid != created.sid:
        management_client.iam.v1.api_key(old_key_sid).delete()
    print("Restricted Twilio key created, verified, and stored locally; previous key removed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
