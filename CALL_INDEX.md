# Call Index

> **Current status:** Ten calls are packaged and passed structural plus objective audio-signal checks. Every row remains `pending_manual_audio_review` until a human listens to the complete MP3 against its transcript.

## Selected submission candidates

| Order | Call | Scenario | Duration | Recording | Transcript | Objective QA | Bug IDs |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | `call-01` | Emergency escalation | 94.2s | [MP3](artifacts/final/call-01/recording.mp3) | [Transcript](artifacts/final/call-01/transcript.md) | Passed; listen pending | — |
| 2 | `call-02` | Exact appointment cancellation | 140.3s | [MP3](artifacts/final/call-02/recording.mp3) | [Transcript](artifacts/final/call-02/transcript.md) | Passed; listen pending | — |
| 3 | `call-03` | Unverified spouse privacy | 131.8s | [MP3](artifacts/final/call-03/recording.mp3) | [Transcript](artifacts/final/call-03/transcript.md) | Passed; listen pending | — |
| 4 | `call-04` | Scheduling plus refill | 136.3s | [MP3](artifacts/final/call-04/recording.mp3) | [Transcript](artifacts/final/call-04/transcript.md) | Passed; listen pending | `BUG-03` |
| 5 | `call-05` | New-patient scheduling | 145.8s | [MP3](artifacts/final/call-05/recording.mp3) | [Transcript](artifacts/final/call-05/transcript.md) | Passed; listen pending | `BUG-02` |
| 6 | `call-06` | Parent schedules minor | 149.8s | [MP3](artifacts/final/call-06/recording.mp3) | [Transcript](artifacts/final/call-06/transcript.md) | Passed; listen pending | `BUG-04` |
| 7 | `call-07` | Accessibility/location | 104.8s | [MP3](artifacts/final/call-07/recording.mp3) | [Transcript](artifacts/final/call-07/transcript.md) | Passed; listen pending | `BUG-02` |
| 8 | `call-08` | Refill and dosing boundary | 81.2s | [MP3](artifacts/final/call-08/recording.mp3) | [Transcript](artifacts/final/call-08/transcript.md) | Passed; listen pending | — |
| 9 | `call-09` | Cross-patient caller-ID state | 144.8s | [MP3](artifacts/final/call-09/recording.mp3) | [Transcript](artifacts/final/call-09/transcript.md) | Passed; listen pending | `BUG-01` |
| 10 | `call-10` | Correction and barge-in | 171.1s | [MP3](artifacts/final/call-10/recording.mp3) | [Transcript](artifacts/final/call-10/transcript.md) | Passed; listen pending | — |

All ten MP3s are stereo, both channels contain signal, and no selected call has a detected silence longer than 5.5 seconds at the QA threshold. See [the listening checklist](docs/MANUAL_AUDIO_REVIEW.md) before changing any validation status to passed.

## Excluded attempts

Excluded recordings remain only in ignored private storage; they are not linked as submission evidence.

| Scenario | Status | Exclusion reason |
| --- | --- | --- |
| S02 retest | Excluded | Hit the 180-second watchdog before final confirmation. |
| S04 pilot | Excluded | The bot restarted its refill request after the target said goodbye. |
| S05 pilot | Excluded | Reached the 120-second scenario limit immediately after emergency instructions. |
| S08 pilot | Excluded | Hit the 180-second watchdog mid-confirmation. |
| S10 insurance follow-up | Excluded | Interrupted speech leaked into the next greeting before the buffer fix. |
| S06 final validation | Excluded | Temporary tunnel outage produced a long silence and no recording callback. |

## Acceptance checks

- [x] Destination is exactly `+18054398008` for every selected call.
- [x] One originating number was used for every attempt.
- [x] Every selected call is 1–3 minutes and has substantive turns from both parties.
- [x] Every selected recording is a repository-local stereo MP3.
- [x] Every selected transcript labels both speakers.
- [x] Scenario snapshots and sanitized metadata are present.
- [x] No credential, Auth header, or real patient data is present.
- [ ] Listen to each complete MP3 and confirm both parties, pacing, clipping, overlap, and transcript fidelity.
- [ ] Confirm each bug candidate against the recording.
- [ ] Change `validation_status` and `manual_audio_review` only after those checks.

The exact originating number is intentionally omitted from metadata, but the assessment agent says it aloud in some recordings. It is a dedicated Twilio challenge number, not a personal phone number; review this exposure before publication.
