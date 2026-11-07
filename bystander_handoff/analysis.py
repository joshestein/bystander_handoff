"""Read action-task logs into per-sample rows, and the statistics the contrasts need.

Exclusions: errored, truncated (sample.limit set), and failed (the final
generation came back empty with stop_reason "unknown", i.e. a malformed tool
call that survived the solver's retries) are not decisions. They are dropped
from rates and counted.
"""

import math
import warnings
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from inspect_ai.log import EvalLog, read_eval_log

Z = 1.96


@dataclass(frozen=True)
class Row:
    cell_id: str
    escalated: bool
    mentioned: bool  # in words, per the judge
    paradigm: bool
    exclusion: str | None  # "errored" | "truncated" | "failed" | None

    @property
    def usable(self) -> bool:
        return self.exclusion is None

    @property
    def outcome(self) -> str:
        if self.escalated:
            return "escalated"
        return "mentioned" if self.mentioned else "silent"


def read_logs(log_dir: Path) -> list[EvalLog]:
    return [read_eval_log(str(p)) for p in sorted(log_dir.glob("*.eval"))]


def rows_from_logs(logs: Iterable[EvalLog]) -> list[Row]:
    out: list[Row] = []
    seen: Counter[str] = Counter()
    for log in logs:
        if log.eval.task.split("/")[-1] != "action":
            continue
        if log.status != "success" or not log.samples:
            warnings.warn(
                f"skipping {log.eval.task_args} ({log.eval.model}): status {log.status}"
            )
            continue
        cell_id = log.eval.task_args["cell"]
        seen[cell_id] += 1
        if seen[cell_id] > 1:
            warnings.warn(
                f"{cell_id} appears in more than one log; samples are being double counted"
            )
        for s in log.samples:
            scores = s.scores or {}
            if s.error or "escalated" not in scores:
                out.append(Row(cell_id, False, False, False, "errored"))
                continue
            judge = scores["judge"].value if "judge" in scores else {}
            escalated = scores["escalated"].value == 1.0
            out_ = s.output
            failed = (
                bool(out_.choices)
                and out_.choices[0].stop_reason == "unknown"
                and not out_.completion.strip()
                and not out_.message.tool_calls
            )
            exclusion = (
                "truncated" if s.limit is not None else "failed" if failed else None
            )
            out.append(
                Row(
                    cell_id=cell_id,
                    escalated=escalated,
                    mentioned=judge.get("mentioned") is True,
                    paradigm=judge.get("paradigm") is True,
                    exclusion=exclusion,
                )
            )
    return out


def exclusions(rows: list[Row]) -> Counter[str]:
    return Counter(r.exclusion for r in rows if r.exclusion)


@dataclass(frozen=True)
class Rate:
    k: int
    n: int

    @property
    def p(self) -> float:
        return self.k / self.n if self.n else math.nan

    def wilson(self) -> tuple[float, float]:
        if not self.n:
            return (math.nan, math.nan)
        p, n = self.p, self.n
        centre = (p + Z * Z / (2 * n)) / (1 + Z * Z / n)
        half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / (1 + Z * Z / n)
        return (centre - half, centre + half)


def rate(rows: list[Row], cell_id: str) -> Rate:
    usable = [r for r in rows if r.cell_id == cell_id and r.usable]
    return Rate(k=sum(r.escalated for r in usable), n=len(usable))


def difference(a: Rate, b: Rate) -> tuple[float, float, float]:
    """a.p - b.p with a Newcombe (Wilson-based) interval. Returns (diff, lo, hi)."""
    (al, ah), (bl, bh) = a.wilson(), b.wilson()
    d = a.p - b.p
    return (
        d,
        d - math.sqrt((a.p - al) ** 2 + (bh - b.p) ** 2),
        d + math.sqrt((ah - a.p) ** 2 + (b.p - bl) ** 2),
    )


def interaction(a: Rate, b: Rate, c: Rate, d: Rate) -> tuple[float, float, float]:
    """(a - b) - (c - d), combining the two Newcombe intervals (MOVER). Consistent with `difference`."""
    d1, l1, u1 = difference(a, b)
    d2, l2, u2 = difference(c, d)
    est = d1 - d2
    return (
        est,
        est - math.sqrt((d1 - l1) ** 2 + (u2 - d2) ** 2),
        est + math.sqrt((u1 - d1) ** 2 + (d2 - l2) ** 2),
    )
