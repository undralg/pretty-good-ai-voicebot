PYTHON ?= python3.12
VENV := .venv
BIN := $(VENV)/bin

.PHONY: install test lint validate list dry-run rotate-key preflight serve live-stack

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -e '.[dev]'

test:
	$(BIN)/pytest

lint:
	$(BIN)/ruff check src tests scripts

validate:
	$(BIN)/python scripts/validate_submission.py

list:
	$(BIN)/python -m pgai_voicebot.cli list-scenarios

dry-run:
	$(BIN)/python -m pgai_voicebot.cli dry-run --scenario S01

preflight:
	$(BIN)/python scripts/check_provider_access.py

rotate-key:
	$(BIN)/python scripts/rotate_twilio_key.py

serve:
	$(BIN)/uvicorn pgai_voicebot.app:app --app-dir src --host 0.0.0.0 --port 8000 --reload

live-stack:
	$(BIN)/python scripts/run_live_stack.py
