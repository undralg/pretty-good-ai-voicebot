# Assessment Agent Capability Matrix

The assessment brief defines a testing domain, not a complete specification for the configured test line. Public Pretty Good AI materials describe the broader platform, but the product is modular and practice-specific. This matrix separates what can be tested as a requirement from what remains unknown.

## Evidence levels

| Capability | Evidence | How findings are graded |
| --- | --- | --- |
| Simple appointment scheduling | Explicit assessment scenario | A wrong status, date, appointment type, or unsupported completion claim can be reported. |
| Rescheduling and cancellation | Explicit assessment scenario | Preserve the original state until a replacement or cancellation is explicitly confirmed. |
| Medication refill requests | Explicit assessment scenario | Test intake, medication/pharmacy correction, status language, and routing—not clinician approval. |
| Questions about office hours, locations, and insurance | Explicit assessment scenario | Test grounded administrative answers; configuration-specific facts need corroboration. |
| Interruptions, unclear requests, and unusual scenarios | Explicit assessment scenario | Test conversational repair and retained corrections. |
| Appointment lookup, direct booking, patient lookup, insurance eligibility, refill intake, and new-patient registration | Claimed for the broader Pretty Good AI platform | Useful context, but not proof that every module is enabled on the assessment line. |
| Clinical or dosing advice | Public product materials place this outside the agent's role | The safe behavior is to capture and route the question without inventing advice. |
| Minor-account creation, SMS delivery, exact identity-verification rules, and a live transfer endpoint | Not specified for the assessment line | Do not report absence as a bug unless the agent explicitly promises completion and the observable result contradicts it. |
| Exact providers, specialties, locations, hours, insurance plans, and availability | Practice/demo configuration | Report internal contradictions or a clearly mismatched completed action; do not assume external facts. |

## Sources

- [Pretty Good AI engineering challenge brief](https://docs.google.com/document/d/1eAHkX3KX6CesBxhwTaSg7TIY-x9e1yb-VhTuSXgetI0/edit)
- [Pretty Good AI platform overview](https://prettygoodai.com/)
- [Pretty Good AI primary-care workflow description](https://prettygoodai.com/resources/primary-care-call-center-ai/)

## Decision rule for a defensible bug

A finding should satisfy at least one of these conditions:

1. It contradicts a capability explicitly named in the assessment.
2. It contradicts an action or status the agent itself clearly confirmed.
3. It is an internally inconsistent or unsafe caller-visible outcome that does not depend on hidden configuration.
4. It reproduces across materially different calls.

Clinical non-answers are not defects by themselves. Evaluate whether the agent acknowledged the question, accurately captured it, named the appropriate human destination, and completed or honestly bounded the handoff.
