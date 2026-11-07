"""The action loop. Ends on a successful escalate, or when the subject stops calling tools.

Runaway loops are cut by the task's message_limit; Inspect records that on the
sample, so a truncated episode is distinguishable from a chosen non-escalation.
"""

from inspect_ai.solver import Generate, Solver, TaskState, solver

from bystander_handoff.tools import ESCALATE, calls_attempted, calls_succeeded


@solver
def review_loop() -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        while not state.completed:
            before = len(state.messages)
            # "single": one model turn, execute its tool calls, return.
            state = await generate(state, tool_calls="single")
            new = state.messages[before:]
            if not calls_attempted(new) or ESCALATE in calls_succeeded(new):
                break
        return state

    return solve
