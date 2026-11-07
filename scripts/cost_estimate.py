"""Project phase-1 cost from the token usage in existing action-task logs.

    uv run python scripts/cost_estimate.py logs/pilot openrouter/x-ai/grok-4.7

Uses mean tokens per sample at k=0 and k=7 separately, times the planned
sample counts, for the given subject model plus the judge. Warns if a k has
no samples (the pilot only runs action at k=0). Cache reads are priced as
input (conservative). Prices are USD per million tokens; edit to match OpenRouter.
"""

import sys
from collections import defaultdict
from pathlib import Path

from inspect_ai.log import read_eval_log

from bystander_handoff.phase1 import CELLS, EPOCHS, seeds_for

PRICES = {  # (input, output) per 1M tokens
    "openrouter/google/gemini-2.5-pro": (1.25, 10.0),
    "openrouter/google/gemini-2.5-flash": (0.30, 2.50),
    "openrouter/openai/gpt-4.1-mini": (0.40, 1.60),
}


def main(log_dir: Path, subject: str) -> None:
    # k -> model -> [(input, output), ...] per sample
    usage: dict[int, dict[str, list[tuple[int, int]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for path in sorted(log_dir.glob("*.eval")):
        log = read_eval_log(str(path))
        if (
            log.eval.task.split("/")[-1] != "action"
            or log.eval.model != subject
            or not log.samples
        ):
            continue
        for s in log.samples:
            for model, u in (s.model_usage or {}).items():
                usage[s.metadata["k"]][model].append(
                    (u.input_tokens + (u.input_tokens_cache_read or 0), u.output_tokens)
                )
    for k in (0, 7):
        if k not in usage:
            print(
                f"WARNING: no {subject} action samples at k={k}; its {sum(seeds_for(c) * EPOCHS for c in CELLS if c.k == k)} planned samples are not in the total"
            )

    planned = {k: sum(seeds_for(c) * EPOCHS for c in CELLS if c.k == k) for k in (0, 7)}
    total = 0.0
    print("| k | model | samples seen | mean in | mean out | planned | cost |")
    print("|---|---|---|---|---|---|---|")
    for k, by_model in sorted(usage.items()):
        for model, pairs in by_model.items():
            mean_in = sum(i for i, _ in pairs) / len(pairs)
            mean_out = sum(o for _, o in pairs) / len(pairs)
            price_in, price_out = PRICES.get(model, (0.0, 0.0))
            cost = planned[k] * (mean_in * price_in + mean_out * price_out) / 1e6
            total += cost
            print(
                f"| {k} | {model} | {len(pairs)} | {mean_in:,.0f} | {mean_out:,.0f} | {planned[k]} | ${cost:,.2f} |"
            )
    print(f"\nprojected phase-1 total: ${total:,.2f}  (unpriced models count as $0)")


if __name__ == "__main__":
    main(
        Path(sys.argv[1] if len(sys.argv) > 1 else "logs/pilot"),
        sys.argv[2] if len(sys.argv) > 2 else "openrouter/x-ai/grok-4.7",
    )
