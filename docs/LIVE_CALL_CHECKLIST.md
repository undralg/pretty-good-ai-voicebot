# Live Call Checklist

> **Current status:** Live calling is complete. Twenty sequential attempts produced 19 MP3s; eleven chronological candidates are packaged. Automated tests, callbacks, transcripts, stereo/channel checks, duration checks, and silence checks pass. Calls 01–10 passed manual listening; only the read-only `call-11`, Loom recording, publication, and final submission remain pending.

Use this checklist in order. A dry run is not a substitute for a live pilot, and a live pilot is not permission to publish or submit.

## Labels

- **[BRIEF]** — explicit assessment requirement.
- **[RECOMMENDED]** — project safeguard, not an additional Pretty Good AI requirement.
- **[CHECKPOINT]** — stop for repository-owner verification or approval.

## 1. Provider and credentials checkpoint

- [ ] **[BRIEF]** Create the Athena test account for product context, and do not call the number shown on its confirmation screen.
- [ ] **[CHECKPOINT]** Confirm the Twilio account can call the assessment destination. A trial account's verified-destination restriction or trial announcement is unsuitable for the final evidence.
- [ ] **[CHECKPOINT]** Select one voice-capable originating number and record its exact E.164 form privately. Use this number for every pilot and final call.
- [ ] **[CHECKPOINT]** Accept Twilio's Predictive and Generative AI/ML Features Addendum and verify ConversationRelay access in the account.
- [ ] **[CHECKPOINT]** Confirm OpenAI API billing/access and select an available text model that supports Responses API streaming. Record the actual model ID in call metadata.
- [ ] **[CHECKPOINT]** Create a Restricted Twilio API key with only `twilio/voice/calls/create` and `twilio/voice/recordings/read` permissions.
- [ ] **[CHECKPOINT]** Create a local ignored `.env` containing `TWILIO_ACCOUNT_SID`, `TWILIO_API_KEY_SID`, `TWILIO_API_KEY_SECRET`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, `PUBLIC_BASE_URL`, `OPENAI_API_KEY`, and `OPENAI_MODEL`.
- [ ] **[RECOMMENDED]** Use the API key for outbound REST requests and recording downloads. Keep the account Auth Token only for validating Twilio's signed callbacks.
- [ ] **[RECOMMENDED]** Keep the assessment destination out of `.env`; it should be immutable in code.
- [ ] **[CHECKPOINT]** Confirm `PUBLIC_BASE_URL` serves the HTTP callback over HTTPS and the ConversationRelay endpoint over WSS.
- [ ] **[RECOMMENDED]** Verify Twilio WebSocket signature validation against the exact public WSS URL before accepting a ConversationRelay session.
- [ ] **[CHECKPOINT]** Review expected Twilio, recording, speech, and model charges. Preserve receipts outside the public repository.
- [ ] Confirm no secret value appears in terminal history, committed files, screenshots, Loom windows, or diagnostic bundles.

## 2. Dry-run gate

- [ ] Run the complete automated test suite.
- [ ] Run one representative scenario in dry-run mode with network calls disabled or mocked.
- [ ] Confirm dry-run output explicitly states that no telephone call was placed.
- [ ] Confirm the only accepted destination is `+18054398008`.
- [ ] Attempt an alternate destination and verify that the application fails before reaching Twilio.
- [ ] Confirm there is no CLI option or environment variable that silently overrides the destination.
- [ ] Replay fixture events for ConversationRelay `setup`, partial/final `prompt`, `interrupt`, and error messages.
- [ ] Confirm streamed OpenAI text is forwarded incrementally with correct spacing and one explicit final token.
- [ ] Confirm an interruption cancels or supersedes the active response rather than allowing stale speech to continue.
- [ ] Confirm scenario prompts use synthetic names, dates, medications, and identifiers only.
- [ ] Confirm the scenario has a goal, facts revealed only when appropriate, a complication, success criteria, and a bounded ending.
- [ ] Confirm artifact paths are unique and cannot overwrite a prior call.
- [ ] Confirm logs redact tokens, auth headers, and credential values.
- [ ] Record the test command, result, and Git commit in the iteration log.

Dry-run completion proves application logic only. It does not prove PSTN connectivity, speech quality, latency, recording completeness, transcription quality, or coherent turn-taking.

## 3. First live-call checkpoint

- [ ] **[CHECKPOINT]** Obtain explicit approval from the repository owner before the first live call. This action incurs cost and contacts an external service.
- [ ] Reconfirm the destination displayed by the application is exactly `+18054398008`.
- [ ] Reconfirm the originating number matches the private E.164 value selected above.
- [ ] Start only one call.
- [ ] Monitor FastAPI, Twilio, and model events without displaying credentials.
- [ ] Confirm the WebSocket `setup` event identifies the expected call and scenario.
- [ ] Listen for natural greeting behavior, reasonable latency, coherent replies, and sensible interruption handling.
- [ ] Stop the call if it enters a silence loop, repeated phrase loop, uncontrolled monologue, or incorrect destination state.

## 4. Post-call evidence gate

- [ ] Confirm Twilio reports a completed call rather than failed, busy, unanswered, or canceled.
- [ ] Download the actual recording as MP3 or OGG into a unique pilot directory.
- [ ] Open the recording locally and listen through the entire file.
- [ ] Confirm both parties are audible and the audio has no disqualifying gaps, clipping, or overlap.
- [ ] Open the transcript and compare it against the recording.
- [ ] Confirm both speakers are labeled and timestamps support later bug citations.
- [ ] Confirm scenario ID, call ID, duration, timestamps, destination, and originating-number consistency match.
- [ ] Confirm no real patient data or secret entered the recording, transcript, or metadata.
- [ ] Score coherence, turn-taking, pacing, active steering, audio clarity, and goal completion.
- [ ] Record actual cost and retain the provider receipts privately.
- [ ] Treat any evaluator output as a candidate finding until a human verifies it against the audio.

Do not count this call toward the final minimum until every final-call check in [CALL_INDEX.md](../CALL_INDEX.md) passes.

## 5. Iteration and debugging evidence

- [ ] Identify the most material observed weakness from a real pilot.
- [ ] Record the symptom, timestamp, evidence, and a testable hypothesis before changing code or prompts.
- [ ] Capture a genuine AI-assisted debugging session, including the prompts used, the proposed change, critical review, and the follow-up test.
- [ ] **[BRIEF]** Use the submitter's own voice and webcam in the debugging Loom.
- [ ] Do not reenact a fabricated bug or present a dry-run fixture as a live-call failure.
- [ ] Repeat the same or closely comparable scenario after the change.
- [ ] Preserve before-and-after evidence and note any remaining limitation.

## 6. Call batch

- [ ] **[RECOMMENDED]** Run calls sequentially so recordings, transcripts, scenario versions, and costs remain easy to match. Sequential execution is not required by the brief.
- [ ] **[RECOMMENDED]** Aim for 90–150 seconds and use a 180-second watchdog to prevent loops, silence, and runaway cost. The brief says good calls are typically one to three minutes; it does not impose this exact watchdog.
- [ ] Vary scenarios rather than changing the telephony stack between calls.
- [ ] Listen to every candidate final recording; do not validate from transcript alone.
- [ ] Keep failed, partial, or low-quality attempts in the pilot/excluded section.
- [ ] Continue until at least 10 calls independently pass the final-call acceptance checks.
- [ ] Prefer a smaller set of well-evidenced, material bugs over a long list of stylistic nitpicks.

## 7. Publication checkpoint

- [ ] **[CHECKPOINT]** Freeze live-call code and artifact contents before preparing public links.
- [ ] Inspect `git status`, the full staged diff, and every new binary file.
- [ ] Search for `.env`, API keys, auth tokens, authorization headers, account secrets, real patient data, and sensitive billing information.
- [ ] Confirm every submitted recording is a repository-local MP3/OGG, not an authenticated or expiring provider URL.
- [ ] Confirm `README.md`, `ARCHITECTURE.md`, `CALL_INDEX.md`, and `BUG_REPORT.md` no longer claim that live evidence is absent once that evidence has actually been verified.
- [ ] Remove instructional placeholders from all final bug entries and call rows.
- [ ] Record the project walkthrough Loom with the submitter's own voice and webcam.
- [ ] Keep both Looms concise and set them to public access.
- [ ] **[CHECKPOINT]** Obtain explicit approval before creating or making the GitHub repository public and before publishing the Loom links.
- [ ] Open the public repository, both Looms, every recording, and every transcript in a signed-out/incognito browser.

## 8. Final-submission checkpoint

- [ ] **[BRIEF]** Public GitHub repository link is correct and accessible.
- [ ] **[BRIEF]** Both public Loom links are correct and accessible.
- [ ] **[BRIEF]** Repository contains working Python code, setup/run instructions, the architecture explanation, at least 10 valid call recordings and transcripts, and the verified bug report.
- [ ] **[BRIEF]** Enter the exact originating phone number in E.164 format. Do not enter `+18054398008` in that field unless it is somehow also the originating number, which it should not be.
- [ ] Confirm all assessment calls used that one originating number.
- [ ] Attach or provide receipts through the requested submission path without publishing sensitive billing details.
- [ ] Confirm the repository contains no unsupported statement that dry-run or automated tests prove live call quality.
- [ ] **[CHECKPOINT]** Show the completed form to the repository owner and obtain explicit approval before final submission.
- [ ] Do not contact Pretty Good AI employees directly for support, clarification, or feedback about the assessment.

After submission, preserve the exact Git commit and public artifact links that were reviewed.
