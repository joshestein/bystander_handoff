"""Inspect tasks. Each takes a cell id; one eval is one task on one cell.

inspect eval bystander_handoff/tasks.py@action -T cell=k7_exposed_clear --model openrouter/google/gemini-2.5-pro
"""

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.solver import generate, system_message, use_tools

from bystander_handoff.cell import Cell
from bystander_handoff.phase1 import CELLS, EPOCHS, seeds_for
from bystander_handoff.render import render
from bystander_handoff.scenario import read_prompt
from bystander_handoff.scorers import escalated
from bystander_handoff.solvers import review_loop
from bystander_handoff.tools import escalate, submit_review

# Cuts runaway tool loops. Each turn is one assistant message plus one tool
# message per call, so this is roughly 6-9 turns. Inspect records the limit on the sample.
MESSAGE_LIMIT = 20


def cell_by_id(cell_id: str) -> Cell:
    for c in CELLS:
        if c.id == cell_id:
            return c
    raise ValueError(f"unknown cell {cell_id!r}; known: {[c.id for c in CELLS]}")


def samples(cell: Cell, prefix: str = "") -> MemoryDataset:
    """One sample per seed. `prefix` goes before the rendered context."""
    return MemoryDataset(
        [
            Sample(
                id=seed,
                input=prefix + render(cell, seed).context,
                metadata=cell.to_metadata(),
            )
            for seed in range(seeds_for(cell))
        ],
        name=cell.id,
    )


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
        scorer=escalated(),
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
        epochs=1,
    )


@task
def belief_exposure(cell: str = "k7_exposed_clear") -> Task:
    """Pilot check: can the subject tell which stages had deploy.log? No tools, no role."""
    c = cell_by_id(cell)
    return Task(
        dataset=samples(c, prefix=read_prompt("belief_exposure.md") + "\n"),
        solver=generate(),
        epochs=1,
    )
