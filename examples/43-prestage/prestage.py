"""Lecture 43: stage inputs before sbatch, verify them, and never submit
when stage-in fails (local stand-in for sbatch)."""
import logging
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.batch import Batch, Slurm
from dagon.prestage import PreStageConfigurationError
from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, scratch, workflow
from common.mock_scheduler import mock_sbatch, submission_for

logging.disable(logging.CRITICAL)    # the induced failure logs an error
refused = []
plain = Batch("b", "true")
plain.pre_stage = True               # requested on a backend without the capability
for label, task in (("batch", plain), ("beeond", Slurm("s", "true", beeond="task",
                                                        pre_stage=True))):
    try:
        workflow("eligibility-" + label, tempfile.gettempdir()).add_task(task)
    except PreStageConfigurationError:
        refused.append(label)
print("ineligible requests refused:", refused)


def run(base, reference):
    log = str(base / "sbatch.jsonl")
    wf = workflow("PreStage43", base, pre_stage=True)
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    model = DagonTask(TaskType.SLURM, "wrf", "wc -l < " + reference + " > n.txt", ntasks=8)
    wf.add_task(model)
    with mock_sbatch(log):
        wf.run()
    return model, submission_for(log, "wrf")


with scratch("43") as base:
    model, submission = run(base, "workflow:///fetch/outputs/observations.csv")
    meta = model.get_execution_metadata()["pre_stage"]
    print("ok run:", model.status.name, "| marker before sbatch:",
          submission["marker_present"], "| verified inputs:", meta["inputs_content_verified"])
    print("metadata is path-free:", str(base) not in str(meta))

with scratch("43") as base:
    model, submission = run(base, "workflow:///fetch/outputs/missing.csv")
    print("bad run:", model.status.name, "| phase:", model.failure_phase,
          "| sbatch called:", submission is not None)
    check(submission is None, "sbatch never runs after a failed stage-in")
