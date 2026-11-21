"""Lecture 03: the task factory, the task classes and the enumerations."""
import sys
import threading
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon import Status, Workflow
from dagon.stager.base import DataMover, StagerMover
from dagon.task import DagonTask, Task, TaskType, tasks_types
from common.course import check

for kind in TaskType:
    module, name = tasks_types[kind]
    print("%-10s -> %s.%s" % (kind.value, module, name))

batch = DagonTask(TaskType.BATCH, "a", "true")
slurm = DagonTask(TaskType.SLURM, "b", "true", partition="debug")
print("DagonTask(BATCH) builds", type(batch).__name__)
print("DagonTask(SLURM) builds", type(slurm).__name__)
print("every task is a Task and a thread:",
      isinstance(slurm, Task) and isinstance(slurm, threading.Thread))
print("a new task is", batch.status.name)
print("statuses:", " ".join(s.name for s in Status))
print("data movers:", " ".join(m.name for m in DataMover))
print("stager modes:", " ".join(m.name for m in StagerMover))
print("reference schema:", Workflow.SCHEMA)
check(len(TaskType) == 16, "DAGonStar registers 16 task types")
