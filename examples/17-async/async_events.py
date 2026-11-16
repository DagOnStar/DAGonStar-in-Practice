"""Lecture 17: launch in the background and observe the lifecycle events."""
import sys
import threading
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, scratch, workflow

with scratch("17") as base:
    wf = workflow("Async17", base)
    wf.add_task(DagonTask(TaskType.BATCH, "fetch",
                          fetch_observations() + " && sleep 0.2"))
    wf.add_task(DagonTask(TaskType.BATCH, "count",
                          "wc -l < workflow:///fetch/outputs/observations.csv > n"))
    events, lock = [], threading.Lock()

    def record(name):
        def listener(subject):
            with lock:
                events.append((name, getattr(subject, "name", "?")))
        return listener

    for name in ("on_workflow_start", "on_task_start", "on_task_staging_in_start",
                 "on_task_execute_start", "on_task_end", "on_workflow_end"):
        wf.add_listener(name, record(name))

    thread = wf.launch()                     # returns immediately
    print("launched; caller is free:", thread.is_alive())
    finished = wf.wait(timeout=30)
    print("finished:", finished)
    for name, subject in events:
        if name in ("on_workflow_start", "on_workflow_end"):
            print("  %-26s %s" % (name, subject))
    for task in ("fetch", "count"):
        mine = [n for n, s in events if s == task]
        print("  %-5s %s" % (task, " > ".join(n[3:] for n in mine)))
    check(events[0][0] == "on_workflow_start", "start comes first")
    check(events[-1][0] == "on_workflow_end", "end comes last")
