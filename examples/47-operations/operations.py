"""Lecture 47: operating DAGonStar: service registration (mocked), JSON round
trips, the runner environment, platform helpers and the packaged runner."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon import Workflow
from dagon.platform_support import bash_executable, shell_path
from dagon.runtime_env import PACKAGE_ROOT, runner_environment
from dagon.task import DagonTask, TaskType
from common.course import check, config, fetch_observations, scratch


class Created:
    status_code, reason = 201, "Created"

    def json(self):
        return {"id": 7}


with scratch("47") as base:
    service = config(base, {"dagon_service": {"use": "True",
                                              "route": "http://dagon-service.invalid"}})
    with mock.patch("dagon.api.requests.head") as head, \
            mock.patch("dagon.api.requests.post", return_value=Created()) as post:
        registered = Workflow("Ops47", config=service)
        registered.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    print("service checked at:", head.call_args.args[0])
    print("workflow id:", registered.workflow_id, "| calls:",
          [c.args[0].rsplit("/", 2)[-2:] for c in post.call_args_list])

    offline = Workflow("Ops47Offline", config=config(base))
    fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations())
    report = DagonTask(TaskType.BATCH, "report", "true")
    offline.add_task(fetch)
    offline.add_task(report)
    report.add_dependency_to(fetch)
    copy = Workflow("placeholder", config=config(base),
                    jsonload=json.loads(json.dumps(offline.as_json())))
    copy.make_dependencies()
    print("JSON round trip keeps the explicit edge:", [t.name for t in copy.tasks[1].prevs])

env = runner_environment({"COURSE": "47"}, base={"PYTHONPATH": "/site/first"})
print("runner PYTHONPATH keeps user entries first:",
      env["PYTHONPATH"].split(os.pathsep)[0] == "/site/first",
      "| package root appended:", env["PYTHONPATH"].split(os.pathsep)[-1] == PACKAGE_ROOT)
print("bash:", bash_executable(), "| shell_path is a str:", isinstance(shell_path("."), str))
runner = shutil.which("dagon-agent-runner")
if runner:
    done = subprocess.run([runner, "--help"], capture_output=True, text=True, timeout=60)
    print("dagon-agent-runner --help:", "ok" if done.returncode == 0 else done.returncode)
else:
    print("dagon-agent-runner not on PATH (python -m pip install dagonstar)")
check(registered.workflow_id == 7, "registered through the mocked service")
