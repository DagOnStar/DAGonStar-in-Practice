"""Lecture 34: declared tools, guardrails checked outside the agent, and an
undeclared action blocked before it has any effect."""
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon import Status
from dagon.agentic.guardrails import check_action
from dagon.agentic.registry import default_registry
from common.agentic import producer, quality_control, workflow
from common.course import check, load, scratch

logging.disable(logging.CRITICAL)   # one run is rejected on purpose

registry = default_registry()
allowed = ["inspect_records"]
verdicts = {}
for label, tool, arguments in (
        ("declared", "inspect_records", {"input": "source"}),
        ("undeclared", "repair_records", {"input": "source"}),
        ("escape", "inspect_records", {"input": "../../etc/passwd"}),
        ("uri", "inspect_records", {"input": "workflow:///other/secret.json"})):
    violation = check_action(tool, arguments, allowed, registry)
    verdicts[label] = violation.code if violation else "allowed"
print("action checks:", verdicts)

with scratch("34") as base:
    wf = workflow("Guarded34", base)
    wf.add_task(producer())
    agent = quality_control()
    wf.add_task(agent)
    wf.run()
    trace = load(agent, "outputs/trace.json")
    tools = [e.get("tool") for e in trace["entries"] if e["event"] == "tool"]
    print("tools used:", tools, "| accepted:", load(agent, "outputs/evaluation.json")["accepted"])

with scratch("34") as base:
    wf = workflow("Blocked34", base)
    wf.add_task(producer())
    rogue = quality_control(agent="quality-adversarial")
    wf.add_task(rogue)
    wf.run()
    report = load(rogue, "outputs/evaluation.json")
    print("adversarial:", rogue.status.name, "|", report["termination_reason"],
          "| tool calls:", report["usage"]["tool_calls"])
    published = Path(rogue.working_dir, "outputs/result.json").exists()
    print("result published:", published)
    check(rogue.status is Status.FAILED and not published, "blocked, nothing published")
