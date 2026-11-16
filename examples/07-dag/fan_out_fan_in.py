"""Lecture 07: a fan-out/fan-in DAG built with explicit control dependencies."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, scratch, workflow

with scratch("07") as base:
    log = base / "order.log"
    def step(name):
        return DagonTask(TaskType.BATCH, name, "echo %s >> '%s'" % (name, log))

    wf = workflow("Stations07", base)
    fetch, report = step("fetch"), step("report")
    analyses = [step("analyse_" + s) for s in ("NAP", "CAP", "ISC")]
    for task in [fetch, *analyses, report]:
        wf.add_task(task)
    for task in analyses:
        task.add_dependency_to(fetch)    # fetch -> analyse_*
        report.add_dependency_to(task)   # analyse_* -> report
    wf.Validate_WF()
    wf.run()

    order = log.read_text().split()
    print("fetch feeds:", sorted(t.name for t in fetch.nexts))
    print("report waits for:", sorted(t.name for t in report.prevs))
    print("first:", order[0], "| last:", order[-1], "| ran:", len(order))
    check(order[0] == "fetch" and order[-1] == "report", "the DAG order holds")
