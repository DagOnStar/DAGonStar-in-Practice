"""Lecture 18: a native task runs an importable Python function."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, load, scratch, workflow

with scratch("18") as base:
    wf = workflow("Native18", base)
    fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations())
    mean = DagonTask(
        TaskType.NATIVE, "mean", "common.weather:mean_temperature",
        inputs={"observations": "workflow:///fetch/outputs/observations.csv"},
        outputs={"result": "mean.json"})
    wf.add_task(fetch)
    wf.add_task(mean)
    wf.run()

    print("type:", type(mean).__name__, "| after:", [t.name for t in mean.prevs])
    spec = load(mean, ".dagon/native_spec.json")
    print("bindings:", json.dumps(spec["inputs"]), json.dumps(spec["outputs"]))
    print("outputs/mean.json:", load(mean, "outputs/mean.json"))
    print("return value:", load(mean, ".dagon/native_result.json"))
    check(load(mean, "outputs/mean.json") == {"mean_temperature_c": 16.0},
          "the mean of the twelve records is 16.0")
