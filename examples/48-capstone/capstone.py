"""Lecture 48 capstone: every registered TaskType in one checkpointed,
FAIR-recorded graph under portable emulation, an accepted agentic step, a
CWL export and a checklist.  No live adapter or network call is made."""
import json
import sys
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon import Status, Workflow
from dagon.config import read_config
from dagon.fair import Agent, FairProfile
from dagon.remote import CloudTask
from dagon.task import DagonTask, TaskType
from common.agentic import OBSERVATIONS, write_ini
from common.course import check, fetch_observations, scratch

REF = "workflow:///fetch/outputs/observations.csv"
TABLE = "workflow:///table/outputs/observations.json"


def forbidden(*_args, **_kwargs):
    raise AssertionError("a live adapter or network call was attempted")


def every_task_type():
    with mock.patch("dagon.docker_task.docker.from_env", return_value=None), \
            mock.patch("dagon.kubernetes_task.config.load_kube_config"), \
            mock.patch("dagon.kubernetes_task.client.CoreV1Api"), \
            mock.patch.object(CloudTask, "connect", return_value=None, create=True):
        return {
            TaskType.CHECKPOINT: DagonTask(TaskType.CHECKPOINT, "checkpoint", REF),
            TaskType.BATCH: DagonTask(TaskType.BATCH, "batch", "wc -l " + REF),
            TaskType.SLURM: DagonTask(TaskType.SLURM, "wrf", "wc -l " + REF, ntasks=64),
            TaskType.CLOUD: DagonTask(TaskType.CLOUD, "cloud", "wc -l " + REF, provider="mock",
                                      ssh_username="user", key_options={"key_path": "/tmp/key"},
                                      instance_id="instance"),
            TaskType.DOCKER: DagonTask(TaskType.DOCKER, "docker", "wc -l " + REF,
                                       image="busybox:1.36", pull=False),
            TaskType.KUBERNETES: DagonTask(TaskType.KUBERNETES, "kubernetes", "wc -l " + REF,
                                           image="busybox:1.36"),
            TaskType.APPTAINER: DagonTask(TaskType.APPTAINER, "roms", "wc -l " + REF,
                                          image="roms.sif"),
            TaskType.NOMAD: DagonTask(TaskType.NOMAD, "nomad", "wc -l " + REF, image="busybox:1.36"),
            TaskType.LLM: DagonTask(TaskType.LLM, "bulletin",
                                    {"messages": [{"role": "user", "content": REF}]},
                                    provider="mock"),
            TaskType.NATIVE: DagonTask(TaskType.NATIVE, "count", "common.weather:count_records",
                                       inputs={"input_file": "workflow:///qc/outputs/result.json"},
                                       outputs={"output_file": "count.json"}),
            TaskType.WEB: DagonTask(TaskType.WEB, "publish", {
                "method": "POST", "url": "http://example.invalid", "json": {"text": REF}}),
            TaskType.FAAS: DagonTask(TaskType.FAAS, "archive", provider="mock", function="echo",
                                     inputs={"document": REF}),
            TaskType.IOT: DagonTask(TaskType.IOT, "buoy", operation="observe", provider="mock",
                                    request={"events": [{"source": REF}]},
                                    completion={"mode": "first_event"},
                                    outputs={"observations": "outputs/observations.json"}),
            TaskType.AGENTIC: DagonTask(TaskType.AGENTIC, "qc", agent="quality-local",
                                        specification={"objective": "Deduplicate the table",
                                                       "output_schema": {"type": "object",
                                                                         "required": ["observations"]}},
                                        inputs={"source": TABLE},
                                        requirements=[{"id": "complete", "evaluator": "record_coverage",
                                                       "expected": {"count": 4}, "mandatory": True}]),
        }


with scratch("48") as base:
    checkpoint, fair_dir = str(base / "checkpoint.json"), str(base / "fair")
    table = json.dumps(OBSERVATIONS)
    with mock.patch("dagon.agentic.providers.OpenAICompatibleAdapter.propose", side_effect=forbidden), \
            mock.patch("urllib.request.urlopen", side_effect=forbidden):
        wf = Workflow("Capstone48", config=read_config(str(write_ini(base))),
                      portable_emulation=True, checkpoint_file=checkpoint)
        wf.enable_fair(FairProfile(title="Gulf of Naples capstone",
                                   description="Every task type under portable emulation.",
                                   creators=[Agent(name="Course participant")],
                                   license="CC-BY-4.0", output_dir=fair_dir))
        wf.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
        wf.add_task(DagonTask(TaskType.BATCH, "table", "mkdir -p outputs; printf '%s' '"
                              + table + "' > outputs/observations.json"))
        tasks = every_task_type()
        check(set(tasks) == set(TaskType), "every registered TaskType is present")
        for task in tasks.values():
            wf.add_task(task)
        wf.run()

    failed = [t.name for t in wf.tasks if t.status is not Status.FINISHED]
    evaluation = json.loads(Path(tasks[TaskType.AGENTIC].working_dir, "outputs",
                                 "evaluation.json").read_text())
    count = json.loads(Path(tasks[TaskType.NATIVE].working_dir, "outputs", "count.json").read_text())
    run = json.loads(Path(fair_dir, "run.json").read_text())
    cwl = base / "capstone.cwl"
    wf.saveAsCWL(str(cwl))
    steps = json.loads(cwl.read_text())["steps"]
    print("tasks:", len(wf.tasks), "| failed:", failed)
    print("agent accepted:", evaluation["accepted"], "| records after QC:", count["count"])
    print("FAIR run covers every task:", set(run["tasks"]) == {t.name for t in wf.tasks})
    print("CWL steps:", len(steps), "| scratch path in CWL:", str(base) in cwl.read_text())
    checklist = {"task types": len(TaskType), "agent accepted": evaluation["accepted"],
                 "checkpoint written": Path(checkpoint).is_file(), "CWL exported": True,
                 "live adapters invoked": 0}
    print(json.dumps(checklist, sort_keys=True))
    check(not failed and count == {"count": 4}, "the capstone graph completed")
