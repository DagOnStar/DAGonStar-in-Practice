"""Lecture 32: desired-state configuration, actuation, and an uncertain
actuation that is recorded and never replayed."""
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, load, scratch, workflow

logging.disable(logging.CRITICAL)   # the uncertain actuation fails on purpose

with scratch("32") as base:
    wf = workflow("IoT32", base)
    configure = DagonTask(
        TaskType.IOT, "sampling_rate", operation="configure", provider="mock",
        target={"device_id": "buoy-capri-01"},
        request={"sampling_seconds": 60},
        completion={"mode": "acknowledged", "timeout_seconds": 5},
        outputs={"state": "outputs/state.json"})
    siren = DagonTask(
        TaskType.IOT, "storm_siren", operation="actuate", provider="mock",
        target={"device_id": "siren-marina-grande"}, action="sound",
        completion={"mode": "acknowledged", "timeout_seconds": 5},
        delivery={"max_attempts": 1})
    gate = DagonTask(
        TaskType.IOT, "harbour_gate", operation="actuate", provider="mock",
        target={"device_id": "gate-02"}, action="close",
        completion={"mode": "acknowledged", "timeout_seconds": 2},
        delivery={"max_attempts": 1},
        provider_options={"unknown_outcome": True})   # the ack never arrives
    for task in (configure, siren, gate):
        wf.add_task(task)
    wf.run()

    print("configure:", load(configure, "outputs/state.json"))
    for task in (configure, siren, gate):
        record = wf.checkpoints["IoT32." + task.name]
        print("%-13s %-8s certainty=%s" % (task.name, task.status.name,
                                          record.get("outcome_certainty")))
    print("gate reusable from checkpoint:", gate.reuse_checkpoint())
    check(wf.checkpoints["IoT32.harbour_gate"]["outcome_certainty"] == "unknown",
          "an unacknowledged actuation is recorded as unknown")
