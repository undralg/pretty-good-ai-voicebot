# Loom Recording Guide

Both videos must be public, use the submitter's own voice, and show the submitter on webcam. Do not read a script word-for-word; use these as timing cues.

## Video 1 — Project walkthrough (maximum 3 minutes)

### 0:00–0:25 — Goal and result

- Explain that the system is an automated synthetic patient calling only the assessment number.
- State the result: eleven chronological calls, three defensible bugs, and one final read-only state audit.

### 0:25–1:10 — Architecture and engineering choices

- Show `README.md` and `ARCHITECTURE.md`.
- Explain Twilio ConversationRelay, FastAPI, the OpenAI Responses API, signed callbacks, the immutable destination, dual-channel recording, and why calls ran sequentially.
- Mention that generated text is provisional until Twilio confirms what was played, which prevents interrupted speech from leaking into transcripts.

### 1:10–1:45 — Evidence and iteration

- Show `CALL_INDEX.md` and point out that calls are ordered by actual start time, beginning with Mara's profile creation.
- Show the original 180-second safeguard evolving into a configurable 240-second watchdog and scenario-specific limits.
- Explain that weak or bot-caused attempts stayed in ignored private storage rather than being presented as target-agent bugs.

### 1:45–2:35 — Strongest findings

- Show `BUG_REPORT.md`.
- Lead with the four-of-four dead-end transfer pattern.
- Show the primary-care/allergy request booked into orthopedics.
- Briefly mention the confirmed Milo-to-Lilo corruption.
- Explain that clinical non-answers, minor-account creation, and unknown demo configuration were deliberately not overclaimed.

### 2:35–3:00 — Final audit and close

- Show `call-11` in `CALL_INDEX.md`.
- Explain that it made no write action and confirmed the earlier cancellation, retained 4:00 p.m. appointment, and unfinalized September 10 discussion.
- Close with what you learned about testing stateful voice agents: verify actions across calls, separate configuration from behavior, and prefer reproducible failures over a long list of nitpicks.

## Video 2 — Genuine AI-assisted debugging

Record a real unresolved issue rather than reenacting a completed fix. The current test run passes but emits a `StarletteDeprecationWarning` involving `fastapi.testclient` and `httpx2`, which is a suitable small debugging task.

Suggested workflow:

1. Start recording before running the tests so the warning appears naturally.
2. Prompt the AI: “The suite passes, but this deprecation warning remains. Diagnose whether it comes from our code or dependency compatibility. Do not suppress the warning. Propose the smallest maintainable fix and explain the tradeoff before editing.”
3. Ask it to inspect `pyproject.toml`, the installed versions, and the affected test-client import.
4. Review its recommendation aloud and ask one follow-up about compatibility or rollback risk.
5. Authorize the minimal edit, then have it run the full test and lint suites.
6. End by showing the diff and explaining why you accepted or rejected the proposed fix.

Do not expose `.env`, API keys, account identifiers, or the ignored private artifact directory while recording either video.
