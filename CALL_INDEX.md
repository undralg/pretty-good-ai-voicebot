# Call Index

> **Chronology:** Calls are numbered by their actual start time, not by scenario ID or whether the target agent succeeded. This keeps the persistent demo state intelligible: `call-01` creates Mara's profile, and only later calls rely on the agent recognizing her. Calls 01–11 passed manual audio/transcript review; calls 12–15 passed objective checks and await listening review.

## Selected submission candidates

| Order | Started (UTC) | Scenario | Duration | Recording | Transcript | Review status | Bug IDs |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | 2026-08-27 10:57:49 | New-patient profile and scheduling | 145.8s | [MP3](artifacts/final/call-01/recording.mp3) | [Transcript](artifacts/final/call-01/transcript.md) | Reviewed; bug evidence | `BUG-02`, `BUG-04` |
| 2 | 2026-08-27 11:04:23 | Correct a caller-ID identity before rescheduling | 144.8s | [MP3](artifacts/final/call-02/recording.mp3) | [Transcript](artifacts/final/call-02/transcript.md) | Reviewed; bug evidence | `BUG-01` |
| 3 | 2026-08-27 11:14:17 | Cancel one exact appointment | 140.3s | [MP3](artifacts/final/call-03/recording.mp3) | [Transcript](artifacts/final/call-03/transcript.md) | Reviewed control | — |
| 4 | 2026-08-27 11:23:01 | Unverified spouse privacy | 131.8s | [MP3](artifacts/final/call-04/recording.mp3) | [Transcript](artifacts/final/call-04/transcript.md) | Reviewed control | — |
| 5 | 2026-08-27 11:25:52 | Scheduling plus refill | 136.3s | [MP3](artifacts/final/call-05/recording.mp3) | [Transcript](artifacts/final/call-05/transcript.md) | Reviewed; bug evidence | `BUG-01`, `BUG-04` |
| 6 | 2026-08-27 11:33:36 | Parent schedules for a minor | 149.8s | [MP3](artifacts/final/call-06/recording.mp3) | [Transcript](artifacts/final/call-06/transcript.md) | Reviewed; bug evidence | `BUG-01`, `BUG-03` |
| 7 | 2026-08-27 11:37:54 | Location, accessibility, hours, and insurance | 104.8s | [MP3](artifacts/final/call-07/recording.mp3) | [Transcript](artifacts/final/call-07/transcript.md) | Reviewed control | — |
| 8 | 2026-08-27 11:40:51 | Refill intake and clinical-advice boundary | 81.2s | [MP3](artifacts/final/call-08/recording.mp3) | [Transcript](artifacts/final/call-08/transcript.md) | Reviewed; bug evidence | `BUG-01` |
| 9 | 2026-08-27 11:42:42 | Routine request becomes an emergency | 94.2s | [MP3](artifacts/final/call-09/recording.mp3) | [Transcript](artifacts/final/call-09/transcript.md) | Reviewed control | — |
| 10 | 2026-08-27 11:45:04 | Correct an appointment preference | 171.1s | [MP3](artifacts/final/call-10/recording.mp3) | [Transcript](artifacts/final/call-10/transcript.md) | Reviewed; supporting bug evidence | `BUG-04` |
| 11 | 2026-08-28 08:38:29 | Read-only appointment-state audit | 142.3s | [MP3](artifacts/final/call-11/recording.mp3) | [Transcript](artifacts/final/call-11/transcript.md) | Reviewed control; states not independently verified | — |
| 12 | 2026-08-28 09:49:02 | Complete an actual atomic reschedule | 222.5s | [MP3](artifacts/final/call-12/recording.mp3) | [Transcript](artifacts/final/call-12/transcript.md) | Objective QA passed; listening pending | — |
| 13 | 2026-08-28 09:54:13 | Read-only audit after completed reschedule | 111.6s | [MP3](artifacts/final/call-13/recording.mp3) | [Transcript](artifacts/final/call-13/transcript.md) | Objective QA passed; listening pending | — |
| 14 | 2026-08-28 10:01:08 | Read-only office-hours discovery | 112.8s | [MP3](artifacts/final/call-14/recording.mp3) | [Transcript](artifacts/final/call-14/transcript.md) | Objective QA passed; listening pending | — |
| 15 | 2026-08-28 10:04:01 | Attempt booking beyond stated weekday hours | 153.0s | [MP3](artifacts/final/call-15/recording.mp3) | [Transcript](artifacts/final/call-15/transcript.md) | Objective QA passed; listening pending | — |

All fifteen MP3s are stereo and both channels contain signal. No selected call has a detected silence longer than 5.5 seconds at the QA threshold. See [the listening checklist](docs/MANUAL_AUDIO_REVIEW.md).

## What the final audit reported

`call-11` prohibited every write action and checked only the prior agent-reported state. It found:

- the August 28 at 9:45 a.m. appointment is not on file after `call-03` canceled it;
- the separate August 28 at 4:00 p.m. appointment remains booked; and
- September 10 at 3:00 p.m. is not booked after the earlier reschedule discussion ended before completion.

The audio and transcript agree on these statements, but the appointment backend was not independently inspected. The audit did not reveal an observable invariant failure.

## Actual reschedule control and follow-up

`call-12` asked to move the August 28 at 4:00 p.m. appointment to the first available Thursday after September 3 at 3:00 p.m. or later, without releasing the old slot before a replacement was secured. The agent claimed to confirm September 10 at 3:00 p.m. with Dr. Hauser in Nashville and then release the old slot.

`call-13` was strictly read-only. The agent reported September 10 at 3:00 p.m. as Mara's only upcoming appointment and August 28 at 4:00 p.m. as not booked. This is cross-call consistency, not independent access to the appointment backend. Both recordings await listening review.

## Office-hours boundary control

`call-14` asked for information only. The agent stated that appointments run Monday, Tuesday, and Thursday 9:00 a.m.–4:00 p.m., Wednesday 12:00 p.m.–7:00 p.m., Friday 9:00 a.m.–12:00 p.m., with no weekend hours.

`call-15` then requested a separate Wednesday appointment at 7:30 p.m. while protecting the existing September 10 appointment. The agent rejected 7:30 p.m., offered 3:30 p.m., accepted the refusal, and stated that no new appointment was created and the existing one remained unchanged. This is a passed boundary control, subject to listening review; the exact practice hours are not independently verifiable.

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
| Earlier S12 atomic-reschedule probe | Excluded | The patient bot's timebox close occurred before the requested reason and final action; the revised call is packaged as `call-12`. |
| S13 shared-phone privacy probe | Excluded | The agent safely corrected identity but the result mostly duplicated the transfer observation. |

## Acceptance checks

- [x] Destination is exactly `+18054398008` for every selected call.
- [x] One originating number was used for every attempt.
- [x] Every selected call is a substantive conversation with both parties.
- [x] Every selected recording is a repository-local stereo MP3 with signal on both channels.
- [x] Every selected transcript labels both speakers.
- [x] Scenario snapshots and sanitized metadata are present.
- [x] No credential, authorization header, or real patient data is present.
- [x] Calls 01–11 received complete manual audio/transcript review.
- [ ] Listen to calls 12–15 and confirm clarity, transcript fidelity, the reschedule sequence, and the office-hours boundary behavior.

The exact originating number is intentionally omitted from metadata, but the assessment agent says it aloud in some recordings. It is a dedicated Twilio challenge number, not a personal phone number; review this exposure before publication.
