"""Outbound Twilio call initiation with immutable destination controls."""

from __future__ import annotations

from dataclasses import dataclass

from .artifacts import ArtifactStore
from .config import Settings
from .constants import ASSESSMENT_NUMBER
from .scenarios import Scenario
from .twiml import build_conversation_relay_twiml


class LiveCallBlocked(RuntimeError):
    """Raised when either live-call safety gate is not satisfied."""


@dataclass(frozen=True, slots=True)
class StartedCall:
    call_sid: str
    destination: str
    scenario_id: str


def place_assessment_call(
    settings: Settings,
    scenario: Scenario,
    store: ArtifactStore,
    *,
    execute: bool,
) -> StartedCall:
    if not execute:
        raise LiveCallBlocked("Live call blocked: pass --execute after reviewing the dry run.")
    settings.require_live_call_ready()

    # This local value is intentionally not accepted from CLI arguments or the environment.
    destination = ASSESSMENT_NUMBER
    if destination != "+18054398008":
        raise AssertionError("Assessment destination invariant changed unexpectedly.")

    from twilio.rest import Client

    twiml = build_conversation_relay_twiml(settings, scenario)
    effective_limit = min(settings.call_time_limit_seconds, scenario.max_duration_seconds)
    client = Client(
        settings.twilio_api_key_sid,
        settings.twilio_api_key_secret,
        account_sid=settings.twilio_account_sid,
    )
    call = client.calls.create(
        to=destination,
        from_=settings.twilio_from_number,
        twiml=twiml,
        record=True,
        recording_channels="dual",
        recording_track="both",
        recording_status_callback=settings.http_url("recordings/completed"),
        recording_status_callback_method="POST",
        recording_status_callback_event=["completed", "absent"],
        status_callback=settings.http_url("calls/status"),
        status_callback_method="POST",
        status_callback_event=["initiated", "ringing", "answered", "completed"],
        trim="do-not-trim",
        time_limit=effective_limit,
    )
    store.initialize_call(
        call.sid,
        scenario,
        source_number=settings.twilio_from_number,
        destination_number=destination,
    )
    store.update_metadata(call.sid, status="initiated", time_limit_seconds=effective_limit)
    return StartedCall(call_sid=call.sid, destination=destination, scenario_id=scenario.id)
