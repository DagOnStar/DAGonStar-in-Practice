"""Lecture 01: the smallest useful workflow, one task that fetches the data."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, scratch, text, workflow

with scratch("01") as base:
    wf = workflow("Hello01", base)
    fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations())
    wf.add_task(fetch)
    wf.run()

    lines = text(fetch, "outputs/observations.csv").splitlines()
    print("status:", fetch.status.name)
    print("records fetched:", len(lines) - 1)
    print("header:", lines[0])
    check(fetch.status.name == "FINISHED", "the task must finish")
    check(len(lines) == 13, "12 records and a header")
