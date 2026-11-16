"""Lecture 33: the agentic contract, its dagon.ini profile, and the
configurations rejected before anything runs."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.agentic import AgenticConfigurationError, AgenticValidationError
from common.agentic import producer, quality_control, workflow
from common.course import check, load, scratch

with scratch("33") as base:
    wf = workflow("Agentic33", base)
    wf.add_task(producer())
    agent = quality_control(tools=[])       # no tools, although the profile has two
    wf.add_task(agent)
    profile = agent.resolve_profile()
    print("profile:", profile.name, "| tools:", profile.tools)
    wf.run()

    report = load(agent, "outputs/evaluation.json")
    print("accepted:", report["accepted"])
    print("fit per attempt:", [a["result_fit"] for a in report["attempts"]])
    print("tool calls:", report["usage"]["tool_calls"],
          "| determinism:", report["execution"]["determinism"])
    print("records kept:", len(load(agent, "outputs/result.json")["observations"]))

    rejected = {}
    for label, options in (("missing_profile", {"agent": "missing"}),
                           ("budget_above_profile", {"budgets": {"max_steps": 99}}),
                           ("unknown_tool", {"tools": ["shell"]}),
                           ("no_requirements", {"requirements": []})):
        try:
            task = quality_control(name=label, **options)
            wf.add_task(task)
            task.resolve_profile()
        except (AgenticConfigurationError, AgenticValidationError) as error:
            rejected[label] = error.code
    print("rejected before execution:", rejected)
    check(report["accepted"] and len(rejected) == 4, "accepted; four refusals")
