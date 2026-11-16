"""Lecture 14: reference counting and the scratch garbage collector."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import (check, fetch_observations, scratch, station_mean,
                           workflow)

SOURCE = "workflow:///fetch/outputs/observations.csv"


def run(remove_dir):
    with scratch("14") as base:
        wf = workflow("Garbage14", base, remove_dir=remove_dir)
        fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations())
        wf.add_task(fetch)
        for s in ("NAP", "CAP"):
            wf.add_task(DagonTask(TaskType.BATCH, "mean_" + s, station_mean(
                s, SOURCE, "outputs/mean.txt")))
        wf.make_dependencies()
        print("remove_dir=%s: references to fetch before run: %d"
              % (remove_dir, fetch.reference_count))
        wf.run()
        names = sorted(p.name.split("-", 1)[1] for p in base.iterdir())
        print("  after run: references=%d, folders=%s"
              % (fetch.reference_count, names))
        return names


kept = run(False)
collected = run(True)
check(kept == ["fetch", "mean_CAP", "mean_NAP"], "nothing is collected")
check(all(name.endswith("-removed") for name in collected),
      "with remove_dir every consumed folder is renamed *-removed")
