"""Lecture 46: a deterministic CWL v1.2 export: file edges, ordering edges,
no scratch paths, and validation with cwltool when it is installed."""
import json
import shutil
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, scratch, station_mean, workflow


def build(base):
    wf = workflow("Cwl46", base)
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    wf.add_task(DagonTask(TaskType.BATCH, "mean_ISC", station_mean(
        "ISC", "workflow:///fetch/outputs/observations.csv", "outputs/mean.txt")))
    notify = DagonTask(TaskType.BATCH, "notify", "echo done > done.txt")
    wf.add_task(notify)
    notify.add_dependency_to(wf.find_task_by_name("Cwl46", "mean_ISC"))  # order only
    return wf


with scratch("46") as base:
    first, second = base / "a.cwl", base / "b.cwl"
    build(base).saveAsCWL(str(first))
    build(base).saveAsCWL(str(second))
    document = json.loads(first.read_text())
    print("cwlVersion:", document["cwlVersion"], "| class:", document["class"])
    print("steps:", sorted(document["steps"]))
    print("deterministic:", first.read_text() == second.read_text(),
          "| scratch path exported:", str(base) in first.read_text())
    print("mean_ISC inputs:", sorted(document["steps"]["mean_ISC"]["in"]))
    print("notify inputs:", sorted(document["steps"]["notify"]["in"]))
    if shutil.which("cwltool"):
        done = subprocess.run(["cwltool", "--validate", str(first)],
                              capture_output=True, text=True)
        print("cwltool --validate:", "ok" if done.returncode == 0 else done.stderr[-300:])
        check(done.returncode == 0, "the export is valid CWL")
    else:
        print("cwltool not installed: validation skipped (pip install cwltool)")
