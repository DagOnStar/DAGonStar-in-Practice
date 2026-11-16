"""Shared fixture of the agentic examples: a temporary dagon.ini with agent
profiles that use DAGonStar's deterministic "mock" adapter.

Nothing here contacts a model endpoint or needs a key.  The observation table
has a duplicated record (id 2), which the quality-control agent must remove.
"""
import json
from pathlib import Path

from dagon import Workflow
from dagon.config import read_config
from dagon.task import DagonTask, TaskType

OBSERVATIONS = {"observations": [
    {"id": 1, "station": "NAP", "temperature_c": 14.0},
    {"id": 2, "station": "CAP", "temperature_c": 16.0},
    {"id": 2, "station": "CAP", "temperature_c": 16.0},
    {"id": 3, "station": "ISC", "temperature_c": 15.0},
    {"id": 4, "station": "ISC", "temperature_c": 15.5},
]}
SOURCE = "workflow:///prepare/outputs/observations.json"

DAGON_INI = """[batch]
scratch_dir_base = {scratch}
run_base =
remove_dir = False

[dagon_service]
use = False

[ftp_pub]
ip = localhost

[agent_provider.fixture]
implementation = mock

[agent_provider.adversarial]
implementation = mock
scenario = undeclared_tool

[agent.quality-local]
provider = fixture
strategy = bounded_iterative
tools = inspect_records, repair_records
guardrails = preserve_record_ids
max_steps = 8
max_tool_calls = 8
timeout_seconds = 60
max_tokens = 4096
max_tool_output_bytes = 65536
max_trace_bytes = 262144

[agent.quality-adversarial]
provider = adversarial
tools = inspect_records
max_steps = 4
timeout_seconds = 30
"""


def write_ini(scratch):
    path = Path(scratch, "dagon.ini")
    path.write_text(DAGON_INI.format(scratch=Path(scratch).as_posix()), encoding="utf-8")
    return path


def workflow(name, scratch, **options):
    """A Workflow whose configuration, with its agent profiles, is read from dagon.ini."""
    return Workflow(name, config=read_config(str(write_ini(scratch))), **options)


def producer(data=None):
    text = json.dumps(OBSERVATIONS if data is None else data).replace("'", "'\\''")
    return DagonTask(TaskType.BATCH, "prepare",
                     "mkdir -p outputs; printf '%s' '" + text + "' > outputs/observations.json")


def quality_control(name="quality_control", **overrides):
    """The agentic task of the course: deduplicate the table, keep every id."""
    options = dict(
        agent="quality-local",
        specification={"schema_version": 1,
                       "objective": "Produce a complete, validated observation table",
                       "context": "Gulf of Naples stations, 2 Nov 2026",
                       "output_schema": {"type": "object", "required": ["observations"]}},
        inputs={"source": SOURCE},
        requirements=[{"id": "completeness", "description": "All four records are present",
                       "evaluator": "record_coverage", "expected": {"count": 4},
                       "weight": 1.0, "mandatory": True, "minimum_score": 1.0}],
        evaluation={"aggregation": "weighted_mean", "threshold": 1.0},
        outputs={"result": "outputs/result.json", "evaluation": "outputs/evaluation.json"},
    )
    options.update(overrides)
    return DagonTask(TaskType.AGENTIC, name=name, **options)
