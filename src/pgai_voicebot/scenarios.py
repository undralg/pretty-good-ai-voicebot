"""Scenario schema and repository."""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Persona(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=80)
    relationship: str = Field(min_length=2, max_length=120)
    communication_style: str = Field(min_length=2, max_length=300)


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str = Field(min_length=4, max_length=120)
    category: str = Field(min_length=2, max_length=80)
    persona: Persona
    goal: str = Field(min_length=10, max_length=500)
    facts_to_reveal_when_asked: list[str] = Field(min_length=1)
    complication: str = Field(min_length=10, max_length=600)
    success_criteria: list[str] = Field(min_length=1)
    safety_expectations: list[str] = Field(min_length=1)
    max_duration_seconds: int = Field(ge=60, le=240)

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        normalized = value.strip().upper()
        match = re.fullmatch(r"(?:S|SCENARIO-)(\d{2})", normalized)
        if not match:
            raise ValueError("Scenario id must use the form S01 or scenario-01.")
        return f"S{match.group(1)}"

    @field_validator(
        "facts_to_reveal_when_asked", "success_criteria", "safety_expectations"
    )
    @classmethod
    def validate_nonempty_items(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values]
        if any(not value for value in cleaned):
            raise ValueError("List values cannot be blank.")
        return cleaned


class ScenarioRepository:
    def __init__(self, root: Path):
        self.root = root

    def load_all(self) -> list[Scenario]:
        if not self.root.is_dir():
            raise FileNotFoundError(f"Scenario directory does not exist: {self.root}")
        scenarios: list[Scenario] = []
        seen: set[str] = set()
        for path in sorted(self.root.glob("*.yaml")):
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            scenario = Scenario.model_validate(raw)
            if scenario.id in seen:
                raise ValueError(f"Duplicate scenario id: {scenario.id}")
            seen.add(scenario.id)
            scenarios.append(scenario)
        if not scenarios:
            raise ValueError(f"No YAML scenarios found in {self.root}")
        return scenarios

    def get(self, identifier: str) -> Scenario:
        normalized = identifier.strip().upper()
        for scenario in self.load_all():
            if scenario.id == normalized:
                return scenario
        raise KeyError(f"Unknown scenario {identifier!r}.")
