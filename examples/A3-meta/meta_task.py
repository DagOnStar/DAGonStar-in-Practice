"""Appendix A3: meta-tasks - run workflows written for other engines as DAGonStar tasks.

    fetch -> means (TaskType.META, command adapter: engines/station_engine.py) -> warmest
    fetch -> records (TaskType.META, cwl adapter: engines/count_records.cwl, run by cwltool)

Data moves only through workflow:// references; the engines are never modified.  A second
run with the same checkpoint file reuses the meta-task after re-verifying its specification,
workflow and data digests.  A Nextflow meta-task then runs under portable emulation: the mock
engine writes placeholders, so neither Nextflow nor a network connection is needed.  The CWL
step needs cwltool (pip install cwltool) and is skipped without it.
"""
import json
import shutil
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon import Status
from dagon.meta import MetaValidationError
from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, scratch, text, workflow

ENGINES = Path(__file__).resolve().parent / "engines"
OBS = "workflow:///fetch/outputs/observations.csv"


def build(base, checkpoint):
    wf = workflow("Meta", base, checkpoint_file=checkpoint)
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    wf.add_task(DagonTask(
        TaskType.META, "means", engine="command", workflow=str(ENGINES / "station_engine.py"),
        inputs={"observations": OBS, "stations": ["NAP", "CAP", "ISC"]},
        outputs={"means": {"path": "means.csv", "source": "results/means.csv"}},
        engine_options={"command": [sys.executable, "{workflow}", "{parameters_file}"]}))
    wf.add_task(DagonTask(TaskType.BATCH, "warmest",
                          "tail -n +2 workflow:///means/outputs/means.csv | sort -t, -k2 -nr | head -n 1 > warmest.txt"))
    if shutil.which("cwltool"):
        wf.add_task(DagonTask(
            TaskType.META, "records", engine="cwl", workflow=str(ENGINES / "count_records.cwl"),
            inputs={"observations": OBS},
            outputs={"records": {"path": "records.txt", "engine_output": "records"}}))
    return wf


with scratch("A3") as base:
    checkpoint = str(base / "checkpoint.json")
    first = build(base, checkpoint)
    first.run(checkpoint)
    check(all(t.status is Status.FINISHED for t in first.tasks), "every task finished")
    means = first.find_task_by_name("Meta", "means")
    warmest = first.find_task_by_name("Meta", "warmest")
    result = means.meta_result
    print("engine:", result["engine"], "| outputs:", [o["path"] for o in result["outputs"]])
    print("means.csv:", text(means, "outputs/means.csv").strip().replace("\n", " | "))
    print("warmest:", text(warmest, "warmest.txt").strip())
    check(text(warmest, "warmest.txt").strip() == "CAP,16.75", "Capri is the warmest station")
    records = first.find_task_by_name("Meta", "records")
    if records is not None:
        print("cwltool counted", text(records, "outputs/records.txt").strip(), "records")
        check(text(records, "outputs/records.txt").strip() == "12", "12 data records")
    else:
        print("cwltool not installed: the CWL meta-task was skipped (pip install cwltool)")

    second = build(base, checkpoint)
    second.run(checkpoint)
    reused = second.find_task_by_name("Meta", "means")
    print("second run reused the meta-task:", bool(reused.fair_checkpoint_reused))
    check(reused.fair_checkpoint_reused and reused.working_dir == means.working_dir, "verified reuse")

    try:
        DagonTask(TaskType.META, "leaky", engine="nextflow", workflow="nextflow-io/hello",
                  engine_options={"api_token": "secret"})
    except MetaValidationError as error:
        print("refused at construction:", type(error).__name__)

    emulated = workflow("MetaEmulated", base / "emulated", portable_emulation=True)
    emulated.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    emulated.add_task(DagonTask(TaskType.META, "ocean", engine="nextflow", workflow="nextflow-io/hello",
                                inputs={"observations": OBS}, outputs={"summary": "results/summary.json"}))
    emulated.run()
    ocean = emulated.find_task_by_name("MetaEmulated", "ocean")
    placeholder = json.loads(text(ocean, "outputs/results/summary.json"))
    print("emulated:", ocean.meta_result["emulated"], "| placeholder for engine:", placeholder["engine"])
    check(ocean.status is Status.FINISHED and ocean.meta_result["emulated"], "mock engine stood in")
