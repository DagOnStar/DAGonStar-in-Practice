"""Lecture 21: an ensemble of perturbed members and a fan-in statistic."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, load, scratch, workflow

OFFSETS = (-1.0, -0.5, 0.0, 0.5, 1.0)
SOURCE = "workflow:///fetch/outputs/observations.csv"

with scratch("21") as base:
    wf = workflow("Ensemble21", base)
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    for index, offset in enumerate(OFFSETS):
        wf.add_task(DagonTask(
            TaskType.NATIVE, "member_%d" % index, "common.weather:ensemble_member",
            inputs={"observations": SOURCE, "offset": offset},
            outputs={"member": "member.json"}))
    stats = DagonTask(
        TaskType.NATIVE, "statistics", "common.weather:ensemble_statistics",
        inputs={"m%d" % i: "workflow:///member_%d/outputs/member.json" % i
                for i in range(len(OFFSETS))},
        outputs={"statistics_file": "statistics.json"})
    wf.add_task(stats)
    wf.run()

    for task in wf.tasks[1:-1]:
        print(" ", task.name, load(task, "outputs/member.json"))
    result = load(stats, "outputs/statistics.json")
    print("statistics waits for", len(stats.prevs), "members:", result)
    check(result == {"members": 5, "ensemble_mean_c": 16.0, "spread_c": 0.707},
          "mean 16.0, spread sqrt(0.5)")
