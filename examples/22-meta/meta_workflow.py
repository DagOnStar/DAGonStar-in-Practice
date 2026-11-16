"""Lecture 22: two workflows composed by DAG_TPS with a cross-workflow reference."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.dag_tps import DAG_TPS
from dagon.task import DagonTask, TaskType
from common.course import (check, config, fetch_observations, scratch,
                           station_mean, text, workflow)

with scratch("22") as base:
    campaign = DAG_TPS("Campaign22", config=config(base))
    acquisition = workflow("Acquisition", base)
    analysis = workflow("Analysis", base)
    fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations())
    mean = DagonTask(TaskType.BATCH, "mean_CAP", station_mean(
        "CAP", "workflow://Acquisition/fetch/outputs/observations.csv",
        "outputs/mean.txt"))
    acquisition.add_task(fetch)
    analysis.add_task(mean)
    campaign.add_workflow(acquisition)
    campaign.add_workflow(analysis)
    campaign.make_dependencies()
    print("Analysis.mean_CAP waits for:",
          [(t.workflow.name, t.name) for t in mean.prevs])
    campaign.run()
    print("result:", text(mean, "outputs/mean.txt").strip())

    alone = workflow("Alone", base)
    alone.add_task(DagonTask(TaskType.BATCH, "orphan",
                             "cat workflow://Missing/fetch/out.csv"))
    try:
        alone.make_dependencies()
    except ConnectionError as error:
        print("unresolved without DAG_TPS or the service:", error)
    check(text(mean, "outputs/mean.txt").strip() == "CAP 16.75", "Capri")
