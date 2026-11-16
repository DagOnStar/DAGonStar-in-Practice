"""Lecture 40: remote tasks over SSH and cloud tasks, with no network."""
import builtins
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.batch import Batch, RemoteBatch
from dagon.remote import CloudTask, RemoteTask
from dagon.task import DagonTask, TaskType
from common.course import check

with mock.patch("dagon.remote.SSHManager") as manager:
    default = Batch("collect", "hostname", ip="192.0.2.10",
                    ssh_username="student", keypath="/tmp/key")
    custom = RemoteTask("collect2", "hostname", ip="192.0.2.10",
                        ssh_username="student", keypath="/tmp/key", ssh_port=2200)
    anonymous = RemoteTask("collect3", "hostname", ip="192.0.2.10", keypath="/tmp/key")
print("Batch(..., ip=...) builds", type(default).__name__,
      "| ports:", default.ssh_port, custom.ssh_port)
print("connections opened:", manager.call_count,
      "| without a username:", anonymous.ssh_connection)

sent = []
custom.workflow = SimpleNamespace(logger=SimpleNamespace(error=lambda *a: None))
custom.ssh_connection = SimpleNamespace(
    execute_command=lambda command: sent.append(command) or {"code": 0})
custom.working_dir = "/scratch/run dir; rm -rf ~"   # a hostile path
custom.mkdir_working_dir(custom.working_dir)
print("quoted remote command:", sent[0])
check(isinstance(default, RemoteBatch) and "'" in sent[0], "quoted")

cloud = DagonTask(TaskType.CLOUD, "regional_model", "hostname", provider="dummy",
                  ssh_username="cloud-user", key_options={"key_path": "/tmp/key"},
                  instance_flavour={"image": "image-id", "size": "small"},
                  instance_name="dagon-course", stop_instance=True)
print("cloud task:", type(cloud).__name__, "| node:", cloud.node,
      "| ssh:", cloud.ssh_connection)
cloud.workflow = mock.Mock()
cloud.workflow.name = "Cloud40"
real_import = builtins.__import__


def without_libcloud(name, *args, **kwargs):
    if name == "libcloud" or name.startswith("libcloud."):
        raise ImportError("No module named 'libcloud'", name="libcloud")
    return real_import(name, *args, **kwargs)


saved = sys.modules.pop("dagon.cloud", None)
try:
    with mock.patch("builtins.__import__", side_effect=without_libcloud):
        try:
            cloud.execute()
        except ImportError as error:
            print("without the extra:", error)
finally:
    if saved is not None:
        sys.modules["dagon.cloud"] = saved
check(isinstance(cloud, CloudTask) and cloud.node is None, "nothing provisioned")
