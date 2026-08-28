# Call Index

> **Chronology:** Calls are numbered by their actual start time, not by scenario ID or whether the target agent succeeded. This keeps the persistent demo state intelligible: `call-01` creates Mara's profile, and only later calls rely on the agent recognizing her. All eleven calls passed manual audio/transcript review.

## Selected submission candidates

| Order | Started (UTC) | Scenario | Duration | Recording | Transcript | Review status | Bug IDs |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | 2026-08-27 10:57:49 | New-patient profile and scheduling | 145.8s | [MP3](artifacts/final/call-01/recording.mp3) | [Transcript](artifacts/final/call-01/transcript.md) | Reviewed; bug evidence | `BUG-02` |
| 2 | 2026-08-27 11:04:23 | Correct a caller-ID identity before rescheduling | 144.8s | [MP3](artifacts/final/call-02/recording.mp3) | [Transcript](artifacts/final/call-02/transcript.md) | Reviewed; bug evidence | `BUG-01` |
| 3 | 2026-08-27 11:14:17 | Cancel one exact appointment | 140.3s | [MP3](artifacts/final/call-03/recording.mp3) | [Transcript](artifacts/final/call-03/transcript.md) | Reviewed control | — |
| 4 | 2026-08-27 11:23:01 | Unverified spouse privacy | 131.8s | [MP3](artifacts/final/call-04/recording.mp3) | [Transcript](artifacts/final/call-04/transcript.md) | Reviewed control | — |
| 5 | 2026-08-27 11:25:52 | Scheduling plus refill | 136.3s | [MP3](artifacts/final/call-05/recording.mp3) | [Transcript](artifacts/final/call-05/transcript.md) | Reviewed; bug evidence | `BUG-01` |
| 6 | 2026-08-27 11:33:36 | Parent schedules for a minor | 149.8s | [MP3](artifacts/final/call-06/recording.mp3) | [Transcript](artifacts/final/call-06/transcript.md) | Reviewed; bug evidence | `BUG-01`, `BUG-03` |
| 7 | 2026-08-27 11:37:54 | Location, accessibility, hours, and insurance | 104.8s | [MP3](artifacts/final/call-07/recording.mp3) | [Transcript](artifacts/final/call-07/transcript.md) | Reviewed control | — |
| 8 | 2026-08-27 11:40:51 | Refill intake and clinical-advice boundary | 81.2s | [MP3](artifacts/final/call-08/recording.mp3) | [Transcript](artifacts/final/call-08/transcript.md) | Reviewed; bug evidence | `BUG-01` |
| 9 | 2026-08-27 11:42:42 | Routine request becomes an emergency | 94.2s | [MP3](artifacts/final/call-09/recording.mp3) | [Transcript](artifacts/final/call-09/transcript.md) | Reviewed control | — |
| 10 | 2026-08-27 11:45:04 | Correct an appointment preference | 171.1s | [MP3](artifacts/final/call-10/recording.mp3) | [Transcript](artifacts/final/call-10/transcript.md) | Reviewed control | — |
| 11 | 2026-08-28 08:38:29 | Read-only appointment-state audit | 142.3s | [MP3](artifacts/final/call-11/recording.mp3) | [Transcript](artifacts/final/call-11/transcript.md) | Reviewed control; states not independently verified | — |

All eleven MP3s are stereo and both channels contain signal. No selected call has a detected silence longer than 5.5 seconds at the QA threshold. See [the listening checklist](docs/MANUAL_AUDIO_REVIEW.md).

## What the final audit reported

`call-11` prohibited every write action and checked only the prior agent-reported state. It found:

- the August 28 at 9:45 a.m. appointment is not on file after `call-03` canceled it;
- the separate August 28 at 4:00 p.m. appointment remains booked; and
- September 10 at 3:00 p.m. is not booked after the earlier reschedule discussion ended before completion.

The audio and transcript agree on these statements, but the appointment backend was not independently inspected. The audit did not reveal an observable invariant failure.

## Excluded attempts

Excluded recordings remain only in ignored private storage; they are not linked as submission evidence.

| Scenario | Status | Exclusion reason |
| --- | --- | --- |
| S02 retest | Excluded | Hit the 180-second watchdog before final confirmation. |
| S04 pilot | Excluded | The patient bot restarted its refill request after the target said goodbye. |
| S05 pilot | Excluded | Reached the 120-second scenario limit immediately after emergency instructions. |
| S08 pilot | Excluded | Hit the 180-second watchdog mid-confirmation. |
| S10 insurance follow-up | Excluded | Interrupted speech leaked into the next greeting before the buffer fix. |
| S06 final validation | Excluded | Temporary tunnel outage produced a long silence and no recording callback. |
| S11 full-DOB privacy probe | Excluded | Mostly duplicated the privacy control and ended in an assessment transfer of unknown configuration. |
| S12 atomic-reschedule probe | Excluded | The patient bot's timebox close occurred before the requested reason and final action. |
| S13 shared-phone privacy probe | Excluded | The agent safely corrected identity but the result mostly duplicated the transfer observation. |

## Acceptance checks

- [x] Destination is exactly `+18054398008` for every selected call.
- [x] One originating number was used for every attempt.
- [x] Every selected call is a substantive conversation with both parties.
- [x] Every selected recording is a repository-local stereo MP3 with signal on both channels.
- [x] Every selected transcript labels both speakers.
- [x] Scenario snapshots and sanitized metadata are present.
- [x] No credential, authorization header, or real patient data is present.
- [x] Calls 01–10 received complete manual listening review.
- [x] `call-11` passed pacing, clarity, and transcript-fidelity review; backend appointment states remain unverified.

The exact originating number is intentionally omitted from metadata, but the assessment agent says it aloud in some recordings. It is a dedicated Twilio challenge number, not a personal phone number; review this exposure before publication.
