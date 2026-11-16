"""Lecture 36: one graph across the continuum: an IoT observation at the
edge, a native normalisation, an agentic quality check, a FaaS archive."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon import Status
from dagon.task import DagonTask, TaskType
from common.agentic import quality_control, workflow
from common.course import check, load, scratch

EVENTS = [{"sequence": n, "id": n, "station": s, "temperature_c": t}
          for n, s, t in ((1, "NAP", 14.0), (2, "CAP", 16.0),
                          (3, "ISC", 15.0), (4, "ISC", 15.5))]

with scratch("36") as base:
    wf = workflow("Continuum36", base)
    edge = DagonTask(TaskType.IOT, "edge", operation="observe", provider="mock",
                     target={"device_id": "gateway-pozzuoli"}, resource="temperature",
                     request={"events": EVENTS},
                     completion={"mode": "sample_count", "count": 4, "timeout_seconds": 10},
                     outputs={"observations": "outputs/observations.json"})
    normalise = DagonTask(TaskType.NATIVE, "normalise",
                          "common.weather:events_to_observations",
                          inputs={"input_file": "workflow:///edge/outputs/observations.json"},
                          outputs={"output_file": "observations.json"})
    qc = quality_control("qc", tools=[],
                         inputs={"source": "workflow:///normalise/outputs/observations.json"})
    archive = DagonTask(TaskType.FAAS, "archive", provider="mock", function="archive",
                        inputs={"table": {"document": "workflow:///qc/outputs/result.json"}},
                        outputs={"receipt": "receipt.json"},
                        provider_options={"mock": {"response": {
                            "status": "succeeded", "outputs": {"receipt": {"stored": True}}}}})
    for task in (edge, normalise, qc, archive):
        wf.add_task(task)
    wf.run()

    print("graph:", " -> ".join("%s(%s)" % (t.name, type(t).__name__) for t in wf.tasks))
    print("states:", {t.name: t.status.name for t in wf.tasks})
    print("QC accepted:", load(qc, "outputs/evaluation.json")["accepted"],
          "| records:", len(load(qc, "outputs/result.json")["observations"]))
    print("receipt:", load(archive, "outputs/receipt.json"))
    check(all(t.status is Status.FINISHED for t in wf.tasks), "every step finished")
