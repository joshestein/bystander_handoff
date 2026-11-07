"""The ten phase-1 cells, in run order, and the per-cell sampling plan."""

from bystander_handoff.cell import Ambiguity, Cell, Predecessor

EPOCHS = 5
SEEDS_PER_CELL = 20
SEEDS_PER_CONTROL_CELL = 10  # dismissive: expected to collapse, needs less power

# Run order. Clear first so clear-only is a usable fallback. Within each
# ambiguity level: k=0, unexposed, exposed (the story), then inert and
# dismissive (the controls).
CELLS: tuple[Cell, ...] = (
    Cell(k=0, ambiguity=Ambiguity.CLEAR),
    Cell(k=7, ambiguity=Ambiguity.CLEAR, predecessor=Predecessor.UNEXPOSED),
    Cell(k=7, ambiguity=Ambiguity.CLEAR, predecessor=Predecessor.EXPOSED),
    Cell(k=7, ambiguity=Ambiguity.CLEAR, predecessor=Predecessor.INERT),
    Cell(k=7, ambiguity=Ambiguity.CLEAR, predecessor=Predecessor.DISMISSIVE),
    Cell(k=0, ambiguity=Ambiguity.AMBIGUOUS),
    Cell(k=7, ambiguity=Ambiguity.AMBIGUOUS, predecessor=Predecessor.UNEXPOSED),
    Cell(k=7, ambiguity=Ambiguity.AMBIGUOUS, predecessor=Predecessor.EXPOSED),
    Cell(k=7, ambiguity=Ambiguity.AMBIGUOUS, predecessor=Predecessor.INERT),
    Cell(k=7, ambiguity=Ambiguity.AMBIGUOUS, predecessor=Predecessor.DISMISSIVE),
)


def seeds_for(cell: Cell) -> int:
    if cell.predecessor is Predecessor.DISMISSIVE:
        return SEEDS_PER_CONTROL_CELL
    return SEEDS_PER_CELL
