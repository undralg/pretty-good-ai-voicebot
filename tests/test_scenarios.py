from __future__ import annotations

from pgai_voicebot.scenarios import ScenarioRepository


def test_scenario_suite_is_complete_and_unique(scenario_root) -> None:
    scenarios = ScenarioRepository(scenario_root).load_all()

    assert len(scenarios) == 20
    assert [scenario.id for scenario in scenarios] == [f"S{number:02d}" for number in range(1, 21)]
    assert len({scenario.id for scenario in scenarios}) == 20
    assert all(60 <= scenario.max_duration_seconds <= 240 for scenario in scenarios)


def test_correction_scenario_requires_initial_and_corrected_turns(scenario_root) -> None:
    scenario = ScenarioRepository(scenario_root).get("S08")

    assert "state only Tuesday" in scenario.complication
    assert "Do not mention Thursday in that same turn" in scenario.complication
    assert "correct the request to Thursday" in scenario.complication


def test_reschedule_scenario_keeps_the_existing_demo_identity(scenario_root) -> None:
    scenario = ScenarioRepository(scenario_root).get("S02")

    assert scenario.persona.name == "Mara Calder"
    assert "confirm that the caller is Mara" in scenario.complication
    assert "different patient" in scenario.complication


def test_suite_does_not_repackage_the_brief_example(scenario_root) -> None:
    scenarios = ScenarioRepository(scenario_root).load_all()
    searchable = " ".join(
        text
        for scenario in scenarios
        for text in (
            scenario.title,
            scenario.goal,
            scenario.complication,
            *scenario.facts_to_reveal_when_asked,
        )
    )

    assert "sunday" not in searchable.lower()


def test_state_audit_is_strictly_read_only(scenario_root) -> None:
    scenario = ScenarioRepository(scenario_root).get("S14")
    instructions = " ".join(
        (
            scenario.goal,
            scenario.complication,
            *scenario.safety_expectations,
        )
    ).lower()

    for forbidden_action in ("booking", "cancellation", "rescheduling", "messaging", "transfer"):
        assert forbidden_action in instructions
    assert "decline" in instructions


def test_atomic_reschedule_requires_a_completed_compatible_replacement(scenario_root) -> None:
    scenario = ScenarioRepository(scenario_root).get("S12")
    instructions = " ".join(
        (
            scenario.goal,
            scenario.complication,
            *scenario.success_criteria,
            *scenario.safety_expectations,
        )
    ).lower()

    assert scenario.max_duration_seconds == 240
    assert "actually complete" in instructions
    assert "until the replacement is confirmed" in instructions
    assert "old slot was released" in instructions
    assert "exact new slot is booked" in instructions


def test_post_reschedule_audit_checks_exact_old_and_new_slots_without_writes(
    scenario_root,
) -> None:
    scenario = ScenarioRepository(scenario_root).get("S15")
    instructions = " ".join(
        (
            scenario.goal,
            scenario.complication,
            *scenario.facts_to_reveal_when_asked,
            *scenario.success_criteria,
            *scenario.safety_expectations,
        )
    ).lower()

    assert "august 28, 2026 at 4:00 p.m." in instructions
    assert "september 10, 2026 at 3:00 p.m." in instructions
    assert "read-only" in instructions
    for forbidden_action in ("booking", "cancellation", "rescheduling", "messaging", "transfer"):
        assert forbidden_action in instructions


def test_hours_discovery_is_information_only_and_produces_exact_boundaries(
    scenario_root,
) -> None:
    scenario = ScenarioRepository(scenario_root).get("S16")
    instructions = " ".join(
        (
            scenario.goal,
            scenario.complication,
            *scenario.facts_to_reveal_when_asked,
            *scenario.success_criteria,
            *scenario.safety_expectations,
        )
    ).lower()

    assert "information-only" in instructions
    assert "opening and closing" in instructions
    assert "either weekend day" in instructions
    assert "bookable appointment" in instructions
    for forbidden_action in ("booking", "cancellation", "rescheduling", "messaging", "transfer"):
        assert forbidden_action in instructions


def test_after_hours_attempt_uses_a_weekday_boundary_and_protects_existing_state(
    scenario_root,
) -> None:
    scenario = ScenarioRepository(scenario_root).get("S17")
    instructions = " ".join(
        (
            scenario.goal,
            scenario.complication,
            *scenario.facts_to_reveal_when_asked,
            *scenario.success_criteria,
            *scenario.safety_expectations,
        )
    ).lower()

    assert "wednesday, september 16, 2026 at 7:30 p.m." in instructions
    assert "wednesday appointments end at 7:00 p.m." in instructions
    assert "thirty minutes beyond" in instructions
    assert "accepts only the exact 7:30 p.m." in instructions
    assert "september 10" in instructions
    assert "remains unchanged" in instructions


def test_location_audit_reconciles_austin_and_nashville_without_writes(
    scenario_root,
) -> None:
    scenario = ScenarioRepository(scenario_root).get("S18")
    instructions = " ".join(
        (
            scenario.goal,
            scenario.complication,
            *scenario.facts_to_reveal_when_asked,
            *scenario.success_criteria,
            *scenario.safety_expectations,
        )
    ).lower()

    assert "every" in instructions
    assert "austin" in instructions
    assert "nashville" in instructions
    assert "exact street" in instructions
    assert "how a booking location is selected" in instructions
    for forbidden_action in (
        "booking",
        "cancellation",
        "rescheduling",
        "messaging",
        "transfer",
    ):
        assert forbidden_action in instructions
    assert "decline" in instructions


def test_multi_boundary_booking_attempt_uses_weekend_and_before_opening(
    scenario_root,
) -> None:
    scenario = ScenarioRepository(scenario_root).get("S19")
    instructions = " ".join(
        (
            scenario.goal,
            scenario.complication,
            *scenario.facts_to_reveal_when_asked,
            *scenario.success_criteria,
            *scenario.safety_expectations,
        )
    ).lower()

    assert "saturday, september 19, 2026 at 10:00 a.m." in instructions
    assert "monday, september 21, 2026 at 8:30 a.m." in instructions
    assert "weekends are closed" in instructions
    assert "monday appointments begin at 9:00 a.m." in instructions
    assert "austin" in instructions
    assert "authorize" in instructions
    assert "september 10" in instructions
    assert "remains unchanged" in instructions


def test_insurance_boundary_separates_acceptance_from_coverage_and_cost(
    scenario_root,
) -> None:
    scenario = ScenarioRepository(scenario_root).get("S20")
    instructions = " ".join(
        (
            scenario.goal,
            scenario.complication,
            *scenario.facts_to_reveal_when_asked,
            *scenario.success_criteria,
            *scenario.safety_expectations,
        )
    ).lower()

    assert "northstar choice silver" in instructions
    assert "plan acceptance" in instructions
    assert "guarantee" in instructions
    assert "exact copay" in instructions
    assert "member-specific" in instructions
    assert "member id" in instructions
    assert "non-transfer verification route" in instructions
    for forbidden_action in (
        "booking",
        "cancellation",
        "rescheduling",
        "messaging",
        "transfer",
    ):
        assert forbidden_action in instructions
