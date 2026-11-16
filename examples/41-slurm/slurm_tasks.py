"""Lecture 41: Slurm submissions: the generated sbatch command and two jobs
run through a local stand-in for sbatch (no cluster needed)."""
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.batch import Slurm
from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, scratch, station_mean, text, workflow
from common.mock_scheduler import mock_sbatch, read_log

logging.disable(logging.CRITICAL)    # one job fails on purpose

command = Slurm("wrf; touch pwned", "echo ok", partition="debug queue", ntasks=4,
                memory=2048, time="01:00:00", nodes=1,
                working_dir="/scratch/work dir").generate_command("launcher.sh")
print("sbatch:", command.replace(" -W ", "\n       -W "))
check("'wrf; touch pwned'" in command and "--ntasks=4" in command, "quoted")

with scratch("41") as base:
    log = str(base / "sbatch.jsonl")
    wf = workflow("Slurm41", base)
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    model = DagonTask(TaskType.SLURM, "mean_NAP", station_mean(
        "NAP", "workflow:///fetch/outputs/observations.csv", "outputs/mean.txt"),
        partition="compute", ntasks=2, time="00:05:00")
    broken = DagonTask(TaskType.SLURM, "broken", "sh -c 'exit 3'")
    wf.add_task(model)
    wf.add_task(broken)
    with mock_sbatch(log):
        wf.run()
    print("jobs submitted:", sorted(r["job_name"] for r in read_log(log)))
    print("mean_NAP:", model.status.name, text(model, "outputs/mean.txt").strip())
    print("broken:", broken.status.name)
    check(model.status.name == "FINISHED" and broken.status.name == "FAILED", "outcomes")
