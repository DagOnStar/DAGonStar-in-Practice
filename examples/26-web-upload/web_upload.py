"""Lecture 26: upload a workflow artifact, authenticate from the environment,
and fail on an unexpected status."""
import logging
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, load, scratch, workflow
from common.services import COURSE_TOKEN, StationService, serve

logging.disable(logging.CRITICAL)        # the "busy" request fails on purpose
os.environ["STATION_TOKEN"] = COURSE_TOKEN   # in real life: set by the job

with serve(StationService) as url, scratch("26") as base:
    wf = workflow("Upload26", base)
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    upload = DagonTask(TaskType.WEB, "upload", {
        "method": "POST", "url": url + "/uploads",
        "multipart": {
            "dataset": {"file": "workflow:///fetch/outputs/observations.csv",
                        "content_type": "text/csv"},
            "description": {"value": "Gulf of Naples, 2 Nov 2026"}},
        "expected_status": 201,
        "outputs": {"body": "receipt.json"}})
    private = DagonTask(TaskType.WEB, "private", {
        "url": url + "/private",
        "auth": {"type": "bearer", "token_env": "STATION_TOKEN"},
        "outputs": {"body": "access.json"}})
    busy = DagonTask(TaskType.WEB, "busy", {
        "url": url + "/busy", "retries": 2, "retry_backoff": 0.01,
        "outputs": {"body": "busy.json"}})
    for task in (upload, private, busy):
        wf.add_task(task)
    wf.run()

    print("upload:", upload.status.name, load(upload, "outputs/receipt.json"))
    print("private:", private.status.name, load(private, "outputs/access.json"))
    print("auth recorded as:", load(private, ".dagon/web_result.json")["auth"])
    request = Path(private.working_dir, ".dagon", "web_request.json").read_text()
    print("token in the request record:", COURSE_TOKEN in request)
    print("busy:", busy.status.name, "after",
          sum(1 for c in StationService.calls if c[1] == "/busy"), "attempts")
    check(busy.status.name == "FAILED", "503 is not an accepted status")
