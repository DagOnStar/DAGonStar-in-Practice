"""Lecture 27: an LLM task turns workflow data into a prompt and saves the reply."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, load, scratch, workflow
from common.services import ChatService, serve

os.environ["COURSE_LLM_KEY"] = "example-key-not-a-secret"   # localhost only

with serve(ChatService) as url, scratch("27") as base:
    wf = workflow("LLM27", base, extra={"llm.course": {
        "endpoint": url, "api_key_env": "COURSE_LLM_KEY", "model": "course-chat"}})
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    summarise = DagonTask(
        TaskType.LLM, "summarise",
        {"messages": [
            {"role": "system", "content": "You are a careful meteorologist."},
            {"role": "user", "content": "Summarise {region}.\n{table}"}]},
        provider="course",
        params={"region": "the Gulf of Naples"},
        input_files={"table": "workflow:///fetch/outputs/observations.csv"},
        output_file="outputs/summary.json")
    wf.add_task(summarise)
    wf.run()

    reply = load(summarise, "outputs/summary.json")
    print("type:", type(summarise).__name__, "| after:", [t.name for t in summarise.prevs])
    print("model:", reply["model"], "| usage:", reply["usage"])
    print("answer:", reply["choices"][0]["message"]["content"])
    check("12 records" in reply["choices"][0]["message"]["content"],
          "the staged CSV reached the prompt")
