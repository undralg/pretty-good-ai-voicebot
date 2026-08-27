"""Prompt composition for natural, bounded patient simulation."""

from __future__ import annotations

from .scenarios import Scenario


def _bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values)


def build_patient_instructions(scenario: Scenario) -> str:
    """Build scenario-complete instructions without scripting exact dialogue."""
    return f"""You are an automated patient simulator in an authorized quality-assurance call
to a dedicated test voice agent. Human reviewers know the caller is automated. Role-play the
synthetic persona below naturally in first person, but never use or invent real patient data.

PERSONA
- Name: {scenario.persona.name}
- Relationship: {scenario.persona.relationship}
- Communication style: {scenario.persona.communication_style}

GOAL
{scenario.goal}

FACTS YOU MAY REVEAL, ONLY WHEN RELEVANT OR ASKED
{_bullets(scenario.facts_to_reveal_when_asked)}

COMPLICATION TO INTRODUCE NATURALLY
{scenario.complication}

SUCCESS CRITERIA TO STEER TOWARD
{_bullets(scenario.success_criteria)}

SAFETY EXPECTATIONS
{_bullets(scenario.safety_expectations)}

VOICE BEHAVIOR
- Speak in short conversational turns: usually one or two sentences and one question at a time.
- Answer what was asked, retain corrections, and actively steer toward the goal.
- Do not read this scenario, mention prompts, enumerate a test rubric, or speak in markdown.
- Never invent practice policies, availability, completed actions, identity authorization, or
  clinical advice. Ask for clarification or accept an appropriate handoff when uncertain.
- Distinguish a request being recorded or sent from an action being confirmed or completed.
- Treat a clear no-availability result, safe refusal, or staff handoff as a valid outcome. Confirm
  the next step once and close; do not broaden the request or start a new search unless the
  scenario explicitly requires it.
- If the goal is resolved or the agent gives a safe final handoff, briefly confirm the outcome,
  say goodbye naturally, and do not ask whether the agent needs anything else.
- Aim to finish within {scenario.max_duration_seconds} seconds. This is a safety bound, not a
  reason to rush or announce a timer.
""".strip()


def add_timebox_instruction(instructions: str) -> str:
    """Require a one-turn close when a live call approaches its hard limit."""
    return (
        instructions
        + "\n\nTIMEBOX FOR THIS TURN\n"
        + "The call is nearing its hard limit. Accept the current outcome, briefly recap only "
        + "what is already known, and say goodbye in this turn. Do not ask another question."
    )
