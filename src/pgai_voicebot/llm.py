"""Streaming language-model adapters."""

from __future__ import annotations

import asyncio
import re
from collections.abc import AsyncIterator, Sequence
from typing import Protocol

from .config import ConfigurationError, Settings

ConversationMessage = dict[str, str]


class StreamingLLM(Protocol):
    async def stream_reply(
        self, *, instructions: str, history: Sequence[ConversationMessage]
    ) -> AsyncIterator[str]: ...


class OpenAIResponsesLLM:
    """OpenAI Responses API adapter that yields text deltas as they arrive."""

    def __init__(self, settings: Settings):
        if not settings.openai_api_key:
            raise ConfigurationError("OPENAI_API_KEY is required for a model-backed call.")
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def stream_reply(
        self, *, instructions: str, history: Sequence[ConversationMessage]
    ) -> AsyncIterator[str]:
        stream = await self._client.responses.create(
            model=self._model,
            instructions=instructions,
            input=list(history),
            max_output_tokens=160,
            store=False,
            stream=True,
        )
        async for event in stream:
            if event.type == "response.output_text.delta" and event.delta:
                yield event.delta


class MockStreamingLLM:
    """Deterministic adapter for local WebSocket tests and demos."""

    def __init__(self, responses: Sequence[str] | None = None):
        self._responses = list(
            responses
            or ["Thanks. I would like to work through this request one step at a time."]
        )

    async def stream_reply(
        self, *, instructions: str, history: Sequence[ConversationMessage]
    ) -> AsyncIterator[str]:
        del instructions, history
        response = self._responses.pop(0) if self._responses else "Thank you. Goodbye."
        for token in re.findall(r"\S+\s*", response):
            await asyncio.sleep(0)
            yield token
