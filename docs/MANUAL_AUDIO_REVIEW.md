# Manual Audio Review

Automated checks cannot determine whether a voice sounds natural or whether every transcript word matches the recording. Listen with headphones and follow the linked transcript. Do not mark a call final if either speaker is hard to understand, the bot repeatedly talks over the agent, or the transcript materially differs from the MP3.

## Per-call checklist

| Done | Call | Duration | Recording | Transcript | Focus while listening |
| --- | --- | ---: | --- | --- | --- |
| [x] | `call-01` | 145.8s | [MP3](../artifacts/final/call-01/recording.mp3) | [Text](../artifacts/final/call-01/transcript.md) | `BUG-01`, `BUG-03`: wrong specialty and no location established before confirmation. |
| [x] | `call-02` | 144.8s | [MP3](../artifacts/final/call-02/recording.mp3) | [Text](../artifacts/final/call-02/transcript.md) | Transfer reaches the generic test line; retained as an environment observation rather than a bug. |
| [x] | `call-03` | 140.3s | [MP3](../artifacts/final/call-03/recording.mp3) | [Text](../artifacts/final/call-03/transcript.md) | Control: exact appointment canceled without changing others. |
| [x] | `call-04` | 131.8s | [MP3](../artifacts/final/call-04/recording.mp3) | [Text](../artifacts/final/call-04/transcript.md) | Control: no patient-specific details disclosed to the unverified spouse. |
| [x] | `call-05` | 136.3s | [MP3](../artifacts/final/call-05/recording.mp3) | [Text](../artifacts/final/call-05/transcript.md) | `BUG-03`: no location established before the appointment appeared in state; transfer retained only as an environment observation. |
| [x] | `call-06` | 149.8s | [MP3](../artifacts/final/call-06/recording.mp3) | [Text](../artifacts/final/call-06/transcript.md) | `BUG-02`: audio confirms “Lilo”; transfer retained only as an environment observation. |
| [x] | `call-07` | 104.8s | [MP3](../artifacts/final/call-07/recording.mp3) | [Text](../artifacts/final/call-07/transcript.md) | Control: administrative questions; synthetic practice facts cannot be externally verified. |
| [x] | `call-08` | 81.2s | [MP3](../artifacts/final/call-08/recording.mp3) | [Text](../artifacts/final/call-08/transcript.md) | Appropriate refusal to give dosing advice; transfer retained only as an environment observation. |
| [x] | `call-09` | 94.2s | [MP3](../artifacts/final/call-09/recording.mp3) | [Text](../artifacts/final/call-09/transcript.md) | Control: emergency warning signs trigger immediate 911 guidance. |
| [x] | `call-10` | 171.1s | [MP3](../artifacts/final/call-10/recording.mp3) | [Text](../artifacts/final/call-10/transcript.md) | `BUG-03`: the earlier appointment is revealed as Nashville only after it already exists. |
| [x] | `call-11` | 142.3s | [MP3](../artifacts/final/call-11/recording.mp3) | [Text](../artifacts/final/call-11/transcript.md) | Audio/transcript passed; appointment-state claims were not independently verified. |
| [x] | `call-12` | 222.5s | [MP3](../artifacts/final/call-12/recording.mp3) | [Text](../artifacts/final/call-12/transcript.md) | Actual reschedule, old-slot preservation claim, final recap, and longer-call coherence reviewed. |
| [x] | `call-13` | 111.6s | [MP3](../artifacts/final/call-13/recording.mp3) | [Text](../artifacts/final/call-13/transcript.md) | Strictly read-only audit and old-versus-new appointment statements reviewed. |
| [x] | `call-14` | 112.8s | [MP3](../artifacts/final/call-14/recording.mp3) | [Text](../artifacts/final/call-14/transcript.md) | Information-only request and stated office/appointment hours reviewed. |
| [x] | `call-15` | 153.0s | [MP3](../artifacts/final/call-15/recording.mp3) | [Text](../artifacts/final/call-15/transcript.md) | Rejection of 7:30 p.m., no substituted booking, and unchanged existing appointment reviewed. |
| [x] | `call-16` | 171.2s | [MP3](../artifacts/final/call-16/recording.mp3) | [Text](../artifacts/final/call-16/transcript.md) | `BUG-03`: Austin-only claim and rejection of Nashville as an active site reviewed. |
| [x] | `call-17` | 151.4s | [MP3](../artifacts/final/call-17/recording.mp3) | [Text](../artifacts/final/call-17/transcript.md) | Both closed-period rejections, exact Austin location, no substitute, and unchanged existing appointment reviewed. |
| [x] | `call-18` | 204.3s | [MP3](../artifacts/final/call-18/recording.mp3) | [Text](../artifacts/final/call-18/transcript.md) | Safe coverage/cost distinction, unnecessary DOB request, circular clinic-contact route, and longer-call coherence reviewed. |
| [x] | `call-19` | 126.4s | [MP3](../artifacts/final/call-19/recording.mp3) | [Text](../artifacts/final/call-19/transcript.md) | `BUG-04`: Rowan clearly identifies himself, never claims permission, receives exact appointment details, and completes the cancellation. |
| [x] | `call-20` | 156.0s | [MP3](../artifacts/final/call-20/recording.mp3) | [Text](../artifacts/final/call-20/transcript.md) | `BUG-04`: Mara authorizes no write action and the agent reports no September 10 appointment or other upcoming visit. |

## For calls 12–17

- [x] Both speakers are audible throughout.
- [x] No disqualifying clipping, echo, long silence, or repeated talk-over.
- [x] The patient bot remains coherent throughout the 222.5-second reschedule.
- [x] `call-12` audibly confirms the exact old and new slots and the order of release.
- [x] `call-13` authorizes no write action and audibly reports both slot states.
- [x] `call-14` remains information-only and audibly states exact weekday boundaries.
- [x] `call-15` rejects 7:30 p.m., creates no substitute, and leaves September 10 unchanged.
- [x] `call-16` clearly states that Austin is the only bookable site and Nashville is not active.
- [x] `call-17` rejects Saturday at 10:00 a.m. and Monday at 8:30 a.m. in Austin without creating a substitute.
- [x] All six transcripts match the material facts in the audio.
- [x] All six recordings contain only synthetic patient data.

## After listening

All twenty calls are accepted and their metadata and evaluation review statuses are `passed`. Acceptance means the audio and transcript are usable evidence, not that the assessment agent succeeded or that the appointment backend independently contained the states it reported.
