"""Lecture 20: generate a workflow from parameters: one summary per station."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import (STATIONS, check, fetch_observations, load, scratch,
                           workflow)

SOURCE = "workflow:///fetch/outputs/observations.csv"

with scratch("20") as base:
    wf = workflow("Sweep20", base)
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    for station in STATIONS:                              # fan-out
        wf.add_task(DagonTask(
            TaskType.NATIVE, "summary_" + station,
            "common.weather:station_summary",
            inputs={"observations": SOURCE, "station": station},
            outputs={"summary": "summary.json"}))
    merge = DagonTask(                                    # fan-in
        TaskType.NATIVE, "merge", "common.weather:merge_summaries",
        inputs={key.lower(): "workflow:///summary_%s/outputs/summary.json" % key
                for key in STATIONS},
        outputs={"report": "report.json"})
    wf.add_task(merge)
    wf.run()

    print("generated:", [t.name for t in wf.tasks])
    for station in STATIONS:
        task = next(t for t in wf.tasks if t.name == "summary_" + station)
        print(" ", load(task, "outputs/summary.json"))
    print("report:", load(merge, "outputs/report.json"))
    check(load(merge, "outputs/report.json")["windiest"] == "CAP", "Capri")
