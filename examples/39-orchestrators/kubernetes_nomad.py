"""Lecture 39: a pod on Kubernetes and a job on Nomad, both APIs mocked."""
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check

with mock.patch("dagon.kubernetes_task.config.load_kube_config"), \
        mock.patch("dagon.kubernetes_task.client.CoreV1Api") as api_class:
    api = api_class.return_value
    pod = DagonTask(TaskType.KUBERNETES, "postprocess", "python plot.py",
                    image="python:3.12-slim", namespace="meteo", remove=True)
    pod.workflow = mock.Mock()
    running = mock.Mock()
    running.status.phase, running.status.pod_ip = "Running", "10.0.0.5"
    api.read_namespaced_pod.return_value = running
    with redirect_stdout(io.StringIO()):        # the backend reports progress
        pod.create_pod()
        ip = pod.info["ip"]
        pod.remove_pod()
    call = api.create_namespaced_pod.call_args
    namespace = call.kwargs.get("namespace", call.args[0] if call.args else None)
print("kubernetes:", type(pod).__name__, "| namespace:", namespace,
      "| ip:", ip, "| deleted:", api.delete_namespaced_pod.called)


class Reply:
    def __init__(self, payload=None, text=""):
        self.payload, self.text, self.status_code = payload, text, 200

    def json(self):
        return self.payload

    def raise_for_status(self):
        return None


job = DagonTask(TaskType.NOMAD, "edge_forecast", "python forecast.py",
                image="python:3.12-slim", nomad_address="http://nomad.invalid:4646",
                cpu=500, memory=1024, datacenter="campania-edge")
job.workflow = mock.Mock()
allocations = [{"ID": "alloc-1", "TaskStates": {"dagon-task": {
    "State": "dead", "Events": [{"Type": "Terminated", "ExitCode": 0}]}}}]
with mock.patch("dagon.nomad_task.requests.post", return_value=Reply({"EvalID": "e1"})) as post, \
        mock.patch("dagon.nomad_task.requests.get", side_effect=[
            Reply({"Status": "running"}), Reply({"Status": "dead"}), Reply(allocations),
            Reply(text="forecast done\n")]), \
        mock.patch("dagon.nomad_task.requests.delete", return_value=Reply()) as delete, \
        mock.patch("dagon.nomad_task.time.sleep"):
    job._submit_job()
    spec = post.call_args.kwargs["json"]["Job"]
    result = job._wait_for_completion(timeout=30)
    logs = job._get_logs()
    job._cleanup_job()
resources = spec["TaskGroups"][0]["Tasks"][0]["Resources"]
print("nomad:", type(job).__name__, "| datacenters:", spec["Datacenters"],
      "| resources:", {k: resources[k] for k in ("CPU", "MemoryMB")})
print("exit:", result["code"], "| logs:", logs.strip(), "| purged:", delete.called)
check(namespace == "meteo" and result["code"] == 0, "both lifecycles complete")
