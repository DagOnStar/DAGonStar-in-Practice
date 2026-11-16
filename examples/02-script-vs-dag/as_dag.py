"""Lecture 02: the same analysis as a script and as a DAG of tasks."""
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import (STATIONS, check, fetch_observations, scratch,
                           station_mean, text, workflow)

HERE = Path(__file__).resolve().parent
SOURCE = "workflow:///fetch/outputs/observations.csv"

with scratch("02") as base:
    subprocess.run(["bash", str(HERE / "pipeline.sh"), str(base / "script")],
                   check=True)
    script_report = (base / "script" / "report.txt").read_text()

    wf = workflow("Stations02", base)
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    for s in STATIONS:
        wf.add_task(DagonTask(TaskType.BATCH, "mean_" + s,
                              station_mean(s, SOURCE, "outputs/mean.txt")))
    inputs = " ".join("workflow:///mean_%s/outputs/mean.txt" % s
                      for s in STATIONS)
    report = DagonTask(TaskType.BATCH, "report", "cat %s > report.txt" % inputs)
    wf.add_task(report)
    wf.run()

    dag_report = text(report, "report.txt")
    print(dag_report, end="")
    print("tasks:", len(wf.tasks))
    print("report waits for:", sorted(t.name for t in report.prevs))
    print("script and DAG agree:", dag_report == script_report)
    check(dag_report == script_report, "the two versions must agree")
