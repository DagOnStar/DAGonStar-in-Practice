"""Lecture 38: Apptainer image preparation and execution, subprocess mocked."""
import io
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.apptainer_task import ApptainerTask
from dagon.task import DagonTask, TaskType
from common.course import check, scratch

with scratch("38") as base:
    task = DagonTask(TaskType.APPTAINER, "roms", "python run_roms.py",
                     image="docker://python:3.12-slim", tmp_dir=str(base))
    print("type:", type(task).__name__, isinstance(task, ApptainerTask))
    task.workflow = mock.Mock()
    task.work_dir = str(base)
    done = mock.Mock(stdout="ok", stderr="", returncode=0)
    quiet = redirect_stdout(io.StringIO())     # the backend reports progress
    with quiet, mock.patch("dagon.apptainer_task.subprocess.run", return_value=done) as run:
        task._prepare_sif_image()
        build = list(run.call_args[0][0])
        task.overlay_file = os.path.join(str(base), "overlay.img")
        task.staging_dir = os.path.join(str(base), "staging")
        task.bind_paths = []
        task.exec_in_container("python run_roms.py")
        execute = list(run.call_args[0][0])
    print("build:", " ".join(w for w in build if not w.startswith(str(base))))
    print("exec flags:", [w for w in execute if w.startswith("--")])
    print("image file:", Path(task.sif_file).suffix)
    with redirect_stdout(io.StringIO()), \
            mock.patch("dagon.apptainer_task.subprocess.run") as run, \
            mock.patch("dagon.apptainer_task.os.path.exists", return_value=True):
        task.image = os.path.join(str(base), "roms.sif")
        task._prepare_sif_image()
    print("prebuilt SIF rebuilt:", run.called)
    check("build" in build and "exec" in execute and not run.called, "commands")
