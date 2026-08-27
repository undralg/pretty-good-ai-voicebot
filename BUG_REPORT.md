# Bug Report

> **Verification status:** These findings are supported by preserved recordings and two-speaker transcripts, but manual audio comparison is still pending. IDs are stable for review; no finding should be called finally verified until the listening checklist is complete.

## Candidate findings

| ID | Finding | Severity | Call(s) | Reproducibility | Confidence before listening |
| --- | --- | --- | --- | --- | --- |
| BUG-01 | Caller-ID state from a prior patient persists after a new caller corrects the identity | Medium | `call-09` | 1/1 tested cross-patient call | High |
| BUG-02 | Office-location facts conflict across calls | Medium | `call-05`, `call-07`, `call-10` | 3 mutually inconsistent call contexts | High |
| BUG-03 | Transfer occurs without final status for either task | Medium | `call-04` | 1/1 multi-intent call | High |
| BUG-04 | Child name is corrupted after repeated spelling | Medium | `call-06` | 1/1 minor-patient call | Medium |

## BUG-01 — Prior patient identity persists after explicit correction

- **Severity:** Medium
- **Scenario:** `S02`
- **Call:** `call-09`
- **Recording:** [recording.mp3](artifacts/final/call-09/recording.mp3) at approximately `00:37–02:14`
- **Transcript:** [transcript.md](artifacts/final/call-09/transcript.md)
- **Confidence:** High from the transcript; confirm exact wording in audio

**Observed behavior**

The agent used caller ID to ask whether the new caller was Mara, the synthetic patient created in the preceding call. The caller explicitly said he was Eli Navarro and supplied a different full name and date of birth. The workflow continued to use the phone-number-linked record path and eventually transferred without reaching the reschedule request.

**Expected behavior**

After an explicit identity correction, the agent should either switch to a safe new-patient/alternate-caller workflow or explain that it cannot locate the second synthetic patient. It should not continue as though caller ID resolves the corrected identity.

**Why this matters**

Persistent caller-ID identity can block shared-phone households and creates a risk that details or actions are associated with the wrong person.

## BUG-02 — Contradictory office-location facts

- **Severity:** Medium
- **Calls:** `call-05`, `call-07`, `call-10`
- **Recordings:** [call-05](artifacts/final/call-05/recording.mp3), [call-07](artifacts/final/call-07/recording.mp3), [call-10](artifacts/final/call-10/recording.mp3)
- **Transcripts:** [call-05](artifacts/final/call-05/transcript.md), [call-07](artifacts/final/call-07/transcript.md), [call-10](artifacts/final/call-10/transcript.md)
- **Confidence:** High that the transcripts conflict; confirm all address words in audio

**Observed behavior**

`call-05` confirms a primary-care/allergy appointment at Pivot Point Orthopedics. `call-07` says the practice has one main location at `1234 Recovery Way, Suite 200, Austin`. `call-10` describes an existing appointment at `220 Athens Way, Nashville`. The “one main location” claim cannot be reconciled with the later Nashville appointment without information the agent did not provide.

**Expected behavior**

The agent should retrieve consistent location data, distinguish multiple offices, or state that it cannot verify the address. Accessibility guidance should be tied to the correct location.

**Why this matters**

Conflicting directions can send a patient to the wrong city and make accessibility planning unreliable.

## BUG-03 — Multi-intent transfer leaves both outcomes ambiguous

- **Severity:** Medium
- **Scenario:** `S07`
- **Call:** `call-04`
- **Recording:** [recording.mp3](artifacts/final/call-04/recording.mp3) at approximately `01:54–02:11`
- **Transcript:** [transcript.md](artifacts/final/call-04/transcript.md)
- **Confidence:** High from the transcript; confirm the distorted transfer phrase in audio

**Observed behavior**

The caller selected a Friday 4:00 p.m. appointment and reminded the agent about the separate amlodipine refill question. After asking the caller to confirm the appointment, the agent moved into a transfer. It never stated whether the appointment was booked and never clearly stated whether the refill question or both tasks were being handed off.

**Expected behavior**

Before transfer, the agent should distinguish the status of each task: booked, not booked, message submitted, or requiring support.

**Why this matters**

The patient may assume an appointment or refill action succeeded and fail to follow up.

## BUG-04 — Child name changes after two spelling confirmations

- **Severity:** Medium
- **Scenario:** `S09`
- **Call:** `call-06`
- **Recording:** [recording.mp3](artifacts/final/call-06/recording.mp3) at approximately `00:52–02:21`
- **Transcript:** [transcript.md](artifacts/final/call-06/transcript.md)
- **Confidence:** Medium until audio confirms whether “Lilo” is agent speech or transcription error

**Observed behavior**

The parent twice spelled `M-I-L-O C-H-E-N`. The agent later repeated the letters correctly, then the transcript says it could not locate “Lilo's” record. The workflow transferred without scheduling.

**Expected behavior**

Once a name has been spelled and read back correctly, downstream lookup and recap should use the confirmed value.

**Why this matters**

A corrupted dependent name can route the wrong record lookup and create an identity-association error.

## Limitations

- ConversationRelay supplies the remote-agent transcript, so unusual names and addresses can be speech-to-text errors. The linked MP3 is authoritative.
- The calls use a synthetic demo backend. Findings describe observable behavior, not the implementation or root cause.
- The supplied example bug from the challenge brief is not included.
