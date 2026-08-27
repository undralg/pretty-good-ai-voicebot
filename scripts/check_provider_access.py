"""Verify Twilio and OpenAI credentials without placing a telephone call."""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
from openai import AsyncOpenAI

from pgai_voicebot.config import Settings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NONEXISTENT_RECORDING_SID = "RE" + "0" * 32


async def check_twilio(settings: Settings) -> None:
    url = (
        "https://api.twilio.com/2010-04-01/Accounts/"
        f"{settings.twilio_account_sid}/Recordings/{NONEXISTENT_RECORDING_SID}.json"
    )
    async with httpx.AsyncClient(
        auth=(settings.twilio_api_key_sid, settings.twilio_api_key_secret),
        timeout=20,
    ) as client:
        response = await client.get(url)
    if response.status_code != 404:
        raise RuntimeError(
            "Twilio restricted-key preflight failed with HTTP "
            f"{response.status_code}; expected an authenticated 404 for a nonexistent recording."
        )


async def check_openai(settings: Settings) -> None:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.responses.create(
        model=settings.openai_model,
        input="Reply with OK.",
        max_output_tokens=16,
        store=False,
    )
    if not response.output_text.strip():
        raise RuntimeError("OpenAI preflight returned no text.")


async def run() -> None:
    settings = Settings.from_env(env_file=PROJECT_ROOT / ".env")
    settings.require_provider_credentials_ready()
    await check_twilio(settings)
    print("Twilio restricted API key: authenticated with recording-read permission")
    await check_openai(settings)
    print(f"OpenAI model: accessible ({settings.openai_model})")


if __name__ == "__main__":
    asyncio.run(run())
