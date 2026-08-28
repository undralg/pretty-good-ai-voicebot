"""ConversationRelay session state and WebSocket protocol handling."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from dataclasses import dataclass, field
from time import monotonic
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from .artifacts import ArtifactStore
from .constants import ASSESSMENT_NUMBER
from .llm import ConversationMessage, StreamingLLM
from .prompts import add_timebox_instruction, build_patient_instructions
from .scenarios import Scenario, ScenarioRepository

TERMINAL_AGENT_PHRASES = (
    "goodbye",
    "have a great day",
    "transferring you now",
    "please stay on the line",
    "you've reached the pretty good ai test line",
)
FIXED_FAREWELL = "Thank you. Goodbye."
TIMEBOX_FAREWELL = "Thank you. I'll stop here for now. Goodbye."
FORCED_FAREWELL_RESERVE_SECONDS = 15
MODEL_CLOSEOUT_RESERVE_SECONDS = 25


def is_terminal_agent_prompt(text: str) -> bool:
    normalized = " ".join(text.lower().split())
    return any(phrase in normalized for phrase in TERMINAL_AGENT_PHRASES)


def should_force_close(*, max_duration_seconds: int, elapsed_seconds: float) -> bool:
    """Reserve the final seconds for a played farewell and normal hangup."""
    return (
        max_duration_seconds >= 150
        and elapsed_seconds
        >= max_duration_seconds - FORCED_FAREWELL_RESERVE_SECONDS
    )


@dataclass(slots=True)
class PendingAssistantTurn:
    """Generated text that is not transcript-authoritative until playback settles."""

    fragments: list[str] = field(default_factory=list)
    played_fragments: list[str] = field(default_factory=list)
    task: asyncio.Task[None] | None = None


class ConversationRelayHandler:
    def __init__(
        self,
        *,
        scenarios: ScenarioRepository,
        store: ArtifactStore,
        llm: StreamingLLM,
    ):
        self._scenarios = scenarios
        self._store = store
        self._llm = llm

    async def run(self, websocket: WebSocket) -> None:
        call_sid: str | None = None
        scenario: Scenario | None = None
        instructions: str | None = None
        history: list[ConversationMessage] = []
        pending_assistant: PendingAssistantTurn | None = None
        started_at: float | None = None
        end_after_phrase: str | None = None
        preempt_next_response = False

        async def stop_pending_response() -> bool:
            """Stop generation and report whether it was still active."""
            if not pending_assistant or not pending_assistant.task:
                return False
            was_active = not pending_assistant.task.done()
            if was_active:
                pending_assistant.task.cancel()
                with suppress(asyncio.CancelledError):
                    await pending_assistant.task
            else:
                await pending_assistant.task
            return was_active

        def finalize_pending_response(
            *, heard_text: str | None = None, interrupted: bool = False
        ) -> None:
            nonlocal pending_assistant
            if not pending_assistant or not call_sid:
                pending_assistant = None
                return
            text = (
                heard_text
                if heard_text is not None
                else (
                    "".join(pending_assistant.played_fragments).strip()
                    or "".join(pending_assistant.fragments).strip()
                )
            )
            if text:
                history.append({"role": "assistant", "content": text})
                self._store.append_event(
                    call_sid,
                    {
                        "type": "turn",
                        "speaker": "patient_bot",
                        "text": text,
                        "interrupted": interrupted,
                    },
                )
            pending_assistant = None

        try:
            while True:
                message = await websocket.receive_json()
                message_type = message.get("type")

                if message_type == "setup":
                    was_active = await stop_pending_response()
                    finalize_pending_response(interrupted=was_active)
                    call_sid, scenario, instructions = self._handle_setup(message)
                    started_at = monotonic()
                    history.clear()
                    preempt_next_response = False
                    self._store.initialize_call(
                        call_sid,
                        scenario,
                        source_number=message.get("from"),
                        destination_number=message.get("to"),
                    )
                    self._store.update_metadata(call_sid, status="relay_connected")
                    continue

                if not call_sid or not scenario or not instructions:
                    await websocket.send_json(
                        {"type": "text", "token": "", "last": True}
                    )
                    continue

                if message_type == "prompt" and message.get("last") is True:
                    user_text = str(message.get("voicePrompt", "")).strip()
                    if not user_text:
                        continue
                    was_active = await stop_pending_response()
                    if was_active:
                        preempt_next_response = True
                    finalize_pending_response(interrupted=was_active)
                    history.append({"role": "user", "content": user_text})
                    self._store.append_event(
                        call_sid,
                        {"type": "turn", "speaker": "remote_agent", "text": user_text},
                    )
                    elapsed = monotonic() - started_at if started_at is not None else 0
                    forced_farewell: str | None = None
                    if is_terminal_agent_prompt(user_text):
                        forced_farewell = FIXED_FAREWELL
                    elif should_force_close(
                        max_duration_seconds=scenario.max_duration_seconds,
                        elapsed_seconds=elapsed,
                    ):
                        forced_farewell = TIMEBOX_FAREWELL
                    if forced_farewell:
                        end_after_phrase = forced_farewell
                        preempt_next_response = False
                        pending_assistant = PendingAssistantTurn(
                            fragments=[forced_farewell]
                        )
                        await websocket.send_json(
                            {
                                "type": "text",
                                "token": forced_farewell,
                                "last": True,
                                "interruptible": True,
                                "preemptible": True,
                            }
                        )
                        continue
                    pending_assistant = PendingAssistantTurn()
                    preempt_response = preempt_next_response
                    preempt_next_response = False
                    response_instructions = instructions
                    if started_at is not None:
                        elapsed = monotonic() - started_at
                        closeout_threshold = max(
                            60,
                            scenario.max_duration_seconds
                            - MODEL_CLOSEOUT_RESERVE_SECONDS,
                        )
                        if elapsed >= closeout_threshold:
                            response_instructions = add_timebox_instruction(instructions)
                    pending_assistant.task = asyncio.create_task(
                        self._send_model_response(
                            websocket=websocket,
                            call_sid=call_sid,
                            instructions=response_instructions,
                            history=history,
                            emitted=pending_assistant.fragments,
                            preempt=preempt_response,
                        )
                    )
                    continue

                if message_type == "interrupt":
                    await stop_pending_response()
                    preempt_next_response = True
                    spoken = str(message.get("utteranceUntilInterrupt", "")).strip()
                    finalize_pending_response(heard_text=spoken, interrupted=True)
                    self._store.append_event(
                        call_sid,
                        {
                            "type": "interrupt",
                            "utterance_until_interrupt": spoken,
                            "duration_until_interrupt_ms": message.get(
                                "durationUntilInterruptMs"
                            ),
                        },
                    )
                    continue

                if message_type == "info":
                    if (
                        pending_assistant
                        and message.get("name") == "tokensPlayed"
                        and message.get("value")
                    ):
                        pending_assistant.played_fragments.append(str(message["value"]))
                    self._store.append_event(
                        call_sid,
                        {
                            "type": "relay_info",
                            "details": {
                                key: value for key, value in message.items() if key != "type"
                            },
                        },
                    )
                    played = str(message.get("value", ""))
                    if end_after_phrase and end_after_phrase in played:
                        finalize_pending_response()
                        await websocket.send_json(
                            {
                                "type": "end",
                                "handoffData": "patient-simulator-complete",
                            }
                        )
                        end_after_phrase = None
                    continue

                if message_type == "error":
                    description = str(message.get("description", "Unknown relay error"))
                    self._store.append_event(
                        call_sid, {"type": "error", "description": description}
                    )
                    self._store.update_metadata(call_sid, status="relay_error")

        except WebSocketDisconnect:
            pass
        finally:
            was_active = await stop_pending_response()
            finalize_pending_response(interrupted=was_active)
            if call_sid:
                self._store.update_metadata(call_sid, status="relay_disconnected")
                self._store.render_transcript(call_sid)

    def _handle_setup(self, message: dict[str, Any]) -> tuple[str, Scenario, str]:
        call_sid = str(message.get("callSid", ""))
        if not call_sid:
            raise ValueError("ConversationRelay setup did not include callSid.")
        destination = message.get("to")
        if destination and destination != ASSESSMENT_NUMBER:
            raise ValueError(f"Unexpected ConversationRelay destination: {destination}")
        custom_parameters = message.get("customParameters") or {}
        scenario_id = custom_parameters.get("scenario_id")
        if not scenario_id:
            raise ValueError("ConversationRelay setup did not include scenario_id.")
        scenario = self._scenarios.get(str(scenario_id))
        return call_sid, scenario, build_patient_instructions(scenario)

    async def _send_model_response(
        self,
        *,
        websocket: WebSocket,
        call_sid: str,
        instructions: str,
        history: list[ConversationMessage],
        emitted: list[str],
        preempt: bool,
    ) -> None:
        try:
            pending_token: str | None = None
            first_message = True
            async for token in self._llm.stream_reply(
                instructions=instructions, history=tuple(history)
            ):
                if not token:
                    continue
                emitted.append(token)
                if pending_token is not None:
                    payload: dict[str, Any] = {
                        "type": "text",
                        "token": pending_token,
                        "last": False,
                        "interruptible": True,
                    }
                    if first_message and preempt:
                        payload["preemptible"] = True
                    await websocket.send_json(payload)
                    first_message = False
                pending_token = token
            final_payload: dict[str, Any] = {
                "type": "text",
                "token": pending_token or "",
                "last": True,
                "interruptible": True,
            }
            if first_message and preempt:
                final_payload["preemptible"] = True
            await websocket.send_json(final_payload)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 - keep the live call responsive on model errors
            self._store.append_event(
                call_sid,
                {"type": "error", "description": f"Model stream failed: {exc}"},
            )
            fallback = "Sorry, could you repeat that?"
            emitted.append(fallback)
            await websocket.send_json(
                {
                    "type": "text",
                    "token": fallback,
                    "last": True,
                    "interruptible": True,
                }
            )
