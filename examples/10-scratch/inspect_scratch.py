"""Lecture 10: what DAGonStar leaves in a task's working directory."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import (check, fetch_observations, scratch, station_mean,
                           workflow)

with scratch("10") as base:
    wf = workflow("Scratch10", base)
    fetch = DagonTask(TaskType.BATCH, "fetch",
                      fetch_observations() + " && echo copied 12 records")
    mean = DagonTask(TaskType.BATCH, "mean", station_mean(
        "NAP", "workflow:///fetch/outputs/observations.csv", "outputs/mean.txt"))
    wf.add_task(fetch)
    wf.add_task(mean)
    wf.run()

    folder = Path(mean.working_dir)
    print("files of the consumer task:")
    for path in sorted(folder.rglob("*")):
        if path.is_file():
            print("  ", path.relative_to(folder).as_posix())
    print("stdout of the producer:",
          Path(fetch.working_dir, ".dagon", "stdout.txt").read_text().strip())
    launcher = (folder / ".dagon" / "launcher.sh").read_text()
    steps = [line[2:] for line in launcher.splitlines()
             if line.startswith("# ") and "DagOn" not in line]
    print("launcher steps:", " | ".join(steps))
    command = next(l for l in launcher.splitlines() if l.startswith("mkdir -p outputs && awk"))
    staged = next(w for w in command.split() if w.endswith(".csv"))
    print("rewritten input:", staged.replace(str(folder), "<task>"))
    check("# Invoke the command" in launcher, "the launcher is kept for audit")
