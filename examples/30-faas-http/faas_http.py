"""Lecture 30: the same FaaS contract against an HTTP function, and an
unknown provider rejected before anything runs."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.faas_providers import get_provider
from dagon.task import DagonTask, TaskType
from common.course import check, load, scratch, workflow
from common.services import FunctionService, serve

SDKS = ("boto3", "azure", "google")

with serve(FunctionService) as url, scratch("30") as base:
    wf = workflow("FaaS30", base)
    average = DagonTask(
        TaskType.FAAS, "average", provider="http", function="mean-of-values",
        inputs={"values": [15.5, 16.75, 15.75]},
        outputs={"result": "mean.json"},
        timeout=10,
        provider_options={"http": {"endpoint": url + "/invoke"}})
    wf.add_task(average)
    wf.run()

    print("status:", average.status.name, "| result:", load(average, "outputs/mean.json"))
    meta = load(average, ".dagon/faas_provider_metadata.json")
    print("provider metadata keys:", sorted(meta))
    print("HTTP calls served:", FunctionService.calls)
    check(load(average, "outputs/mean.json") == {"mean": 16.0, "n": 3}, "mean")

try:
    get_provider("lambda-typo")
except ValueError as error:
    print("rejected:", error)
print("cloud SDKs imported:", [m for m in SDKS if m in sys.modules] or "none")
check(not any(m in sys.modules for m in SDKS), "optional SDKs load lazily")
