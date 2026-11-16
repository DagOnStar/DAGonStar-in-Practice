"""Lecture 42: BeeOND job-local storage: validated configuration, the sbatch
fragment, and task and workflow volumes under portable emulation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.batch import Slurm
from dagon.beeond import BeeONDConfig
from dagon.task import DagonTask, TaskType
from common.course import check, scratch, text, workflow

defaults = BeeONDConfig()
print("defaults: scope=%s persist=%s comment=%s"
      % (defaults.scope, defaults.persist, defaults.comment))
rejected = []
for options in ({"scope": "cluster"}, {"mount_template": "/mnt/$(id)"}, {"volume": "a b"}):
    try:
        BeeONDConfig(**options)
    except ValueError:
        rejected.append(next(iter(options)))
print("rejected options:", rejected)

command = Slurm("wrf", "run", comment="beeond-fs", nodes=2, nodelist="wn[01-02]",
                beeond="task", working_dir="/scratch/w").generate_command("launcher.sh")
print("comment flags:", command.count("--comment=beeond-fs"), "| nodes:", "--nodes=2" in command)

with scratch("42") as base:
    wf = workflow("BeeOND42", base, portable_emulation=True)
    wf.create_beeond_volume("forcing", time="00:10:00")
    write = DagonTask(TaskType.SLURM, "wrf", 'echo "wrfout d01" > "$DAGON_BEEOND/wrfout.txt"',
                      beeond="task")
    read = DagonTask(TaskType.BATCH, "archive", "cp workflow:///wrf/beeond/wrfout.txt kept.txt")
    stage = DagonTask(TaskType.SLURM, "stage", 'echo "boundary" > "$DAGON_BEEOND/bc.txt"',
                      beeond="workflow:forcing")
    use = DagonTask(TaskType.SLURM, "roms", 'cat "$DAGON_BEEOND/bc.txt" > used.txt',
                    beeond="workflow:forcing")
    for task in (write, read, stage, use):
        wf.add_task(task)
    wf.make_dependencies()
    use.add_dependency_to(stage)          # shared volume: order by hand
    wf.run()
    print("task volume persisted:", text(read, "kept.txt").strip())
    print("workflow volume shared:", text(use, "used.txt").strip())
    check(text(use, "used.txt").strip() == "boundary", "shared volume")
