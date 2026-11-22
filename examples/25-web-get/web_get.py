"""Lecture 25: a web task performs one declarative HTTP request."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, load, scratch, workflow
from common.services import StationService, serve

with serve(StationService) as url, scratch("25") as base:
    wf = workflow("Web25", base)
    latest = DagonTask(TaskType.WEB, "latest_CAP", {
        "method": "GET",
        "url": url + "/stations/CAP/latest",
        "query": {"units": "nautical"},
        "headers": {"Accept": "application/json"},
        "timeout": 10,
        "expected_status": [200],
        "outputs": {"body": "latest.json", "headers": "headers.json",
                    "metadata": "request.json"}})
    alert = DagonTask(TaskType.BATCH, "alert",
                      "grep -q '\"wind\": 13' workflow:///latest_CAP/outputs/"
                      "latest.json && echo 'gale warning' > alert.txt")
    wf.add_task(latest)
    wf.add_task(alert)
    wf.run()

    body = load(latest, "outputs/latest.json")
    meta = load(latest, ".dagon/web_result.json")
    print("type:", type(latest).__name__, "| alert after:", [t.name for t in alert.prevs])
    print("body:", body)
    print("status:", meta["status_code"], "| type:", meta["content_type"],
          "| sha256:", meta["sha256"][:12])
    print("alert:", Path(alert.working_dir, "alert.txt").read_text().strip())
    check(body["wind"] == 13.61 and body["units"] == "nautical", "7 m/s in knots")
