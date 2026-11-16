"""Lecture 28: what an LLM task records, what it never records, and a
provider-free rehearsal with portable emulation."""
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, load, scratch, workflow
from common.services import ChatService, serve

KEY = "example-key-not-a-secret"
os.environ["COURSE_LLM_KEY"] = KEY
PROMPT = {"messages": [{"role": "user", "content": "Flag anomalies in:\n{table}"}],
          "temperature": 0}


def build(base, **options):
    wf = workflow("Audit28", base, extra={"llm.course": {
        "endpoint": options.pop("endpoint", "http://127.0.0.1:9"),
        "api_key_env": "COURSE_LLM_KEY", "model": "course-chat"}}, **options)
    wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    task = DagonTask(TaskType.LLM, "review", PROMPT, provider="course",
                     input_files={"table": "workflow:///fetch/outputs/observations.csv"})
    wf.add_task(task)
    wf.run()
    return wf, task


with serve(ChatService) as url, scratch("28") as base:
    wf, task = build(base, endpoint=url)
    files = sorted(p.relative_to(task.working_dir).as_posix()
                   for p in Path(task.working_dir).rglob("*") if p.is_file()
                   and "ssh_key" not in p.name)
    print("files:", files)
    leaked = any(KEY in p.read_text(errors="ignore")
                 for p in Path(base).rglob("*") if p.is_file())
    print("API key written anywhere in scratch:", leaked)
    print("serialised task:", sorted(wf.as_json()["tasks"]["review"]))
    check(not leaked, "the key stays in the environment")

with scratch("28") as base:
    wf, task = build(base, portable_emulation=True)       # no provider at all
    echoed = json.loads(load(task, "response.json")["choices"][0]["message"]["content"])
    print("portable rehearsal id:", load(task, "response.json")["id"])
    print("rendered prompt starts:", echoed["messages"][0]["content"][:40].replace("\n", " | "))
    check(echoed["temperature"] == 0, "the rendered request is echoed back")
