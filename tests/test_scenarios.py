from __future__ import annotations

from pgai_voicebot.scenarios import ScenarioRepository


def test_scenario_suite_is_complete_and_unique(scenario_root) -> None:
    scenarios = ScenarioRepository(scenario_root).load_all()

    assert len(scenarios) == 10
    assert [scenario.id for scenario in scenarios] == [f"S{number:02d}" for number in range(1, 11)]
    assert len({scenario.id for scenario in scenarios}) == 10
    assert all(60 <= scenario.max_duration_seconds <= 210 for scenario in scenarios)


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
