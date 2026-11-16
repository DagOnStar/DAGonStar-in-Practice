"""Lecture 35: independent result fit, mandatory gates, publication only
when accepted, and checkpoint identity by content."""
import json
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.agentic.evaluation import aggregate
from dagon.task import DagonTask, TaskType
from common.agentic import OBSERVATIONS, producer, quality_control, workflow
from common.course import check, load, scratch

logging.disable(logging.CRITICAL)   # one run is rejected on purpose

golden = aggregate([
    {"id": "completeness", "status": "pass", "score": 1.0, "weight": 2.0,
     "mandatory": False, "minimum_score": None, "hard": False},
    {"id": "stations", "status": "fail", "score": 0.0, "weight": 1.0,
     "mandatory": True, "minimum_score": 1.0, "hard": False}], threshold=0.6)
print("F = %.4f | accepted: %s | gate failures: %s"
      % (golden["result_fit"], golden["accepted"], golden["mandatory_failures"]))

with scratch("35") as base:
    wf = workflow("Gate35", base)
    wf.add_task(producer())
    agent = quality_control(tools=[], budgets={"max_attempts": 2}, requirements=[
        {"id": "completeness", "evaluator": "record_coverage",
         "expected": {"count": 4}, "weight": 2.0},
        {"id": "stations", "evaluator": "exact_match", "expected": 5,
         "weight": 1.0, "mandatory": True, "options": {"path": "station_count"}}],
        evaluation={"threshold": 0.6})
    publish = DagonTask(TaskType.BATCH, "publish",
                        "cp workflow:///quality_control/outputs/result.json table.json")
    wf.add_task(agent)
    wf.add_task(publish)
    wf.run()
    print("gated run:", agent.status.name, "| publish ran:", publish.working_dir is not None,
          "| result exists:", Path(agent.working_dir, "outputs/result.json").exists())

with scratch("35") as base:
    checkpoint = str(base / "checkpoint.json")

    def run(threshold=1.0):
        wf = workflow("Resume35", base, checkpoint_file=checkpoint)
        wf.add_task(producer())
        task = quality_control(evaluation={"threshold": threshold})
        wf.add_task(task)
        wf.run(checkpoint)
        return task

    first = run()
    print("reused, same contract:", run().fair_checkpoint_reused)
    print("reused, new threshold:", run(threshold=0.95).fair_checkpoint_reused)
    table = Path(first.prevs[0].working_dir, "outputs", "observations.json")
    table.write_text(json.dumps({"observations": OBSERVATIONS["observations"][:2]
                                 + OBSERVATIONS["observations"][3:]}))
    print("reused, new input content:", run(threshold=0.95).fair_checkpoint_reused)
check(abs(golden["result_fit"] - 2 / 3) < 1e-12 and not golden["accepted"], "golden")
