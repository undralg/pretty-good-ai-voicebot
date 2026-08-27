"""FastAPI application for ConversationRelay and Twilio callbacks."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response, WebSocket

from .artifacts import ArtifactStore
from .config import Settings
from .llm import OpenAIResponsesLLM, StreamingLLM
from .recordings import download_recording
from .relay import ConversationRelayHandler
from .scenarios import ScenarioRepository
from .security import validate_twilio_signature

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_app(
    settings: Settings | None = None,
    *,
    llm_factory: Callable[[], StreamingLLM] | None = None,
    scenario_root: Path | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env(env_file=PROJECT_ROOT / ".env")
    scenarios = ScenarioRepository(scenario_root or PROJECT_ROOT / "scenarios")
    store = ArtifactStore(
        settings.artifact_root
        if settings.artifact_root.is_absolute()
        else PROJECT_ROOT / settings.artifact_root
    )
    llm_factory = llm_factory or (lambda: OpenAIResponsesLLM(settings))

    application = FastAPI(title="Pretty Good AI Patient Simulator", version="0.1.0")

    @application.get("/health")
    async def health() -> dict[str, object]:
        return {
            "ok": True,
            "live_calls_enabled": settings.live_calls_enabled,
            "signature_validation": settings.validate_twilio_signatures,
            "scenario_count": len(scenarios.load_all()),
        }

    @application.websocket("/ws")
    async def relay_websocket(websocket: WebSocket) -> None:
        signature = websocket.headers.get("x-twilio-signature")
        signature_url = settings.websocket_url("ws") if settings.public_base_url else str(websocket.url)
        if not validate_twilio_signature(
            settings, url=signature_url, signature=signature, params={}
        ):
            await websocket.close(code=1008, reason="Invalid Twilio signature")
            return
        await websocket.accept()
        try:
            llm = llm_factory()
            await ConversationRelayHandler(
                scenarios=scenarios, store=store, llm=llm
            ).run(websocket)
        except ValueError as exc:
            store_error = str(exc)
            await websocket.close(code=1008, reason=store_error[:120])

    async def verified_form(request: Request, callback_path: str) -> dict[str, str]:
        form = {key: str(value) for key, value in (await request.form()).multi_items()}
        signature = request.headers.get("x-twilio-signature")
        signature_url = (
            settings.http_url(callback_path)
            if settings.public_base_url
            else str(request.url)
        )
        if not validate_twilio_signature(
            settings, url=signature_url, signature=signature, params=form
        ):
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")
        return form

    @application.post("/calls/status")
    async def call_status(request: Request) -> dict[str, bool]:
        form = await verified_form(request, "calls/status")
        call_sid = form.get("CallSid")
        if call_sid:
            store.update_metadata(
                call_sid,
                status=form.get("CallStatus", "unknown"),
                call_duration=form.get("CallDuration"),
            )
        return {"ok": True}

    @application.post("/recordings/completed")
    async def recording_completed(request: Request) -> dict[str, bool]:
        form = await verified_form(request, "recordings/completed")
        call_sid = form.get("CallSid")
        recording_status = form.get("RecordingStatus")
        if not call_sid:
            raise HTTPException(status_code=400, detail="Missing CallSid in recording callback")
        if recording_status == "absent":
            store.update_metadata(
                call_sid,
                recording_status="absent",
                recording_error_code=form.get("RecordingErrorCode"),
            )
            store.render_transcript(call_sid)
            return {"ok": True}

        recording_url = form.get("RecordingUrl")
        if not recording_url:
            raise HTTPException(status_code=400, detail="Missing recording callback fields")
        audio = await download_recording(settings, recording_url)
        store.save_recording(call_sid, audio)
        store.update_metadata(
            call_sid,
            recording_status=recording_status or "completed",
            recording_sid=form.get("RecordingSid"),
            recording_channels=form.get("RecordingChannels"),
            recording_duration=form.get("RecordingDuration"),
        )
        store.render_transcript(call_sid)
        return {"ok": True}

    @application.post("/relay-ended")
    async def relay_ended(request: Request) -> Response:
        await verified_form(request, "relay-ended")
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response><Hangup/></Response>',
            media_type="application/xml",
        )

    return application


app = create_app()
