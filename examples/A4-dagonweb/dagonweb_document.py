"""Appendix A4: a DAGonWeb workflow document, loaded and run by DAGonStar.

DAGonWeb saves what you draw as a DAGonStar task-map document; editor state
lives only in additive "dagonweb" keys.  This script writes such a document
for the station pipeline by hand, with the conventions DAGonWeb uses (named
inputs prepended as shell assignments, one explicit dependency in
explicit_prevs), and runs it the way DAGonWeb's executor does: load the
document, apply the runtime options, run with a checkpoint.  The first run
fails on a typo in report; the "fixed" document is resumed, as DAGonWeb's
Resume button does.  No web server is started: DAGonWeb itself is not needed
to run its documents.
"""
import json
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon import Workflow
from common.course import (STATIONS, check, config, fetch_observations,
                           scratch, text)

logging.disable(logging.CRITICAL)        # the first run fails on purpose
OBS = "workflow:///fetch/outputs/observations.csv"
AWK = ("awk -F, -v s={s} '$1==s{{t+=$3;n++}}"
       "END{{printf \"%s %.2f\\n\", s, t/n}}' $obs > {s}.txt")
REPORT = "cat " + " ".join(
    "workflow:///mean_%s/%s.txt" % (s, s) for s in STATIONS) + " > report.txt"


def task(name, script, inputs=None, explicit=(), x=0, y=0):
    """One task as DAGonWeb stores it: command plus editor state."""
    inputs = inputs or {}
    assign = "".join("%s=%s ;\n" % item for item in inputs.items())
    return {"name": name, "type": "batch",
            "command": assign + script,
            "explicit_prevs": list(explicit), "prevs": [], "nexts": [],
            "dagonweb": {"x": x, "y": y,
                         "config": {"command": script,
                                    "inputs": inputs}}}


def document(report_command):
    tasks = [task("fetch", fetch_observations(), x=120, y=220)]
    tasks += [task("mean_" + s, AWK.format(s=s), {"obs": OBS},
                   x=400, y=120 + 100 * i)
              for i, s in enumerate(STATIONS)]
    tasks.append(task("report", report_command, x=680, y=220))
    tasks.append(task("notify", "echo report ready > notice.txt",
                      explicit=["report"], x=900, y=220))
    return {"name": "Stations", "id": None, "host": "localhost",
            "tasks": {t["name"]: t for t in tasks},
            "dagonweb": {"runtime": {"max_threads": 4,
                                     "portable_emulation": False}}}


def run(doc, base, checkpoint, resume=False):
    """What DAGonWeb's executor does with a saved document."""
    runtime = doc["dagonweb"]["runtime"]
    wf = Workflow(doc["name"], config=config(base),
                  max_threads=runtime["max_threads"],
                  portable_emulation=runtime["portable_emulation"],
                  checkpoint_file=checkpoint, jsonload=doc)
    wf.make_dependencies()
    wf.run(resume_checkpoint_file=checkpoint if resume else None)
    return wf, {t.name: t for t in wf.tasks}


def failed(tasks):
    return [n for n, t in tasks.items() if t.status.name == "FAILED"]


def names(tasks):
    return " ".join(sorted(t.name for t in tasks))


with scratch("A4") as base:
    checkpoint = str(base / "checkpoint.json")
    broken = document(REPORT.replace("cat ", "catt ", 1))   # a typo
    (base / "stations.json").write_text(json.dumps(broken, indent=2))
    assign, script = broken["tasks"]["mean_CAP"]["command"].split("\n")
    print("mean_CAP command (awk program elided):")
    print("  " + assign)
    print("  " + script.split("'")[0] + "'...'" + script.split("'")[-1])

    doc = json.loads((base / "stations.json").read_text())
    first, t1 = run(doc, base, checkpoint)
    print("report after:", names(t1["report"].prevs))
    print("notify after:", names(t1["notify"].prevs), "(explicit)")
    print("run 1 failed:", failed(t1))
    check(failed(t1) == ["report", "notify"],
          "a non-zero exit fails the task and its dependants")

    second, t2 = run(document(REPORT), base, checkpoint, resume=True)
    print("run 2 failed:", failed(t2))
    reused = sorted(n for n in t1 if t1[n].working_dir
                    and t1[n].working_dir == t2[n].working_dir)
    print("reused:", " ".join(reused))
    means = text(t2["report"], "report.txt").strip().replace("\n", " | ")
    print("report:", means)
    saved = second.as_json()["tasks"]["notify"]
    print("as_json explicit_prevs:", saved["explicit_prevs"])
    check(reused == ["fetch", "mean_CAP", "mean_ISC", "mean_NAP"],
          "only the finished tasks are reused")
    check(means == "NAP 15.50 | CAP 16.75 | ISC 15.75", "station means")
    check(saved["explicit_prevs"] == ["report"],
          "explicit dependency survives the round trip")
