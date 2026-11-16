"""Lecture 15: record a checkpoint, then resume without re-running tasks."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import (check, fetch_observations, scratch, station_mean,
                           workflow)

SOURCE = "workflow:///fetch/outputs/observations.csv"

with scratch("15") as base:
    checkpoint = str(base / "checkpoint.json")
    runs = base / "executions.log"

    def build():
        wf = workflow("Checkpoint15", base, checkpoint_file=checkpoint)
        wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()
                              + " && echo fetch >> '%s'" % runs))
        wf.add_task(DagonTask(TaskType.BATCH, "mean", station_mean(
            "NAP", SOURCE, "outputs/mean.txt") + " && echo mean >> '%s'" % runs))
        return wf

    first = build()
    first.run()
    record = json.loads(Path(checkpoint).read_text())
    print("checkpoint keys:", sorted(record))
    print("fetch record:", {k: record["Checkpoint15.fetch"][k]
                            for k in ("name", "workflow", "code")})

    second = build()
    second.run(resume_checkpoint_file=checkpoint)
    same = [a.working_dir == b.working_dir
            for a, b in zip(first.tasks, second.tasks)]
    print("executions:", runs.read_text().split())
    print("second run reused the folders:", same)
    check(runs.read_text().split() == ["fetch", "mean"], "each ran once")
