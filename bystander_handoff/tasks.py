"""Inspect tasks. Each takes a cell id; one eval is one task on one cell.

inspect eval bystander_handoff/tasks.py@action -T cell=k7_exposed_clear --model openrouter/google/gemini-2.5-pro
"""

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.solver import generate, system_message, use_tools

from bystander_handoff.cell import Cell
from bystander_handoff.followups import ALL_CELLS as FOLLOWUP_CELLS
from bystander_handoff.phase1 import CELLS, EPOCHS, seeds_for
from bystander_handoff.predecessors import INCIDENT_FILE
from bystander_handoff.render import render
from bystander_handoff.scenario import read_prompt
from bystander_handoff.scorers import (
    escalated,
    exposure_set,
    judge,
    mentioned_host,
    rating,
)
from bystander_handoff.solvers import review_loop
from bystander_handoff.tools import escalate, submit_review

# Cuts runaway tool loops. Each turn is one assistant message plus one tool
# message per call, so this is roughly 6-9 turns. Inspect records the limit on the sample.
MESSAGE_LIMIT = 20


def cell_by_id(cell_id: str) -> Cell:
    known = CELLS + FOLLOWUP_CELLS
    for c in known:
        if c.id == cell_id:
            return c
    raise ValueError(f"unknown cell {cell_id!r}; known: {[c.id for c in known]}")


def samples(cell: Cell, prefix: str = "") -> MemoryDataset:
    """One sample per seed. `prefix` goes before the rendered context.

    Target is the list of build stages that had deploy.log as an input; only
    belief_exposure scores against it.
    """
    out = []
    for seed in range(seeds_for(cell)):
        rendered = render(cell, seed)
        exposed = [r.stage for r in rendered.reports if INCIDENT_FILE in r.inputs]
        out.append(
            Sample(
                id=seed,
                input=prefix + rendered.context,
                target=exposed,
                metadata=cell.to_metadata(),
            )
        )
    return MemoryDataset(out, name=cell.id)


@task
def action(cell: str = "k0_clear") -> Task:
    """The subject does its review with tools available. Primary outcome: escalate."""
    c = cell_by_id(cell)
    return Task(
        dataset=samples(c),
        solver=[
            system_message(read_prompt("subject_system.md")),
            use_tools(escalate(), submit_review()),
            review_loop(),
        ],
        scorer=[escalated(), mentioned_host(), judge()],
        epochs=EPOCHS,
        message_limit=MESSAGE_LIMIT,
    )


@task
def belief_ambiguity(cell: str = "k0_clear") -> Task:
    """Pilot check: is the incident detectable when asked directly? No tools, no role."""
    c = cell_by_id(cell)
    return Task(
        dataset=samples(c, prefix=read_prompt("belief_ambiguity.md") + "\n"),
        solver=generate(),
        scorer=rating(),
        epochs=1,
    )


@task
def belief_exposure(cell: str = "k7_exposed_clear") -> Task:
    """Pilot check: can the subject tell which stages had deploy.log? No tools, no role."""
    c = cell_by_id(cell)
    return Task(
        dataset=samples(c, prefix=read_prompt("belief_exposure.md") + "\n"),
        solver=generate(),
        scorer=exposure_set(),
        epochs=1,
    )
