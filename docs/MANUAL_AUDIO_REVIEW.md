# Manual Audio Review

Automated checks cannot determine whether a voice sounds natural or whether every transcript word matches the recording. Listen with headphones and follow the linked transcript. Do not mark a call final if either speaker is hard to understand, the bot repeatedly talks over the agent, or the transcript materially differs from the MP3.

## Per-call checklist

| Done | Call | Duration | Recording | Transcript | Focus while listening |
| --- | --- | ---: | --- | --- | --- |
| [x] | `call-01` | 145.8s | [MP3](../artifacts/final/call-01/recording.mp3) | [Text](../artifacts/final/call-01/transcript.md) | `BUG-02`: primary-care/allergy intent is confirmed at an orthopedics practice. |
| [x] | `call-02` | 144.8s | [MP3](../artifacts/final/call-02/recording.mp3) | [Text](../artifacts/final/call-02/transcript.md) | `BUG-01`: announced transfer reaches the generic test line; retain the shared-number limitation. |
| [x] | `call-03` | 140.3s | [MP3](../artifacts/final/call-03/recording.mp3) | [Text](../artifacts/final/call-03/transcript.md) | Control: exact appointment canceled without changing others. |
| [x] | `call-04` | 131.8s | [MP3](../artifacts/final/call-04/recording.mp3) | [Text](../artifacts/final/call-04/transcript.md) | Control: no patient-specific details disclosed to the unverified spouse. |
| [x] | `call-05` | 136.3s | [MP3](../artifacts/final/call-05/recording.mp3) | [Text](../artifacts/final/call-05/transcript.md) | `BUG-01`: appointment and refill statuses remain unresolved before the dead-end transfer. |
| [x] | `call-06` | 149.8s | [MP3](../artifacts/final/call-06/recording.mp3) | [Text](../artifacts/final/call-06/transcript.md) | `BUG-01`, `BUG-03`: audio confirms “Lilo,” followed by the dead-end transfer. |
| [x] | `call-07` | 104.8s | [MP3](../artifacts/final/call-07/recording.mp3) | [Text](../artifacts/final/call-07/transcript.md) | Control: administrative questions; synthetic practice facts cannot be externally verified. |
| [x] | `call-08` | 81.2s | [MP3](../artifacts/final/call-08/recording.mp3) | [Text](../artifacts/final/call-08/transcript.md) | `BUG-01`: appropriate refusal to give dosing advice, followed by a dead-end transfer. |
| [x] | `call-09` | 94.2s | [MP3](../artifacts/final/call-09/recording.mp3) | [Text](../artifacts/final/call-09/transcript.md) | Control: emergency warning signs trigger immediate 911 guidance. |
| [x] | `call-10` | 171.1s | [MP3](../artifacts/final/call-10/recording.mp3) | [Text](../artifacts/final/call-10/transcript.md) | Control: correction is retained; no completed reschedule is claimed. |
| [x] | `call-11` | 142.3s | [MP3](../artifacts/final/call-11/recording.mp3) | [Text](../artifacts/final/call-11/transcript.md) | Audio/transcript passed; appointment-state claims were not independently verified. |
| [ ] | `call-12` | 222.5s | [MP3](../artifacts/final/call-12/recording.mp3) | [Text](../artifacts/final/call-12/transcript.md) | Verify the actual reschedule, old-slot preservation claim, final recap, and longer-call coherence. |
| [ ] | `call-13` | 111.6s | [MP3](../artifacts/final/call-13/recording.mp3) | [Text](../artifacts/final/call-13/transcript.md) | Verify the strictly read-only audit and the old-versus-new appointment statements. |

## For calls 12–13

- [ ] Both speakers are audible throughout.
- [ ] No disqualifying clipping, echo, long silence, or repeated talk-over.
- [ ] The patient bot remains coherent throughout the 222.5-second reschedule.
- [ ] `call-12` audibly confirms the exact old and new slots and the order of release.
- [ ] `call-13` authorizes no write action and audibly reports both slot states.
- [ ] Both transcripts match the material facts in the audio.
- [ ] Both recordings contain only synthetic patient data.

## After listening

If the calls pass, change their metadata and evaluation review statuses to `passed`. This still will not independently verify that the appointment backend contained the states the agent reported.

Calls 01–11 are already accepted. Acceptance means the audio and transcript are usable evidence, not that the assessment agent succeeded.
