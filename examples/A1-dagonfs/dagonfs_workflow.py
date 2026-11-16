"""Appendix A: a DAGonStar workflow whose scratch lives on a DAGonFS volume.

On a Linux node with MPI, FUSE 3 and a DAGonFS build, set
  DAGONFS_PYTHON=/path/to/DAGonFS/python  DAGONFS=/path/to/build/dagonfs
and the script mounts a client-server volume, runs the workflow on it, copies
the result to persistent storage (stage-out) and unmounts the volume.
Anywhere else it runs the same workflow on a temporary directory, so the
workflow itself is always tested.
"""
import os
import platform
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import STATIONS, check, fetch_observations, scratch, station_mean, text, workflow

if os.environ.get("DAGONFS_PYTHON"):
    sys.path.insert(0, os.environ["DAGONFS_PYTHON"])
try:
    from dagonfs import Volume
except ImportError:
    Volume = None


@contextmanager
def scratch_space(base):
    live = (Volume is not None and platform.system() == "Linux"
            and shutil.which(os.environ.get("DAGONFS", "dagonfs")))
    if live:
        with Volume(base / "dagonfs", model="client-server", ranks=4) as volume:
            yield "DAGonFS client-server, 4 ranks", volume.mountpoint(0)
    else:
        if Volume is not None:
            plan = Volume(base / "dagonfs", model="client-server", ranks=4,
                          executable="dagonfs").command()
            print("would launch:", " ".join(plan).replace(str(base), "<base>"))
        yield "local directory (no DAGonFS on this host)", base / "fallback"


with scratch("A1") as base:
    persistent = base / "results"                       # durable storage
    with scratch_space(base) as (kind, mount):
        mount.mkdir(parents=True, exist_ok=True)
        wf = workflow("DAGonFS_A1", mount)               # scratch_dir_base = mount
        wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
        for s in STATIONS:
            wf.add_task(DagonTask(TaskType.BATCH, "mean_" + s, station_mean(
                s, "workflow:///fetch/outputs/observations.csv", "outputs/mean.txt")))
        parts = " ".join("workflow:///mean_%s/outputs/mean.txt" % s for s in STATIONS)
        report = DagonTask(TaskType.BATCH, "report", "cat %s > report.txt" % parts)
        wf.add_task(report)
        wf.run()
        persistent.mkdir()
        shutil.copy(Path(report.working_dir, "report.txt"), persistent)   # stage-out
        print("scratch:", kind)
        print("task folders on the scratch:", len(list(mount.iterdir())))
    print("kept after the volume is gone:", (persistent / "report.txt").read_text().split())
    check((persistent / "report.txt").read_text() == text(report, "report.txt"), "stage-out")
