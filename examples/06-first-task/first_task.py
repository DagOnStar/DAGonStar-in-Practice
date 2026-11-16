"""Lecture 06: one local batch task, its status and its working directory."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, scratch, text, where, workflow

with scratch("06") as base:
    wf = workflow("FirstTask06", base)
    hello = DagonTask(TaskType.BATCH, "hello",
                      "mkdir -p outputs && echo 'Ciao from the Gulf' "
                      "> outputs/greeting.txt")
    print("before run:", hello.status.name, "| working dir:", hello.working_dir)
    wf.add_task(hello)
    wf.run()

    folder = Path(hello.working_dir)
    print("after run:", hello.status.name)
    print("directory: <timestamp>-" + where(hello))
    print("timestamp digits:", len(folder.name.split("-")[0]))
    print("greeting:", text(hello, "outputs/greeting.txt").strip())
    check(hello.status.name == "FINISHED", "the task finished")
    check(folder.parent == base, "the task runs inside the scratch base")
