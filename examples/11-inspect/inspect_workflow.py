"""Lecture 11: serialise a workflow to JSON, reload it, time it, observe it."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon import Workflow
from dagon.task import DagonTask, TaskType
from common.course import check, config, fetch_observations, scratch, workflow

with scratch("11") as base:
    wf = workflow("Inspect11", base)
    fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations())
    count = DagonTask(TaskType.BATCH, "count",
                      "wc -l < workflow:///fetch/outputs/observations.csv > n.txt")
    plot = DagonTask(TaskType.BATCH, "plot", "echo placeholder > plot.txt")
    for task in (fetch, count, plot):
        wf.add_task(task)
    plot.add_dependency_to(count)            # explicit edge, no file passed

    document = wf.as_json()
    (base / "workflow.json").write_text(json.dumps(document, indent=2))
    print("JSON keys:", sorted(document), "| tasks:", list(document["tasks"]))
    print("count as JSON:", {k: document["tasks"]["count"][k]
                              for k in ("name", "type")})

    copy = Workflow("placeholder", config=config(base),
                    jsonload=json.loads((base / "workflow.json").read_text()))
    copy.make_dependencies()
    print("reloaded:", copy.name, [t.name for t in copy.tasks],
          "| plot after:", [t.name for t in copy.tasks[2].prevs])

    ended = []
    wf.add_listener("on_task_end", lambda task: ended.append(task.name))
    wf.run()
    times = wf.get_task_times()
    print("ended:", len(ended), "tasks | timed:", sorted(times))
    check(all(t >= 0 for t in times.values()), "every task has a duration")
