"""Write every phase-1 cell, at a few seeds, to rendered/ for reading.

This is the pre-registration artifact: exactly what the subject sees.
"""

import shutil
from pathlib import Path

from bystander_handoff.phase1 import CELLS
from bystander_handoff.render import render
from bystander_handoff.scenario import read_prompt

OUT = Path(__file__).parent.parent / "rendered"
SEEDS = (0, 1, 2)


def main() -> None:
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir()
    (OUT / "subject_system.md").write_text(read_prompt("subject_system.md"))
    for cell in CELLS:
        cell_dir = OUT / cell.id
        cell_dir.mkdir()
        for seed in SEEDS:
            (cell_dir / f"seed{seed}.md").write_text(render(cell, seed).context)
    print(f"wrote {len(CELLS)} cells x {len(SEEDS)} seeds to {OUT}")


if __name__ == "__main__":
    main()
