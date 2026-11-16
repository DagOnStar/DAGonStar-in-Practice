"""Lecture 19: scalar inputs, environment variables and a failing function."""
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import (check, fetch_observations, load, scratch, text,
                           workflow)

logging.disable(logging.CRITICAL)   # the last task fails on purpose
SOURCE = "workflow:///fetch/outputs/observations.csv"

with scratch("19") as base:
    wf = workflow("Bindings19", base)
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    knots = DagonTask(TaskType.NATIVE, "to_knots", "common.weather:scale_wind",
                      inputs={"observations": SOURCE, "factor": 1.943844,
                              "unit": "kn"},
                      outputs={"scaled": "wind_kn.csv"},
                      environment={"COURSE_LABEL": "lecture-19"})
    broken = DagonTask(TaskType.NATIVE, "calibrate",
                       "common.weather:always_fails",
                       inputs={"observations": SOURCE})
    wf.add_task(knots)
    wf.add_task(broken)
    wf.run()

    print("returned:", load(knots, ".dagon/native_result.json"))
    print("first rows:", text(knots, "outputs/wind_kn.csv").splitlines()[:2])
    print("calibrate:", broken.status.name)
    error = text(broken, ".dagon/native_stderr.txt").strip().splitlines()[-1]
    print("its stderr ends with:", error)
    try:
        DagonTask(TaskType.NATIVE, "typo", "common.weather:scale_wind",
                  inputs={"observations": SOURCE, "factr": 2})
    except ValueError as exc:
        print("rejected at construction:", str(exc)[:60])
    check(knots.status.name == "FINISHED" and broken.status.name == "FAILED",
          "one success and one failure")
