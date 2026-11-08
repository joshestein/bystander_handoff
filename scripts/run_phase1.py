"""Run action evals, one per cell, in order. Default: phase1.CELLS (clear first).

    uv run python scripts/run_phase1.py [model] [log_dir] [cell_id,cell_id,...] [brief]

Cell ids may come from phase1.CELLS or followups.ALL_CELLS. Brief is a key of
tasks.BRIEFS (default `assigned`). Use one log dir per (model, brief).

Skips any cell that already has a successful log in the directory, so it can
be re-run after an interruption without double counting. Analyze with
scripts/contrasts.py at any point.
"""

import sys
from pathlib import Path

from inspect_ai import eval as inspect_eval
from inspect_ai.log import read_eval_log

from bystander_handoff.phase1 import CELLS
from bystander_handoff.tasks import action, cell_by_id


def completed_cells(log_dir: Path) -> set[str]:
    done = set()
    for path in log_dir.glob("*.eval"):
        log = read_eval_log(str(path), header_only=True)
        if log.eval.task.split("/")[-1] == "action" and log.status == "success":
            done.add(log.eval.task_args["cell"])
    return done


def main(
    model: str, log_dir: str, cell_ids: list[str] | None, brief: str = "assigned"
) -> None:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    done = completed_cells(Path(log_dir))
    cells = [cell_by_id(c) for c in cell_ids] if cell_ids else CELLS
    for cell in cells:
        if cell.id in done:
            print(f"skip {cell.id}: already in {log_dir}")
            continue
        print(f"\n=== {cell.id}")
        (log,) = inspect_eval(
            action(cell=cell.id, brief=brief),
            model=model,
            log_dir=log_dir,
            display="plain",
        )
        if log.status != "success":
            raise RuntimeError(
                f"{cell.id} failed: {log.status}. Fix and re-run; completed cells are skipped."
            )


if __name__ == "__main__":
    main(
        sys.argv[1] if len(sys.argv) > 1 else "openrouter/x-ai/grok-4.7",
        sys.argv[2] if len(sys.argv) > 2 else "logs/phase1",
        sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] else None,
        sys.argv[4] if len(sys.argv) > 4 else "assigned",
    )
