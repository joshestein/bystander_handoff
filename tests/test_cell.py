import pytest

from bystander_handoff.cell import Ambiguity, Cell, Predecessor
from bystander_handoff.phase1 import CELLS


def test_phase1_has_ten_distinct_cells() -> None:
    assert len(CELLS) == 10
    assert len({c.id for c in CELLS}) == 10


def test_id_format() -> None:
    assert Cell(k=0, ambiguity=Ambiguity.CLEAR).id == "k0_clear"
    assert (
        Cell(k=7, ambiguity=Ambiguity.AMBIGUOUS, predecessor=Predecessor.EXPOSED).id
        == "k7_exposed_ambiguous"
    )


def test_k0_rejects_predecessor() -> None:
    with pytest.raises(ValueError):
        Cell(k=0, ambiguity=Ambiguity.CLEAR, predecessor=Predecessor.INERT)


def test_k7_requires_predecessor() -> None:
    with pytest.raises(ValueError):
        Cell(k=7, ambiguity=Ambiguity.CLEAR)


def test_metadata_is_flat_and_includes_id() -> None:
    cell = Cell(k=7, ambiguity=Ambiguity.CLEAR, predecessor=Predecessor.INERT)
    assert cell.to_metadata() == {
        "k": 7,
        "ambiguity": "clear",
        "predecessor": "inert",
        "cell_id": "k7_inert_clear",
    }


def test_dismissive_cells_get_fewer_seeds() -> None:
    from bystander_handoff.phase1 import SEEDS_PER_CELL, SEEDS_PER_CONTROL_CELL, seeds_for

    counts = {seeds_for(c) for c in CELLS}
    assert counts == {SEEDS_PER_CELL, SEEDS_PER_CONTROL_CELL}
    assert sum(seeds_for(c) for c in CELLS) == 180
