"""Lecture 12: the Gulf of Naples station pipeline, end to end."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import (STATIONS, check, fetch_observations, scratch, text,
                           workflow)

SOURCE = "workflow:///fetch/outputs/observations.csv"
SUMMARY = ("mkdir -p outputs && awk -F, -v s=%s '$1==s{t+=$3;n++;"
           "if($4>w)w=$4}END{printf \"%%s %%.2f %%.1f\\n\", s, t/n, w}' "
           "%s > outputs/summary.txt")

with scratch("12") as base:
    wf = workflow("GulfOfNaples12", base)
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    for s in STATIONS:
        wf.add_task(DagonTask(TaskType.BATCH, "summary_" + s,
                              SUMMARY % (s, SOURCE)))
    parts = " ".join("workflow:///summary_%s/outputs/summary.txt" % s
                     for s in STATIONS)
    report = DagonTask(TaskType.BATCH, "report",
                       "cat %s | sort -k3 -n -r > report.txt" % parts)
    wf.add_task(report)
    wf.make_dependencies()
    wf.Validate_WF()

    events = []
    wf.add_listener("on_task_end", lambda task: events.append(task.name))
    wf.run()

    rows = [line.split() for line in text(report, "report.txt").splitlines()]
    print("station  mean_c  max_wind")
    for station, mean, wind in rows:
        print("%-8s %6s %9s" % (station, mean, wind))
    print("windiest:", rows[0][0], "| tasks ended:", len(events))
    (base / "pipeline.json").write_text(json.dumps(wf.as_json()))
    check(rows[0] == ["CAP", "16.75", "8.0"], "Capri is the windiest")
    check(len(events) == 5, "five tasks ran")
