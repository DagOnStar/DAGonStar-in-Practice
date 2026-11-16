"""Lecture 29: a FaaS task invokes an already-deployed function (mock provider)."""
import sys
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.faas_providers import get_provider
from dagon.task import DagonTask, TaskType
from common.course import check, load, scratch, workflow

with scratch("29") as base:
    wf = workflow("FaaS29", base)
    prepare = DagonTask(TaskType.BATCH, "prepare",
                        "mkdir -p outputs && echo '{\"station\": \"NAP\"}' "
                        "> outputs/request.json")
    classify = DagonTask(
        TaskType.FAAS, "classify", provider="mock", function="sea-state",
        inputs={"request": {"document": "workflow:///prepare/outputs/request.json"},
                "threshold": 7.0},
        outputs={"result": "sea_state.json"},
        retry={"max_attempts": 3, "backoff": "exponential"},
        provider_options={"mock": {"response": {
            "status": "succeeded", "outputs": {"result": {"beaufort": 4}}}}})
    wf.add_task(prepare)
    wf.add_task(classify)
    wf.run()

    print("type:", type(classify).__name__, "| after:", [t.name for t in classify.prevs])
    print("result:", load(classify, "outputs/sea_state.json"))
    request = load(classify, ".dagon/faas_request.json")
    document = request["data"]["inputs"]["request"]["document"]
    print("the file travels as a descriptor:", sorted(document))
    print("records:", sorted(p.name for p in Path(classify.working_dir, ".dagon").glob("faas_*")))
    with mock.patch("dagon.faas.get_provider", return_value=get_provider("mock")) as factory:
        classify.execute()                     # completed: not invoked again
    print("provider calls on re-execution:", factory.call_count)
    check(factory.call_count == 0, "a completed invocation is never repeated")
