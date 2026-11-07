"""Cell table and the five pre-registered contrasts, from action-task logs.

    uv run python scripts/contrasts.py logs/phase1

Reports every number twice: all usable samples, and with paradigm-flagged
samples removed. Never only the second.
"""

import sys
from collections import Counter
from pathlib import Path

from bystander_handoff.analysis import (
    Row,
    difference,
    exclusions,
    interaction,
    rate,
    read_logs,
    rows_from_logs,
)
from bystander_handoff.phase1 import CELLS

# (name, a, b): a.p - b.p. The interaction is handled separately.
CONTRASTS = (
    ("1 witness (clear)", "k7_exposed_clear", "k7_unexposed_clear"),
    ("3 presence (clear)", "k7_unexposed_clear", "k7_inert_clear"),
    ("4 context (clear)", "k7_inert_clear", "k0_clear"),
    ("5 positive control (clear)", "k7_dismissive_clear", "k7_exposed_clear"),
    ("1 witness (ambiguous)", "k7_exposed_ambiguous", "k7_unexposed_ambiguous"),
    ("3 presence (ambiguous)", "k7_unexposed_ambiguous", "k7_inert_ambiguous"),
    ("4 context (ambiguous)", "k7_inert_ambiguous", "k0_ambiguous"),
    (
        "5 positive control (ambiguous)",
        "k7_dismissive_ambiguous",
        "k7_exposed_ambiguous",
    ),
)


def report(rows: list[Row], title: str) -> None:
    print(f"\n## {title}  (n usable = {sum(r.usable for r in rows)})\n")
    print("| cell | n | escalated | mentioned | silent | rate | 95% CI |")
    print("|---|---|---|---|---|---|---|")
    for cell in CELLS:
        usable = [r for r in rows if r.cell_id == cell.id and r.usable]
        if not usable:
            continue
        counts = Counter(r.outcome for r in usable)
        rt = rate(rows, cell.id)
        lo, hi = rt.wilson()
        print(
            f"| {cell.id} | {rt.n} | {counts['escalated']} | {counts['mentioned']} | {counts['silent']} "
            f"| {rt.p:.2f} | [{lo:.2f}, {hi:.2f}] |"
        )

    print("\n| contrast | a | b | a - b | 95% CI |")
    print("|---|---|---|---|---|")
    for name, a_id, b_id in CONTRASTS:
        a, b = rate(rows, a_id), rate(rows, b_id)
        if not (a.n and b.n):
            continue
        d, lo, hi = difference(a, b)
        print(f"| {name} | {a.p:.2f} | {b.p:.2f} | {d:+.2f} | [{lo:+.2f}, {hi:+.2f}] |")

    cells = [
        rate(rows, c)
        for c in (
            "k7_exposed_ambiguous",
            "k7_unexposed_ambiguous",
            "k7_exposed_clear",
            "k7_unexposed_clear",
        )
    ]
    if all(c.n for c in cells):
        est, lo, hi = interaction(*cells)
        print(
            f"| 2 pluralistic ignorance (ambiguous gap - clear gap) | | | {est:+.2f} | [{lo:+.2f}, {hi:+.2f}] |"
        )


def main(log_dir: Path) -> None:
    rows = rows_from_logs(read_logs(log_dir))
    print(f"# {log_dir}: {len(rows)} samples")
    for cell_id, counts in exclusions(rows).items():
        print(f"excluded in {cell_id}: {dict(counts)}")
    report(rows, "all usable samples")
    flagged = sum(r.paradigm for r in rows if r.usable)
    report(
        [r for r in rows if not r.paradigm],
        f"paradigm-flagged removed ({flagged} flagged)",
    )


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "logs/phase1"))
