"""Lecture 13: COPY, LINK and DONTMOVE: how an input reaches the consumer."""
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon import DataMover
from dagon.task import DagonTask, TaskType
from common.course import (check, fetch_observations, scratch, station_mean,
                           workflow)

logging.disable(logging.CRITICAL)   # the DONTMOVE run fails on purpose
SOURCE = "workflow:///fetch/outputs/observations.csv"


def run(mover):
    with scratch("13") as base:
        wf = workflow("Staging13", base)
        wf.set_data_mover(mover)
        fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations())
        mean = DagonTask(TaskType.BATCH, "mean",
                         station_mean("ISC", SOURCE, "outputs/mean.txt"))
        wf.add_task(fetch)
        wf.add_task(mean)
        wf.run()
        staged = list(Path(mean.working_dir, ".dagon", "inputs").rglob("*.csv"))
        kind = ("none" if not staged else
                "symlink" if staged[0].is_symlink() else "copy")
        print("%-8s staged=%-7s consumer=%s" % (mover.name, kind, mean.status.name))
        return kind, mean.status.name


results = {mover.name: run(mover)
           for mover in (DataMover.COPY, DataMover.LINK, DataMover.DONTMOVE)}
check(results["COPY"] == ("copy", "FINISHED"), "COPY materialises a copy")
check(results["LINK"] == ("symlink", "FINISHED"), "LINK creates a symlink")
check(results["DONTMOVE"] == ("none", "FAILED"), "DONTMOVE moves nothing")
