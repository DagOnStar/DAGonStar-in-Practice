"""Lecture 37: a Docker task wraps the command in a container; the client is
mocked, so no daemon is needed (set DAGON_LIVE_DOCKER=1 to also run one)."""
import os
import sys
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.docker_task import DockerRemoteTask, DockerTask
from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, scratch, text, workflow

with mock.patch("dagon.docker_task.docker.from_env") as from_env:
    task = DagonTask(TaskType.DOCKER, "regrid", "python regrid.py",
                     image="python:3.12-slim", working_dir="/work dir", remove=True)
    print("type:", type(task).__name__, "| client created:", from_env.called)
    task.container = mock.Mock(id="c0ffee")
    wrapped = task.include_command("python regrid.py")
    print("wrapped:", wrapped.splitlines()[0][:72])
    check("docker exec -t c0ffee" in wrapped and "'/work dir'" in wrapped, "exec")

with mock.patch("dagon.docker_task.docker.DockerClient") as client, \
        mock.patch("dagon.remote.SSHManager") as ssh:
    remote = DockerRemoteTask("regrid_hpc", "python regrid.py",
                              image="python:3.12-slim", ip="192.0.2.10",
                              ssh_username="student", keypath="/tmp/key",
                              working_dir="/home/student/work", ssh_port=2200, pull=False)
print("remote endpoint:", client.call_args.kwargs["base_url"], "| pull:", remote.pull)
check(client.call_args.kwargs["base_url"] == "ssh://student@192.0.2.10:2200", "ssh")

if os.environ.get("DAGON_LIVE_DOCKER") == "1":
    with scratch("37") as base:
        wf = workflow("Docker37", base)
        wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
        count = DagonTask(TaskType.DOCKER, "count", "wc -l workflow:///fetch/"
                          "outputs/observations.csv > n.txt", image="busybox:1.36")
        wf.add_task(count)
        wf.run()
        print("live container:", count.status.name, text(count, "n.txt").split()[0])
else:
    print("live run skipped (set DAGON_LIVE_DOCKER=1 with a running daemon)")
