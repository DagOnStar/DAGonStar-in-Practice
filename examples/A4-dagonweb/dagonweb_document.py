"""Appendix A4: a DAGonWeb workflow document, loaded and run by DAGonStar alone.

DAGonWeb saves what you draw as a DAGonStar task-map document; editor state lives only in
additive "dagonweb" keys.  This script writes such a document for the station pipeline by
hand, with the conventions DAGonWeb uses (named inputs prepended as shell assignments, one
explicit dependency in explicit_prevs), and runs it the way DAGonWeb's executor does:
load the document, apply the runtime options, run with a checkpoint.  The first run fails
on a typo in report; the "fixed" document is resumed, as DAGonWeb's Resume button does.
No web server is started: DAGonWeb itself is not needed to run its documents.
"""
import json
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon import Workflow
from common.course import STATIONS, check, config, fetch_observations, scratch, text

logging.disable(logging.CRITICAL)                # the first run fails on purpose
OBS = "workflow:///fetch/outputs/observations.csv"
AWK = "awk -F, -v s={s} '$1==s{{t+=$3;n++}}END{{printf \"%s %.2f\\n\", s, t/n}}' $obs > {s}.txt"


def task(name, script, inputs=None, explicit=(), x=0, y=0):
    """One task as DAGonWeb stores it: the runtime command, plus the editor's own state."""
    inputs = inputs or {}
    assignments = "".join("%s=%s ;\n" % item for item in inputs.items())
    return {"name": name, "type": "batch", "command": assignments + script,
            "explicit_prevs": list(explicit), "prevs": [], "nexts": [],
            "dagonweb": {"x": x, "y": y, "config": {"command": script, "inputs": inputs}}}


def document(report_command):
    tasks = [task("fetch", fetch_observations(), x=120, y=220)]
    tasks += [task("mean_" + s, AWK.format(s=s), {"obs": OBS}, x=400, y=120 + 100 * i)
              for i, s in enumerate(STATIONS)]
    tasks.append(task("report", report_command, x=680, y=220))
    tasks.append(task("notify", "echo report ready > notice.txt", explicit=["report"], x=900, y=220))
    return {"name": "Stations", "id": None, "host": "localhost",
            "tasks": {t["name"]: t for t in tasks},
            "dagonweb": {"runtime": {"max_threads": 4, "portable_emulation": False}}}


def run(doc, base, checkpoint, resume=False):
    """What DAGonWeb's executor does with a saved document."""
    runtime = doc["dagonweb"]["runtime"]
    wf = Workflow(doc["name"], config=config(base), max_threads=runtime["max_threads"],
                  portable_emulation=runtime["portable_emulation"], checkpoint_file=checkpoint,
                  jsonload=doc)
    wf.make_dependencies()
    wf.run(resume_checkpoint_file=checkpoint if resume else None)
    return wf, {t.name: t for t in wf.tasks}


REPORT = "cat " + " ".join("workflow:///mean_%s/%s.txt" % (s, s) for s in STATIONS) + " > report.txt"

with scratch("A4") as base:
    checkpoint = str(base / "checkpoint.json")
    broken = document(REPORT.replace("cat ", "catt ", 1))         # a typo made in the editor
    (base / "stations.json").write_text(json.dumps(broken, indent=2))
    print("document keys:", sorted(broken), "| mean_CAP command:")
    print("  " + broken["tasks"]["mean_CAP"]["command"].replace("\n", "\n  "))

    first, t1 = run(json.loads((base / "stations.json").read_text()), base, checkpoint)
    print("data edges into report:", sorted(p.name for p in t1["report"].prevs))
    print("notify runs after:", [p.name for p in t1["notify"].prevs], "(explicit, no data)")
    print("run 1:", {name: t.status.name for name, t in t1.items()})
    check(t1["report"].status.name == "FAILED", "a non-zero exit status fails the task")
    check(t1["notify"].status.name == "FAILED", "and its dependants")

    second, t2 = run(document(REPORT), base, checkpoint, resume=True)  # fixed, then Resume
    print("run 2:", {name: t.status.name for name, t in t2.items()})
    reused = sorted(n for n in t1 if t1[n].working_dir and t1[n].working_dir == t2[n].working_dir)
    print("reused from run 1:", reused)
    print("report:", text(t2["report"], "report.txt").strip().replace("\n", " | "))
    saved = second.as_json()["tasks"]["notify"]
    print("as_json keeps the explicit edge:", saved["explicit_prevs"])
    check(reused == ["fetch", "mean_CAP", "mean_ISC", "mean_NAP"], "only the finished tasks are reused")
    check(text(t2["report"], "report.txt") == "NAP 15.50\nCAP 16.75\nISC 15.75\n", "station means")
    check(saved["explicit_prevs"] == ["report"], "explicit dependency survives the round trip")
