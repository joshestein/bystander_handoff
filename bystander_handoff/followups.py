"""Cells outside phase 1. Each list is one follow-up; run with scripts/run_phase1.py <model> <log_dir> <cell_ids>."""

from bystander_handoff.cell import Ambiguity, Cell, Predecessor

# Exploratory, post-hoc after the k=7 null: do thirty silent witnesses do what seven did not?
# Ambiguous only (the level with headroom on Grok 4.7 and DeepSeek).
K30_CELLS: tuple[Cell, ...] = (
    Cell(k=30, ambiguity=Ambiguity.AMBIGUOUS, predecessor=Predecessor.INERT),
    Cell(k=30, ambiguity=Ambiguity.AMBIGUOUS, predecessor=Predecessor.UNEXPOSED),
    Cell(k=30, ambiguity=Ambiguity.AMBIGUOUS, predecessor=Predecessor.EXPOSED),
)

ALL_CELLS: tuple[Cell, ...] = K30_CELLS
