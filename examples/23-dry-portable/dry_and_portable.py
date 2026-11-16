"""Lecture 23: a dry run plans without executing; portable emulation runs
scheduler tasks locally, without sbatch."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import (check, fetch_observations, scratch, station_mean,
                           text, workflow)

SOURCE = "workflow:///fetch/outputs/observations.csv"

with scratch("23") as base:
    dry = workflow("Dry23", base)
    dry.set_dry(True)
    fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations())
    dry.add_task(fetch)
    dry.run()
    made = sorted(p.name for p in Path(fetch.working_dir).iterdir())
    print("dry run:", fetch.status.name, "| folder holds only", made)
    check(made == [".dagon"], "nothing was executed")

with scratch("23") as base:
    portable = workflow("Portable23", base, portable_emulation=True)
    portable.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    model = DagonTask(TaskType.SLURM, "mean_ISC",
                      station_mean("ISC", SOURCE, "outputs/mean.txt"),
                      partition="compute", ntasks=4, time="00:10:00")
    portable.add_task(model)
    portable.run()
    print("portable:", type(model).__name__, model.status.name,
          "| result:", text(model, "outputs/mean.txt").strip())
    check(text(model, "outputs/mean.txt").strip() == "ISC 15.75", "Ischia")
