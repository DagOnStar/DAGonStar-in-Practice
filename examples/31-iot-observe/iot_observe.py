"""Lecture 31: a bounded IoT observation and its checkpoint."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, load, scratch, workflow

READINGS = [{"sequence": n, "value": v, "unit": "Cel"}
            for n, v in enumerate((16.0, 16.5, 17.0, 17.5, 18.0), start=1)]

try:
    DagonTask(TaskType.IOT, "forever", operation="observe", completion={})
except ValueError as error:
    print("unbounded observation rejected:", error)

with scratch("31") as base:
    wf = workflow("IoT31", base)
    buoy = DagonTask(
        TaskType.IOT, "buoy_CAP", operation="observe", provider="mock",
        target={"device_id": "buoy-capri-01"}, resource="sea_temperature",
        request={"events": READINGS},
        completion={"mode": "sample_count", "count": 3, "timeout_seconds": 10},
        outputs={"observations": "outputs/observations.json"})
    mean = DagonTask(TaskType.BATCH, "mean",
                     "python3 -c \"import json,sys; e=json.load(open(sys.argv[1]))"
                     "['events']; print(sum(x['value'] for x in e)/len(e))\" "
                     "workflow:///buoy_CAP/outputs/observations.json > mean.txt")
    wf.add_task(buoy)
    wf.add_task(mean)
    wf.run()

    events = load(buoy, "outputs/observations.json")["events"]
    print("kept sequences:", [e["sequence"] for e in events], "of", len(READINGS))
    print("mean of the sample:", Path(mean.working_dir, "mean.txt").read_text().strip())
    print("provenance:", sorted(load(buoy, ".dagon/iot_provenance.json")))
    print("checkpoint reusable:", buoy.reuse_checkpoint())
    Path(buoy.working_dir, "outputs/observations.json").unlink()
    print("after deleting the output:", buoy.reuse_checkpoint())
    check(len(events) == 3, "the completion bound keeps three samples")
