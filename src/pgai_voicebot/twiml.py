"""Minimal, testable TwiML generation without dynamic destination input."""

from __future__ import annotations

from xml.etree.ElementTree import Element, SubElement, tostring

from .config import Settings
from .scenarios import Scenario


def build_conversation_relay_twiml(settings: Settings, scenario: Scenario) -> str:
    response = Element("Response")
    connect = SubElement(
        response,
        "Connect",
        {"action": settings.http_url("relay-ended"), "method": "POST"},
    )
    relay = SubElement(
        connect,
        "ConversationRelay",
        {
            "url": settings.websocket_url("ws"),
            "language": "en-US",
            "interruptible": "speech",
            "interruptSensitivity": "medium",
            "reportInputDuringAgentSpeech": "speech",
            "events": "tokens-played",
        },
    )
    SubElement(relay, "Parameter", {"name": "scenario_id", "value": scenario.id})
    SubElement(
        relay,
        "Parameter",
        {
            "name": "scenario_time_limit_seconds",
            "value": str(scenario.max_duration_seconds),
        },
    )
    return '<?xml version="1.0" encoding="UTF-8"?>' + tostring(
        response, encoding="unicode", short_empty_elements=True
    )
