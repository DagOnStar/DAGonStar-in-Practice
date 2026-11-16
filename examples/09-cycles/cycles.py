"""Lecture 09: a cycle is rejected before anything runs, then repaired."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, scratch, workflow

with scratch("09") as base:
    wf = workflow("Cycle09", base)
    simulate = DagonTask(TaskType.BATCH, "simulate", "echo sim > sim.txt")
    assimilate = DagonTask(TaskType.BATCH, "assimilate", "echo da > da.txt")
    forecast = DagonTask(TaskType.BATCH, "forecast", "echo fc > fc.txt")
    for task in (simulate, assimilate, forecast):
        wf.add_task(task)
    assimilate.add_dependency_to(simulate)
    forecast.add_dependency_to(assimilate)
    simulate.add_dependency_to(forecast)        # the next cycle's initial state

    try:
        wf.Validate_WF()
    except Exception as error:
        print("rejected:", error)
        rejected = True
    else:
        rejected = False
    check(rejected, "a cycle must be rejected")

    simulate.remove_dependency_to(forecast)     # break the back edge
    wf.Validate_WF()
    wf.run()
    print("repaired; ran:", [t.name for t in wf.tasks if t.status.name == "FINISHED"])
    check(all(t.status.name == "FINISHED" for t in wf.tasks), "all tasks ran")
