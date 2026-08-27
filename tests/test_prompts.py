from pgai_voicebot.prompts import add_timebox_instruction
from pgai_voicebot.relay import should_force_close


def test_timebox_instruction_requires_a_close_without_another_question() -> None:
    result = add_timebox_instruction("Base scenario instructions")

    assert result.startswith("Base scenario instructions")
    assert "say goodbye in this turn" in result
    assert "Do not ask another question" in result


def test_force_close_reserves_last_thirty_seconds_only_for_long_scenarios() -> None:
    assert should_force_close(max_duration_seconds=180, elapsed_seconds=150)
    assert not should_force_close(max_duration_seconds=180, elapsed_seconds=149.9)
    assert not should_force_close(max_duration_seconds=120, elapsed_seconds=119)
