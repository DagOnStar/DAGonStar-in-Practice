"""Lecture 45: FAIR metadata is opt-in, declared, licensed and credential-free."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.fair import AccessPolicy, Agent, Artifact, FairProfile
from dagon.task import DagonTask, TaskType
from common.course import check, fetch_observations, scratch, station_mean, workflow

SECRET = "sk-course-sentinel-0000"     # a fake key that must never be exported

with scratch("45") as base:
    plain = workflow("Plain45", base)
    plain.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
    plain.run()
    print("FAIR folder without enable_fair:", Path(base, ".dagon", "fair").exists())

    wf = workflow("Fair45", base, extra={"llm": {"api_key": SECRET}})
    wf.enable_fair(FairProfile(
        title="Capri mean temperature, 2 Nov 2026",
        description="Station mean computed from the course dataset.",
        creators=[Agent(name="Course participant")], license="CC-BY-4.0",
        keywords=["meteorology", "Gulf of Naples"],
        access_policy=AccessPolicy(metadata="public", data="local")))
    fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations()).declare_outputs(
        Artifact("outputs/observations.csv", name="Observations", media_type="text/csv",
                 license="CC-BY-4.0"))
    mean = DagonTask(TaskType.BATCH, "mean_CAP", station_mean(
        "CAP", "workflow:///fetch/outputs/observations.csv", "outputs/mean.txt"))
    mean.declare_outputs(Artifact("outputs/mean.txt", name="Capri mean",
                                  media_type="text/plain", license="CC-BY-4.0"))
    wf.add_task(fetch)
    wf.add_task(mean)
    wf.run()

    bundle = next(Path(base, ".dagon", "fair", "Fair45").iterdir())
    print("bundle:", sorted(p.name for p in bundle.iterdir()))
    exported = "".join(p.read_text() for p in bundle.iterdir() if p.is_file())
    print("secret in the bundle:", SECRET in exported)
    crate = json.loads((bundle / "ro-crate-metadata.json").read_text())
    names = sorted(i.get("name") for i in crate["@graph"] if i.get("@type") == "File")
    print("files described in the RO-Crate:", names)
    check(SECRET not in exported, "configuration secrets never reach metadata")
