"""Authenticated download of completed Twilio recordings."""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

import httpx

from .config import ConfigurationError, Settings


def dual_channel_mp3_url(recording_url: str) -> str:
    parts = urlsplit(recording_url)
    path = parts.path
    for suffix in (".json", ".xml", ".wav", ".mp3"):
        if path.endswith(suffix):
            path = path[: -len(suffix)]
            break
    path += ".mp3"
    return urlunsplit((parts.scheme, parts.netloc, path, "RequestedChannels=2", ""))


async def download_recording(settings: Settings, recording_url: str) -> bytes:
    if not settings.twilio_api_key_sid or not settings.twilio_api_key_secret:
        raise ConfigurationError("Twilio API key credentials are required to download recordings.")
    async with httpx.AsyncClient(
        auth=(settings.twilio_api_key_sid, settings.twilio_api_key_secret), timeout=30
    ) as client:
        response = await client.get(dual_channel_mp3_url(recording_url))
        response.raise_for_status()
        return response.content
