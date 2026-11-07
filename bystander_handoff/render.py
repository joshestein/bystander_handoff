"""render(cell, seed): everything the subject sees, assembled in a fixed order.

Knows nothing about tasks or Inspect. Tasks wrap the result with a system
prompt or a question.
"""

from dataclasses import dataclass

from bystander_handoff.cell import Cell
from bystander_handoff.predecessors import StageReport, reports
from bystander_handoff.scenario import deploy_log, read_scenario

REPORTS_SECTION = "stage reports"
BUILD_STAGES_PLACEHOLDER = "{build_stages}"


@dataclass(frozen=True)
class Rendered:
    files: dict[str, str]  # in the order the subject sees them
    reports: tuple[StageReport, ...]
    context: str

    @property
    def manifest(self) -> str:
        return self.files["pipeline.yaml"]


def render(cell: Cell, seed: int) -> Rendered:
    stage_reports = reports(cell, seed)
    files = {
        "pipeline.yaml": _manifest(stage_reports),
        "deploy_config.yaml": read_scenario("deploy_config.yaml"),
        "endpoints-allowlist.yaml": read_scenario("endpoints-allowlist.yaml"),
        "deploy.log": deploy_log(cell.ambiguity),
    }
    return Rendered(files, stage_reports, _context(files, stage_reports))


def _manifest(stage_reports: tuple[StageReport, ...]) -> str:
    """pipeline_base.yaml with the build stages substituted in."""
    entries = "\n".join(
        f"  - name: {r.stage}\n"
        f"    inputs: [{', '.join(r.inputs)}]\n"
        f"    outputs: [artifacts/{r.service}-2.14.0.tar]"
        for r in stage_reports
    )
    base = read_scenario("pipeline_base.yaml")
    # The placeholder is on its own line; drop that line entirely at k=0.
    replacement = f"{entries}\n" if entries else ""
    return base.replace(f"{BUILD_STAGES_PLACEHOLDER}\n", replacement)


def _context(files: dict[str, str], stage_reports: tuple[StageReport, ...]) -> str:
    sections = [f"=== {name} ===\n{body.rstrip()}\n" for name, body in files.items()]
    if stage_reports:
        body = "\n\n".join(r.text for r in stage_reports)
        sections.append(f"=== {REPORTS_SECTION} ===\n{body}\n")
    return "\n".join(sections)
