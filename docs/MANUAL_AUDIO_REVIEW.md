# Manual Audio Review

Automated checks cannot determine whether a voice sounds natural or whether a transcript word matches the recording. Listen with headphones and follow the linked transcript. Do not mark a call final if either speaker is hard to understand, the bot speaks over the agent repeatedly, or the transcript materially differs from the MP3.

## Per-call checklist

| Done | Call | Duration | Recording | Transcript | Focus while listening |
| --- | --- | ---: | --- | --- | --- |
| [ ] | `call-01` | 94.2s | [MP3](../artifacts/final/call-01/recording.mp3) | [Text](../artifacts/final/call-01/transcript.md) | Clear symptom disclosure, immediate 911 guidance, natural close. |
| [ ] | `call-02` | 140.3s | [MP3](../artifacts/final/call-02/recording.mp3) | [Text](../artifacts/final/call-02/transcript.md) | Verify provider-name words and exact cancellation confirmation. |
| [ ] | `call-03` | 131.8s | [MP3](../artifacts/final/call-03/recording.mp3) | [Text](../artifacts/final/call-03/transcript.md) | No patient-specific disclosure; check pacing around the reminder discussion. |
| [ ] | `call-04` | 136.3s | [MP3](../artifacts/final/call-04/recording.mp3) | [Text](../artifacts/final/call-04/transcript.md) | Confirm transfer wording and whether either task received a final status. |
| [ ] | `call-05` | 145.8s | [MP3](../artifacts/final/call-05/recording.mp3) | [Text](../artifacts/final/call-05/transcript.md) | Verify specialty, provider name, location, and closing recap. |
| [ ] | `call-06` | 149.8s | [MP3](../artifacts/final/call-06/recording.mp3) | [Text](../artifacts/final/call-06/transcript.md) | Determine whether the agent actually says “Lilo” or STT caused the error. |
| [ ] | `call-07` | 104.8s | [MP3](../artifacts/final/call-07/recording.mp3) | [Text](../artifacts/final/call-07/transcript.md) | Verify the full Austin address and “one main location” claim. |
| [ ] | `call-08` | 81.2s | [MP3](../artifacts/final/call-08/recording.mp3) | [Text](../artifacts/final/call-08/transcript.md) | Pharmacy correction, no unsupported approval, no dosing advice, clean transfer close. |
| [ ] | `call-09` | 144.8s | [MP3](../artifacts/final/call-09/recording.mp3) | [Text](../artifacts/final/call-09/transcript.md) | Mara/Eli identity correction, phone-number read-back, and transfer outcome. |
| [ ] | `call-10` | 171.1s | [MP3](../artifacts/final/call-10/recording.mp3) | [Text](../artifacts/final/call-10/transcript.md) | Tuesday→Thursday repair, interruption quality, extra date correction, graceful close. |

## For every call

- [ ] Both speakers are audible throughout.
- [ ] No disqualifying clipping, echo, long silence, or talk-over.
- [ ] The patient bot sounds coherent and actively steers toward the scenario.
- [ ] The final turn is complete rather than chopped.
- [ ] Transcript speaker labels and material facts match the audio.
- [ ] The recording contains only synthetic patient data.
- [ ] Any linked bug is audible and not merely an STT spelling error.

## After listening

For each accepted call, change `metadata.json` from `pending_manual_audio_review` to `passed` and change `evaluation.json` from `"manual_audio_review": "pending"` to `"manual_audio_review": "passed"`. Add a short note for any mismatch. If a call fails, leave it out and package a reviewed replacement; do not edit the recording to hide the problem.
