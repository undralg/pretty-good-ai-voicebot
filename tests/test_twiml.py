from __future__ import annotations

from xml.etree import ElementTree

from pgai_voicebot.scenarios import ScenarioRepository
from pgai_voicebot.twiml import build_conversation_relay_twiml


def test_twiml_connects_only_the_relay_and_carries_scenario(dry_settings, scenario_root) -> None:
    scenario = ScenarioRepository(scenario_root).get("S01")

    root = ElementTree.fromstring(build_conversation_relay_twiml(dry_settings, scenario))
    connect = root.find("Connect")
    relay = connect.find("ConversationRelay") if connect is not None else None

    assert connect is not None
    assert connect.attrib == {
        "action": "https://voice.example.test/relay-ended",
        "method": "POST",
    }
    assert relay is not None
    assert relay.attrib["url"] == "wss://voice.example.test/ws"
    assert relay.attrib["interruptible"] == "speech"
    assert relay.attrib["events"] == "tokens-played"
    parameters = {item.attrib["name"]: item.attrib["value"] for item in relay.findall("Parameter")}
    assert parameters["scenario_id"] == "S01"
    assert parameters["scenario_time_limit_seconds"] == str(scenario.max_duration_seconds)
    assert "+18054398008" not in build_conversation_relay_twiml(dry_settings, scenario)
