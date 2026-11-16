"""Lecture 16: a failing task, what it stops, and the resumed run."""
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, scratch, workflow

logging.disable(logging.CRITICAL)   # the first run fails on purpose
BROKEN = "test -f calibration.txt && echo calibrated > outputs/qc.txt"
FIXED = "mkdir -p outputs && echo calibrated > outputs/qc.txt"


def build(base, checkpoint, qc_command):
    wf = workflow("Failures16", base, checkpoint_file=checkpoint)
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    wf.add_task(DagonTask(TaskType.BATCH, "qc", qc_command))
    wf.add_task(DagonTask(TaskType.BATCH, "plot",
                          "cat workflow:///qc/outputs/qc.txt > plot.txt"))
    wf.add_task(DagonTask(TaskType.BATCH, "archive",
                          "cp workflow:///fetch/outputs/observations.csv ."))
    return wf


with scratch("16") as base:
    checkpoint = str(base / "checkpoint.json")
    first = build(base, checkpoint, BROKEN)
    first.run()                                   # returns: no exception
    print("run 1:", {t.name: t.status.name for t in first.tasks})
    print("plot never started:", first.tasks[2].working_dir is None)

    second = build(base, checkpoint, FIXED)
    second.run(resume_checkpoint_file=checkpoint)
    print("run 2:", {t.name: t.status.name for t in second.tasks})
    reused = [b.name for a, b in zip(first.tasks, second.tasks)
              if a.working_dir and a.working_dir == b.working_dir]
    print("reused from run 1:", reused)
    check(all(t.status.name == "FINISHED" for t in second.tasks), "all done")
    check(reused == ["fetch", "archive"], "only successful tasks are reused")
