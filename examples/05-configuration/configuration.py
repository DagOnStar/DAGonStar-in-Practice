"""Lecture 05: the same configuration as a dagon.ini file and as a dictionary."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon import Workflow
from dagon.config import read_config
from dagon.task import DagonTask, TaskType
from common.course import check, config, scratch

HERE = Path(__file__).resolve().parent

with scratch("05") as base:
    ini = (HERE / "dagon.ini").read_text()
    ini = ini.replace("scratch_dir_base = /tmp/",
                      "scratch_dir_base = %s" % base.as_posix())
    (base / "dagon.ini").write_text(ini)

    from_file = Workflow("FromFile05", config_file=str(base / "dagon.ini"))
    sections = read_config(str(base / "dagon.ini"))
    print("sections:", ", ".join(s for s in sections if not s.startswith(
        ("logger", "handler", "formatter"))))
    print("batch:", dict(sections["batch"], scratch_dir_base="<scratch>"))

    from_dict = Workflow("FromDict05", config=config(base))
    for wf in (from_file, from_dict):
        wf.add_task(DagonTask(TaskType.BATCH, "probe", "echo ok > ok.txt"))
        wf.run()
        task = wf.tasks[0]
        inside = Path(task.working_dir).parent == base
        print(wf.name, "| remove_dir:", wf.get_remove_dir_op(),
              "| task dir inside scratch:", inside)
        check(inside, "the scratch base decides where tasks run")
