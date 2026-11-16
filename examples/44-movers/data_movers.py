"""Lecture 44: which data mover the stager chooses, and the commands it
generates (remote tasks and Globus are mocked)."""
import sys
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.remote import RemoteTask
from dagon.stager.base import DataMover, Stager, StagerMover
from common.course import check, config

cfg = config("/scratch", extra={"globus": {"clientid": "course-client",
                                           "intermediate_endpoint": "ep-relay"}})


def task(ip, endpoint=None, remote=False):
    item = mock.Mock(spec=RemoteTask) if remote else mock.Mock()
    item.get_info.return_value = {"ip": ip, "SCP": "active", "FTP": "none",
                                  "GRIDFTP": "active" if endpoint else "none"}
    item.get_scratch_dir.return_value = item.working_dir = "/scratch/" + ip
    item.get_endpoint.return_value = endpoint
    item.get_user.return_value = "student"
    item.get_ip.return_value = ip
    return item


for mover in (DataMover.COPY, DataMover.LINK):
    script = Stager(mover, StagerMover.NORMAL, cfg).stage_in(
        task("10.0.0.1"), task("10.0.0.1"), "/scratch/dst", "outputs/obs.csv")
    verb = "cp -r" if "cp -r" in script else "ln -sf" if "ln -sf" in script else "?"
    print("same host, %-4s -> %s" % (mover.name, verb))

stager = Stager(DataMover.COPY, StagerMover.NORMAL, cfg)
script = stager.stage_in(task("10.0.0.2"), task("10.0.0.1", remote=True),
                         "/scratch/dst", "outputs/obs.csv")
print("different hosts     ->", stager.last_data_mover.name,
      "| uses", "student@10.0.0.1" if "student@10.0.0.1" in script else "?")

with mock.patch("dagon.communication.data_transfer.GlobusManager") as globus:
    stager.stage_in(task("10.0.0.2", endpoint="ep-hpc"), task("10.0.0.1", endpoint="ep-lab"),
                    "/scratch/dst", "outputs/obs.csv")
print("Globus endpoints    ->", stager.last_data_mover.name,
      "| manager:", globus.call_args.args)

strict = stager.generate_command("/scratch/src dir/*", "/scratch/dst",
                                 'cp -r "$file" "$dst"', StagerMover.NORMAL.value, strict=True)
print("strict loop records failures:", "dagon_stage_status=1" in strict)
print("modes:", {m.name: m.value for m in StagerMover})
check(stager.last_data_mover is DataMover.GRIDFTP, "Globus selected")
