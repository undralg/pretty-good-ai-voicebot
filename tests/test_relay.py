from __future__ import annotations

import asyncio

import pytest
from fastapi import WebSocketDisconnect

from pgai_voicebot.artifacts import ArtifactStore
from pgai_voicebot.llm import MockStreamingLLM
from pgai_voicebot.relay import ConversationRelayHandler, is_terminal_agent_prompt
from pgai_voicebot.scenarios import ScenarioRepository


class FakeWebSocket:
    def __init__(
        self,
        messages: list[dict[str, object]],
        *,
        delays_before_receive: list[float] | None = None,
    ):
        self._messages = list(messages)
        self._delays = list(delays_before_receive or [0.0] * len(messages))
        self.sent: list[dict[str, object]] = []

    async def receive_json(self) -> dict[str, object]:
        if self._messages:
            delay = self._delays.pop(0)
            if delay:
                await asyncio.sleep(delay)
            return self._messages.pop(0)
        await asyncio.sleep(0.02)
        raise WebSocketDisconnect()

    async def send_json(self, payload: dict[str, object]) -> None:
        self.sent.append(payload)


@pytest.mark.parametrize(
    "prompt",
    [
        "Goodbye.",
        "Have a great day.",
        "Please stay on the line. Transferring you now.",
        "Hello. You've reached the Pretty Good AI test line.",
    ],
)
def test_terminal_agent_prompts_are_detected(prompt) -> None:
    assert is_terminal_agent_prompt(prompt)


@pytest.mark.asyncio
async def test_relay_streams_terminated_text_and_writes_both_sides(tmp_path, scenario_root) -> None:
    websocket = FakeWebSocket(
        [
            {
                "type": "setup",
                "callSid": "CArelay123",
                "from": "+14155550123",
                "to": "+18054398008",
                "customParameters": {"scenario_id": "S01"},
            },
            {
                "type": "prompt",
                "voicePrompt": "How can I help you today?",
                "last": True,
            },
        ]
    )
    store = ArtifactStore(tmp_path / "private")
    handler = ConversationRelayHandler(
        scenarios=ScenarioRepository(scenario_root),
        store=store,
        llm=MockStreamingLLM(["I need a morning appointment, please."]),
    )

    await handler.run(websocket)  # type: ignore[arg-type]

    assert websocket.sent
    assert websocket.sent[-1]["type"] == "text"
    assert websocket.sent[-1]["last"] is True
    assert websocket.sent[-1]["token"] == "please."
    assert all("preemptible" not in message for message in websocket.sent)
    transcript = (tmp_path / "private" / "CArelay123" / "transcript.md").read_text(
        encoding="utf-8"
    )
    assert "remote_agent" in transcript
    assert "How can I help you today?" in transcript
    assert "patient_bot" in transcript
    assert "I need a morning appointment, please." in transcript


@pytest.mark.asyncio
async def test_tokens_played_are_transcript_authoritative(tmp_path, scenario_root) -> None:
    websocket = FakeWebSocket(
        [
            {
                "type": "setup",
                "callSid": "CAplayed123",
                "to": "+18054398008",
                "customParameters": {"scenario_id": "S01"},
            },
            {
                "type": "prompt",
                "voicePrompt": "How can I help?",
                "last": True,
            },
            {
                "type": "info",
                "name": "tokensPlayed",
                "value": "Only what was heard.",
            },
        ],
        delays_before_receive=[0.0, 0.0, 0.03],
    )
    handler = ConversationRelayHandler(
        scenarios=ScenarioRepository(scenario_root),
        store=ArtifactStore(tmp_path / "private"),
        llm=MockStreamingLLM(["Generated words that were not all played."]),
    )

    await handler.run(websocket)  # type: ignore[arg-type]

    transcript = (tmp_path / "private" / "CAplayed123" / "transcript.md").read_text(
        encoding="utf-8"
    )
    assert "Only what was heard." in transcript
    assert "Generated words that were not all played." not in transcript


@pytest.mark.asyncio
async def test_relay_rejects_an_unexpected_destination(tmp_path, scenario_root) -> None:
    websocket = FakeWebSocket(
        [
            {
                "type": "setup",
                "callSid": "CAbadtarget",
                "to": "+14155550199",
                "customParameters": {"scenario_id": "S01"},
            }
        ]
    )
    handler = ConversationRelayHandler(
        scenarios=ScenarioRepository(scenario_root),
        store=ArtifactStore(tmp_path),
        llm=MockStreamingLLM(),
    )

    with pytest.raises(ValueError, match="Unexpected ConversationRelay destination"):
        await handler.run(websocket)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_explicit_goodbye_uses_fixed_farewell_without_restarting_goal(
    tmp_path, scenario_root
) -> None:
    websocket = FakeWebSocket(
        [
            {
                "type": "setup",
                "callSid": "CAgoodbye123",
                "to": "+18054398008",
                "customParameters": {"scenario_id": "S04"},
            },
            {"type": "prompt", "voicePrompt": "Goodbye.", "last": True},
            {
                "type": "info",
                "name": "tokensPlayed",
                "value": "Thank you. Goodbye.",
            },
        ]
    )

    class FailingLLM:
        async def stream_reply(self, *, instructions, history):
            del instructions, history
            raise AssertionError("The model must not run after an explicit goodbye.")
            yield "unreachable"

    handler = ConversationRelayHandler(
        scenarios=ScenarioRepository(scenario_root),
        store=ArtifactStore(tmp_path / "private"),
        llm=FailingLLM(),
    )

    await handler.run(websocket)  # type: ignore[arg-type]

    assert websocket.sent == [
        {
            "type": "text",
            "token": "Thank you. Goodbye.",
            "last": True,
            "interruptible": True,
            "preemptible": True,
        },
        {
            "type": "end",
            "handoffData": "patient-simulator-complete",
        },
    ]
    transcript = (
        tmp_path / "private" / "CAgoodbye123" / "transcript.md"
    ).read_text(encoding="utf-8")
    assert "Thank you. Goodbye." in transcript


@pytest.mark.asyncio
async def test_interrupt_cancels_stale_generation_and_records_spoken_fragment(
    tmp_path, scenario_root
) -> None:
    websocket = FakeWebSocket(
        [
            {
                "type": "setup",
                "callSid": "CAinterrupt123",
                "to": "+18054398008",
                "customParameters": {"scenario_id": "S08"},
            },
            {
                "type": "prompt",
                "voicePrompt": "Let me repeat that callback number.",
                "last": True,
            },
            {
                "type": "interrupt",
                "utteranceUntilInterrupt": "The number is",
                "durationUntilInterruptMs": 420,
            },
            {
                "type": "prompt",
                "voicePrompt": "Sorry, the last digit is six, not five.",
                "last": True,
            },
        ],
        delays_before_receive=[0.0, 0.0, 0.01, 0.0],
    )

    class InterruptibleLLM:
        def __init__(self) -> None:
            self.calls = 0

        async def stream_reply(self, *, instructions, history):
            del instructions, history
            self.calls += 1
            if self.calls == 1:
                yield "The number is "
                await asyncio.Event().wait()
                yield "stale tail that must never play"
            else:
                yield "Correct, the final digit is six."

    handler = ConversationRelayHandler(
        scenarios=ScenarioRepository(scenario_root),
        store=ArtifactStore(tmp_path / "private"),
        llm=InterruptibleLLM(),
    )

    await handler.run(websocket)  # type: ignore[arg-type]

    tokens = "".join(str(message.get("token", "")) for message in websocket.sent)
    assert "stale tail" not in tokens
    assert "Correct, the final digit is six." in tokens
    correction_messages = [
        message
        for message in websocket.sent
        if "Correct" in str(message.get("token", ""))
    ]
    assert correction_messages[0]["preemptible"] is True
    events = (
        tmp_path / "private" / "CAinterrupt123" / "transcript.jsonl"
    ).read_text(encoding="utf-8")
    assert '"type": "interrupt"' in events
    assert '"utterance_until_interrupt": "The number is"' in events
    assert '"text": "The number is"' in events
    transcript = (
        tmp_path / "private" / "CAinterrupt123" / "transcript.md"
    ).read_text(encoding="utf-8")
    assert "patient_bot (interrupted)" in transcript
    assert "stale tail" not in transcript
