"""The ten phase-1 cells and the per-cell sampling plan."""

from bystander_handoff.cell import Ambiguity, Cell, Predecessor

CELLS: tuple[Cell, ...] = (
    Cell(k=0, ambiguity=Ambiguity.CLEAR),
    Cell(k=0, ambiguity=Ambiguity.AMBIGUOUS),
    Cell(k=7, ambiguity=Ambiguity.CLEAR, predecessor=Predecessor.INERT),
    Cell(k=7, ambiguity=Ambiguity.AMBIGUOUS, predecessor=Predecessor.INERT),
    Cell(k=7, ambiguity=Ambiguity.CLEAR, predecessor=Predecessor.UNEXPOSED),
    Cell(k=7, ambiguity=Ambiguity.AMBIGUOUS, predecessor=Predecessor.UNEXPOSED),
    Cell(k=7, ambiguity=Ambiguity.CLEAR, predecessor=Predecessor.EXPOSED),
    Cell(k=7, ambiguity=Ambiguity.AMBIGUOUS, predecessor=Predecessor.EXPOSED),
    Cell(k=7, ambiguity=Ambiguity.CLEAR, predecessor=Predecessor.DISMISSIVE),
    Cell(k=7, ambiguity=Ambiguity.AMBIGUOUS, predecessor=Predecessor.DISMISSIVE),
)

SEEDS_PER_CELL = 20
EPOCHS = 5
