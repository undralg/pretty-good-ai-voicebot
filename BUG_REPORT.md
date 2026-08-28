# Bug Report

> **Evidence standard:** Findings are limited to capabilities named in the assessment, caller-visible failures, or outcomes the agent explicitly claimed to complete. Calls 01–10 were manually reviewed against their audio on August 27, 2026. Call 11 is a read-only control that passed structural and dual-channel audio checks but still awaits the submitter's listening review. The report describes observable behavior and does not infer which backend component caused it.

## Confirmed findings

| ID | Finding | Severity | Call(s) | Reproducibility | Confidence |
| --- | --- | --- | --- | --- | --- |
| BUG-01 | Transfer paths repeatedly terminate at the generic test line without completing the handoff | High | `call-02`, `call-05`, `call-06`, `call-08` | 4/4 tested transfer paths | High for caller-visible behavior; transfer configuration is unknown |
| BUG-02 | A primary-care/allergy request is confirmed at an orthopedics practice without disclosing the specialty mismatch | High | `call-01` | 1/1 tested new-patient booking | High |
| BUG-03 | A child's name changes from Milo to Lilo after two spelling confirmations | Medium | `call-06` | 1/1 tested dependent lookup | High; confirmed in audio |

## BUG-01 — Transfer paths repeatedly end at a dead-end test line

- **Severity:** High
- **Calls:** `call-02`, `call-05`, `call-06`, `call-08`
- **Recordings:** [call-02](artifacts/final/call-02/recording.mp3), [call-05](artifacts/final/call-05/recording.mp3), [call-06](artifacts/final/call-06/recording.mp3), [call-08](artifacts/final/call-08/recording.mp3)
- **Transcripts:** [call-02](artifacts/final/call-02/transcript.md), [call-05](artifacts/final/call-05/transcript.md), [call-06](artifacts/final/call-06/transcript.md), [call-08](artifacts/final/call-08/transcript.md)
- **Reproduction rate:** Four of four packaged calls in which the agent offered, promised, or initiated a transfer

**Observed behavior**

Across four different workflows, the agent offered, promised, or initiated a connection to support, but the next voice was the generic message, “Hello. You've reached the Pretty Good AI test line,” followed by goodbye. No staff member or continuing support workflow appeared.

- In `call-02`, the transfer interrupts a corrected rescheduling request after the caller has supplied a second synthetic identity.
- In `call-05`, the agent had promised to connect the refill request to patient support. After an unclear transition phrase, neither task receives a final status and the generic test-line message begins.
- In `call-06`, the agent transfers after failing to locate the child's record; the promised patient-support assistance never occurs.
- In `call-08`, the agent transfers immediately after a refill-status and dosing question, without acknowledging what must be handed to a clinician or pharmacist.

**Expected behavior**

If a real handoff is available, the caller should reach the named destination and the unresolved reason should carry forward. If the assessment environment intentionally has no live destination, the agent should say that support is unavailable in the test environment and give an accurate next step rather than promise a transfer that immediately disconnects.

**Why this matters**

Transfer is the fallback for requests the automation cannot safely complete. A failure in that path affects scheduling, account access, and clinical-question routing and can leave the patient believing that follow-up is underway when it is not.

**Limitation**

The assessment does not document its transfer endpoint. The result could be caused by test-line configuration rather than the conversational agent itself, and the exact transition phrase in `call-05` is distorted. The reproducible caller-visible failure is still valid; the report does not assign an internal root cause.

## BUG-02 — Primary-care request is booked into orthopedics

- **Severity:** High
- **Scenario:** `S01`
- **Call:** `call-01`
- **Recording:** [recording.mp3](artifacts/final/call-01/recording.mp3) at approximately `00:56–02:05`
- **Transcript:** [transcript.md](artifacts/final/call-01/transcript.md)
- **Confidence:** High

**Observed behavior**

The caller asks for a routine new-patient appointment “to establish primary care and discuss recurring seasonal allergies.” The agent repeats that intent, then confirms an appointment with Dr. Bricker at Pivot Point Orthopedics. It does not explain that the practice is orthopedic, ask whether the caller has a musculoskeletal concern, or warn that the offered specialty may not match the request.

**Expected behavior**

The agent should match the visit reason to an appropriate appointment type and specialty. If the test practice offers only orthopedics, it should state that limitation and avoid presenting the slot as a suitable primary-care/allergy appointment.

**Why this matters**

An apparently successful booking can send a patient to the wrong specialty, delay care, and consume an appointment that cannot address the stated reason for visit.

## BUG-03 — Confirmed child name is corrupted before lookup

- **Severity:** Medium
- **Scenario:** `S09`
- **Call:** `call-06`
- **Recording:** [recording.mp3](artifacts/final/call-06/recording.mp3) at approximately `00:52–02:21`
- **Transcript:** [transcript.md](artifacts/final/call-06/transcript.md)
- **Confidence:** High; manual listening confirms the agent says “Lilo”

**Observed behavior**

The parent twice spells `M-I-L-O C-H-E-N`. The agent reads the letters back correctly, but later says it cannot locate “Lilo's” record before initiating the unsuccessful transfer.

**Expected behavior**

Once a name has been spelled and confirmed, the lookup and every later recap should use that confirmed value.

**Why this matters**

Corrupting a dependent's name can cause a false record-not-found result or associate a request with the wrong patient.

## Controls and observations intentionally not reported as bugs

- `call-03` canceled only the intended 9:45 a.m. appointment. The read-only `call-11` later confirmed that it is absent, the separate 4:00 p.m. appointment remains booked, and the unfinalized September 10 slot is absent.
- `call-04` appropriately withheld appointment details from an unverified spouse.
- `call-08` appropriately avoided individualized dosing advice. The reported defect is the failed handoff path, not the refusal to answer the clinical question.
- `call-09` appropriately abandoned routine scheduling and gave immediate emergency guidance after synthetic stroke warning signs.
- Automatic creation of a minor's record, the demo-assigned birthdate, exact privacy-verification policy, SMS delivery, and the generic transfer destination are not documented assessment-line capabilities.
- Cross-call location differences and the omitted September 10 option are not included because practice configuration and backend availability cannot be independently verified.
- Caller-ID carryover is not included because the patient bot later confirmed that Mara's number was also Eli's, preventing clean attribution to the assessment agent.

## General limitations

- ConversationRelay supplies the remote-agent transcript, so unusual names can be speech-to-text errors. The linked MP3 is authoritative.
- The calls use synthetic data and a demo backend. Findings describe the recorded behavior, not production patient data or the implementation's internal cause.
- Public product descriptions help identify likely workflows but do not prove that every module is enabled on the assessment line. See [CAPABILITY_MATRIX.md](docs/CAPABILITY_MATRIX.md).
