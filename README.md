# Pretty Good AI Voice Bot

Python automated-patient simulator for the Pretty Good AI engineering challenge.

> **Current status:** The live voice stack is implemented, tested, and published at [github.com/undralg/pretty-good-ai-voicebot](https://github.com/undralg/pretty-good-ai-voicebot). Twenty-nine sequential attempts produced 28 recordings; twenty chronological calls are packaged with dual-channel MP3s, two-speaker transcripts, immutable scenario snapshots, metadata, and evaluations. All twenty passed manual audio/transcript review. The latest linked pair records a spouse disclosure/cancellation and a read-only call confirming that the cancellation persisted. Appointment states, locations, and practice hours remain agent-reported rather than independently inspected.

## What it does

The bot calls only the assessment line at `+18054398008`, acts as a synthetic patient, and steers toward a scenario goal while responding naturally to the assessment agent. Twenty authored scenarios cover scheduling, rescheduling, cancellation, refill safety, urgent symptoms, privacy, multiple intents, correction handling, parent/child identity separation, accessibility, insurance grounding, location consistency, office-hours consistency, and cross-call state integrity.

No real patient data is used. The destination cannot be supplied through the CLI or environment, and live execution requires two separate acknowledgements.

## Architecture

Twilio Programmable Voice creates the outbound call and connects it to FastAPI with `<Connect><ConversationRelay>`. ConversationRelay handles PSTN audio, speech recognition, speech synthesis, and barge-in. FastAPI validates signed Twilio HTTP/WSS traffic, loads a YAML patient scenario, and streams `gpt-4.1-mini` Responses API text deltas back to Twilio. A restricted Twilio API key is used for call creation and recording reads; the account Auth Token is used only to verify callbacks.

Generated text is provisional until playback. `tokensPlayed` records what the patient side actually heard, `utteranceUntilInterrupt` repairs interrupted turns, and replacement talk cycles preempt stale queued speech. Explicit transfer/goodbye phrases and near-limit closeout are deterministic. Each call stores an immutable scenario snapshot, dual-channel MP3, JSONL event ledger, rendered transcript, and metadata. See [ARCHITECTURE.md](ARCHITECTURE.md).

Official references:

- [Twilio ConversationRelay WebSocket messages](https://www.twilio.com/docs/voice/conversationrelay/websocket-messages)
- [Twilio ConversationRelay TwiML](https://www.twilio.com/docs/voice/twiml/connect/conversationrelay)
- [OpenAI GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini)

## Evidence

- [Call index](CALL_INDEX.md) — twenty selected recordings and transcripts in actual chronological order
- [Bug report](BUG_REPORT.md) — evidence-backed candidates, with manual-audio status stated
- [Capability matrix](docs/CAPABILITY_MATRIX.md) — separates assessment requirements, broader product claims, and unknown test-line configuration
- [Manual audio review](docs/MANUAL_AUDIO_REVIEW.md) — final human listening checklist
- [Scenario suite](scenarios/) — synthetic inputs and expected behavior

Objective QA confirmed that every selected MP3 is stereo, both channels carry non-silent audio, durations are 81–223 seconds, and the longest detected silence is 5.5 seconds. These checks do not replace listening.

## Local setup

Requirements: Python 3.12, `ffmpeg`, `cloudflared`, a paid Twilio project with ConversationRelay enabled, one voice-capable originating number, and a funded OpenAI API project.

```bash
make install
cp .env.example .env
```

Populate the ignored `.env`:

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
TWILIO_ACCOUNT_SID=
TWILIO_API_KEY_SID=
TWILIO_API_KEY_SECRET=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=
TWILIO_VALIDATE_SIGNATURES=true
CALL_TIME_LIMIT_SECONDS=240
ARTIFACT_ROOT=artifacts/private
```

`TWILIO_API_KEY_SID` and `TWILIO_API_KEY_SECRET` should belong to a restricted key with only call-create and recording-read permissions. `TWILIO_AUTH_TOKEN` remains necessary because Twilio signs callbacks with the account token.

## Test and run

```bash
# No paid calls.
make test
make lint
make validate
make dry-run

# Read-only provider credential check; no telephone call.
make preflight

# Terminal 1: signed HTTPS/WSS callback endpoint.
make live-stack

# Terminal 2: paid external action to the immutable assessment number.
# PGVOICE_ENABLE_LIVE_CALLS must first equal the exact acknowledgement
# documented in src/pgai_voicebot/constants.py.
.venv/bin/pgai-voicebot live-call --scenario S01 --execute
```

There is deliberately no `--to` option. Calls are run sequentially so status callbacks, recordings, transcripts, and scenario versions cannot be mixed. The brief describes full calls as typically one to three minutes rather than imposing a hard maximum. The project therefore uses a configurable 240-second watchdog while individual scenarios may select shorter limits; this watchdog and sequential execution are project safeguards, not extra Pretty Good AI requirements.

## Tests

The automated suite covers:

- immutable destination and dual live-call gates;
- scenario schema and configurable 240-second watchdog;
- TwiML generation and signed HTTP/WSS callbacks;
- restricted-key call/recording paths;
- streaming token termination and spacing;
- barge-in cancellation, `tokensPlayed`, and stale-buffer preemption;
- deterministic transfer/goodbye and graceful end-session messages;
- callback ordering, absent recordings, scenario snapshots, and artifact paths.

Current local result: **48 tests passed** and Ruff passed.

## Artifact handling

`artifacts/private/` is ignored and contains all attempts, including excluded failures. `scripts/package_candidate_calls.py` copies an explicit chronological allowlist into `artifacts/final/`, removes the source number and provider Call SID from metadata, and marks every selection `pending_manual_audio_review`. It never promotes calls by globbing or by provider status alone.

The transcripts and audio may still contain the dedicated Twilio originating number when the assessment agent says it aloud. That disclosure was reviewed and explicitly approved before public publication; it is a dedicated challenge number, not a personal phone number.
