"""Cell: one combination of the manipulated factors.

A Cell is one combination of k, predecessor, and ambiguity. Everything else
(task, tools, files, model) is fixed outside the cell. Seed is not a field:
a cell is seed-free, and render(cell, seed) varies surface text within it.
"""

from dataclasses import asdict, dataclass
from enum import StrEnum


class Predecessor(StrEnum):
    INERT = "inert"
    UNEXPOSED = "unexposed"
    EXPOSED = "exposed"
    DISMISSIVE = "dismissive"


class Ambiguity(StrEnum):
    CLEAR = "clear"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True)
class Cell:
    k: int
    ambiguity: Ambiguity
    predecessor: Predecessor | None = None

    def __post_init__(self) -> None:
        if self.k not in (0, 7):
            raise ValueError(f"k must be 0 or 7, got {self.k}")
        if self.k == 0 and self.predecessor is not None:
            raise ValueError("k=0 has no predecessors")
        if self.k > 0 and self.predecessor is None:
            raise ValueError(f"k={self.k} requires a predecessor")

    @property
    def id(self) -> str:
        middle = f"_{self.predecessor}" if self.predecessor else ""
        return f"k{self.k}{middle}_{self.ambiguity}"

    def to_metadata(self) -> dict[str, str | int | None]:
        return asdict(self) | {"cell_id": self.id}
