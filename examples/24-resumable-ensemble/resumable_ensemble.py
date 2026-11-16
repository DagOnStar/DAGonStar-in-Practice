"""Lecture 24: a resumable ensemble, and the limit of name-based checkpoints."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, load, scratch, workflow

SOURCE = "workflow:///fetch/outputs/observations.csv"


def build(base, offsets):
    wf = workflow("Resumable24", base, checkpoint_file=str(base / "ck.json"))
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    for i, offset in enumerate(offsets):
        wf.add_task(DagonTask(TaskType.NATIVE, "member_%d" % i,
                              "common.weather:ensemble_member",
                              inputs={"observations": SOURCE, "offset": offset},
                              outputs={"member": "member.json"}))
    wf.add_task(DagonTask(TaskType.NATIVE, "statistics",
                          "common.weather:ensemble_statistics",
                          inputs={"m%d" % i: "workflow:///member_%d/outputs/"
                                  "member.json" % i for i in range(5)},
                          outputs={"statistics_file": "statistics.json"}))
    wf.run(resume_checkpoint_file=str(base / "ck.json"))
    return load(wf.tasks[-1], "outputs/statistics.json")


with scratch("24") as base:
    first = build(base, (-1.0, -0.5, 0.0, 0.5, 1.0))
    print("run 1:", first)
    again = build(base, (-1.0, -0.5, 0.0, 0.5, 1.0))
    print("run 2 (resumed, nothing re-runs):", again)
    changed = build(base, (-2.0, -1.0, 0.0, 1.0, 2.0))   # same task names!
    print("run 3 (new offsets, same names):", changed)
    check(changed == first, "the checkpoint trusts names, not content")

with scratch("24") as base:
    fresh = build(base, (-2.0, -1.0, 0.0, 1.0, 2.0))
    print("fresh checkpoint with the new offsets:", fresh)
    check(fresh["spread_c"] == 1.414, "a fresh run sees the new spread")
