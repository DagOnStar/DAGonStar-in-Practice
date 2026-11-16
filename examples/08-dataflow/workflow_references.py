"""Lecture 08: a data dependency expressed with a workflow:// reference."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import (check, fetch_observations, scratch, station_mean,
                           text, workflow)

with scratch("08") as base:
    wf = workflow("Stations08", base)
    fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations())
    mean = DagonTask(TaskType.BATCH, "mean_CAP", station_mean(
        "CAP", "workflow:///fetch/outputs/observations.csv", "outputs/mean.txt"))
    wf.add_task(fetch)
    wf.add_task(mean)
    print("prevs before make_dependencies:", mean.prevs)
    wf.make_dependencies()
    print("prevs after make_dependencies:", [t.name for t in mean.prevs])
    wf.run()

    staged = next(Path(mean.working_dir, ".dagon", "inputs").rglob("*.csv"))
    print("staged copy:", staged.relative_to(mean.working_dir).as_posix())
    print("result:", text(mean, "outputs/mean.txt").strip())
    check(text(mean, "outputs/mean.txt").strip() == "CAP 16.75", "Capri mean")
