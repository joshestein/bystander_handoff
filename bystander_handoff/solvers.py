"""The action loop. Ends on escalate, or when the subject stops calling tools."""

from inspect_ai.model import ChatMessageAssistant
from inspect_ai.solver import Generate, Solver, TaskState, solver

from bystander_handoff.tools import ESCALATE

MAX_TURNS = 8


@solver
def review_loop() -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        for _ in range(MAX_TURNS):
            # "single": one model turn, execute its tool calls, return.
            state = await generate(state, tool_calls="single")
            called = tool_calls_in(state.output.message)
            if not called or ESCALATE in called:
                break
        return state

    return solve


def tool_calls_in(message: ChatMessageAssistant) -> list[str]:
    """Function names called by an assistant message, in order."""
    return [call.function for call in (message.tool_calls or [])]
