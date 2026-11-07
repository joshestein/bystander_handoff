When an LLM agent witnesses misconduct, do silent upstream witnesses reduce its intervention, and does incident ambiguity explain the reduction?

The subject is the last reviewer in a deploy pipeline. Stage 1 committed an incident in `deploy.log`; `k` scripted predecessors said nothing. Outcome: does the subject call `escalate`?

## Setup

```sh
uv sync
uv run pre-commit install
echo 'OPENROUTER_API_KEY=...' > .env
```

## Development

```sh
uv run pytest
uv run pre-commit run --all-files   # ruff lint + format
```
