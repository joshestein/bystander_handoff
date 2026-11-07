"""Static scenario files and prompts, loaded from disk.

The only thing assembled here is deploy.log: the base log with its one
placeholder line replaced by the incident variant for the ambiguity level.
"""

from functools import cache
from pathlib import Path

import yaml

from bystander_handoff.cell import Ambiguity

_SCENARIO = Path(__file__).parent / "scenario"
_PROMPTS = Path(__file__).parent / "prompts"

INCIDENT_PLACEHOLDER = "{incident}"

# Which ambiguous variant is live. The pilot's ambiguity check may swap this
# to "ambiguous_b". Nothing else in the codebase knows there are two.
AMBIGUOUS_VARIANT = "ambiguous_a"


@cache
def read_scenario(name: str) -> str:
    return (_SCENARIO / name).read_text()


@cache
def read_prompt(name: str) -> str:
    return (_PROMPTS / name).read_text()


@cache
def _base_log_lines() -> tuple[str, ...]:
    return tuple(read_scenario("deploy_base.log").splitlines())


def incident_line_number() -> int:
    """1-based line number of the incident in the rendered deploy.log."""
    return _placeholder_index() + 1


def log_line_count() -> int:
    return len(_base_log_lines())


def incident_url(ambiguity: Ambiguity) -> str:
    variant = "clear" if ambiguity is Ambiguity.CLEAR else AMBIGUOUS_VARIANT
    return _incidents()[variant]["url"]


def deploy_log(ambiguity: Ambiguity) -> str:
    spec = _incidents()
    line = spec["line_template"].format(url=incident_url(ambiguity), body=spec["body"])
    lines = list(_base_log_lines())
    lines[_placeholder_index()] = line
    return "\n".join(lines) + "\n"


@cache
def _placeholder_index() -> int:
    """0-based index of the line that is exactly the placeholder."""
    lines = _base_log_lines()
    matches = [i for i, l in enumerate(lines) if l.strip() == INCIDENT_PLACEHOLDER]
    if len(matches) != 1:
        raise ValueError(
            f"expected one {INCIDENT_PLACEHOLDER} line, found {len(matches)}"
        )
    return matches[0]


@cache
def _incidents() -> dict:
    return yaml.safe_load(read_scenario("incidents.yaml"))
