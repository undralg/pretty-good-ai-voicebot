"""Environment-backed configuration with explicit live-call readiness checks."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

from .constants import (
    DEFAULT_CALL_TIME_LIMIT_SECONDS,
    LIVE_CALL_ACKNOWLEDGEMENT,
    MAX_CALL_TIME_LIMIT_SECONDS,
    MIN_CALL_TIME_LIMIT_SECONDS,
)

E164_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")
ACCOUNT_SID_PATTERN = re.compile(r"^AC[0-9a-fA-F]{32}$")
API_KEY_SID_PATTERN = re.compile(r"^SK[0-9a-fA-F]{32}$")


class ConfigurationError(ValueError):
    """Raised when configuration is invalid or insufficient for a live call."""


def _parse_bool(value: str | None, *, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ConfigurationError(f"Expected a boolean value, received {value!r}.")


@dataclass(frozen=True, slots=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    twilio_account_sid: str | None
    twilio_auth_token: str | None
    twilio_api_key_sid: str | None
    twilio_api_key_secret: str | None
    twilio_from_number: str | None
    public_base_url: str | None
    live_call_acknowledgement: str
    validate_twilio_signatures: bool
    call_time_limit_seconds: int
    artifact_root: Path

    @classmethod
    def from_env(cls, *, env_file: Path | None = None) -> Settings:
        load_dotenv(dotenv_path=env_file, override=False)
        raw_limit = os.getenv(
            "CALL_TIME_LIMIT_SECONDS", str(DEFAULT_CALL_TIME_LIMIT_SECONDS)
        )
        try:
            call_limit = int(raw_limit)
        except ValueError as exc:
            raise ConfigurationError("CALL_TIME_LIMIT_SECONDS must be an integer.") from exc
        if not MIN_CALL_TIME_LIMIT_SECONDS <= call_limit <= MAX_CALL_TIME_LIMIT_SECONDS:
            raise ConfigurationError(
                "CALL_TIME_LIMIT_SECONDS must be between "
                f"{MIN_CALL_TIME_LIMIT_SECONDS} and {MAX_CALL_TIME_LIMIT_SECONDS}."
            )

        public_base = os.getenv("PUBLIC_BASE_URL") or None
        if not public_base and env_file:
            runtime_url_path = env_file.parent / ".runtime" / "public_base_url"
            if runtime_url_path.is_file():
                public_base = runtime_url_path.read_text(encoding="utf-8").strip() or None
        if public_base:
            public_base = public_base.rstrip("/")

        settings = cls(
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip(),
            twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID") or None,
            twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN") or None,
            twilio_api_key_sid=os.getenv("TWILIO_API_KEY_SID") or None,
            twilio_api_key_secret=os.getenv("TWILIO_API_KEY_SECRET") or None,
            twilio_from_number=os.getenv("TWILIO_FROM_NUMBER") or None,
            public_base_url=public_base,
            live_call_acknowledgement=os.getenv("PGVOICE_ENABLE_LIVE_CALLS", "NO"),
            validate_twilio_signatures=_parse_bool(
                os.getenv("TWILIO_VALIDATE_SIGNATURES"), default=True
            ),
            call_time_limit_seconds=call_limit,
            artifact_root=Path(os.getenv("ARTIFACT_ROOT", "artifacts/private")),
        )
        settings._validate_optional_values()
        return settings

    @property
    def live_calls_enabled(self) -> bool:
        return self.live_call_acknowledgement == LIVE_CALL_ACKNOWLEDGEMENT

    def _validate_optional_values(self) -> None:
        if self.twilio_account_sid and not ACCOUNT_SID_PATTERN.fullmatch(
            self.twilio_account_sid
        ):
            raise ConfigurationError("TWILIO_ACCOUNT_SID has an invalid format.")
        if self.twilio_api_key_sid and not API_KEY_SID_PATTERN.fullmatch(
            self.twilio_api_key_sid
        ):
            raise ConfigurationError("TWILIO_API_KEY_SID has an invalid format.")
        if self.twilio_from_number and not E164_PATTERN.fullmatch(self.twilio_from_number):
            raise ConfigurationError("TWILIO_FROM_NUMBER must use E.164 format.")
        if self.public_base_url:
            parsed = urlparse(self.public_base_url)
            if parsed.scheme != "https" or not parsed.netloc:
                raise ConfigurationError("PUBLIC_BASE_URL must be a complete HTTPS URL.")
        if not self.openai_model:
            raise ConfigurationError("OPENAI_MODEL cannot be empty.")

    def require_provider_credentials_ready(self) -> None:
        missing: list[str] = []
        for env_name, value in (
            ("OPENAI_API_KEY", self.openai_api_key),
            ("TWILIO_ACCOUNT_SID", self.twilio_account_sid),
            ("TWILIO_AUTH_TOKEN", self.twilio_auth_token),
            ("TWILIO_API_KEY_SID", self.twilio_api_key_sid),
            ("TWILIO_API_KEY_SECRET", self.twilio_api_key_secret),
            ("TWILIO_FROM_NUMBER", self.twilio_from_number),
        ):
            if not value:
                missing.append(f"{env_name} is required")
        if not self.validate_twilio_signatures:
            missing.append("TWILIO_VALIDATE_SIGNATURES must be true for live calls")
        if missing:
            raise ConfigurationError("Provider preflight blocked:\n- " + "\n- ".join(missing))

    def require_live_call_ready(self) -> None:
        missing: list[str] = []
        try:
            self.require_provider_credentials_ready()
        except ConfigurationError as exc:
            missing.extend(str(exc).splitlines()[1:])
        if not self.live_calls_enabled:
            missing.append(
                "PGVOICE_ENABLE_LIVE_CALLS must equal the acknowledgement in constants.py"
            )
        if not self.public_base_url:
            missing.append("PUBLIC_BASE_URL is required")
        if missing:
            raise ConfigurationError("Live call blocked:\n- " + "\n- ".join(missing))

    def http_url(self, path: str) -> str:
        if not self.public_base_url:
            raise ConfigurationError("PUBLIC_BASE_URL is required to build callback URLs.")
        return f"{self.public_base_url}/{path.lstrip('/')}"

    def websocket_url(self, path: str) -> str:
        http_url = self.http_url(path)
        return "wss://" + http_url.removeprefix("https://")
