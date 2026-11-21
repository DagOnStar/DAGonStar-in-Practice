"""Appendix A2: volume tasks - create a volume, share it, stream, release.

The first run serves the volume with the local-directory adapter of
local_directory.py:

    fetch -> Gulf (TaskType.VOLUME: create "gulf", stage in the data)
    Gulf  -> mean_NAP, mean_CAP, mean_ISC: write into the volume
    Gulf  -> split ~~stream~~> count: count reads while split runs
    all   -> Collect (destroy "gulf", stage out means/)
    Collect -> report: reads workflow:///Collect/means/... as files

The second run builds the same graph for the dagonfs provider under
portable emulation (a local folder stands in for the volume: no DAGonFS
is started) and has no destroy task.  The volume is then released by
reference counting when its last user has finished, and report, which
reads the means inside the volume, is ordered after their writers by hand.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import local_directory  # noqa: F401  (registers "local-directory")
from dagon import Status
from dagon.task import DagonTask, TaskType
from common.course import (STATIONS, check, fetch_observations, scratch,
                           text, workflow)

FETCHED = "workflow:///fetch/outputs/observations.csv"
VOLUME = "workflow:///Gulf/gulf"
OBS = VOLUME + "/inputs/observations.csv"
MEAN = ("awk -F, -v s={s} '$1==s{{t+=$3;n++}}"
        "END{{printf \"%s %.2f\\n\", s, t/n}}' "
        + OBS + " > " + VOLUME + "/means/{s}.txt")
SPLIT = ("for s in NAP CAP ISC; do "
         "grep ^$s " + OBS + " > $s.csv; "
         '"$DAGON_PYTHON" -m dagon.adhoc stream publish '
         '"$DAGON_STREAM_OUT" $s.csv; done')
COUNT = ('n=0; for item in $("$DAGON_PYTHON" -m dagon.adhoc '
         "stream items workflow:///split/stations?stream=gulf "
         "--into got); do "
         'n=$((n + $(wc -l < "$item"))); done; '
         "echo $n > records.txt")


def batch(name, command):
    return DagonTask(TaskType.BATCH, name, command)


def build(base, name, provider, emulate, destroy):
    wf = workflow(name, base / name, portable_emulation=emulate)
    fetch = batch("fetch", fetch_observations() + " && mkdir -p means")
    gulf = DagonTask(
        TaskType.VOLUME, "Gulf", provider=provider, volume="gulf",
        stage_in={"inputs/observations.csv": FETCHED,
                  "means": {"path": "workflow:///fetch/means",
                            "type": "directory"}})
    means = [batch("mean_" + s, MEAN.format(s=s)) for s in STATIONS]
    tasks = [fetch, gulf, *means,
             batch("split", SPLIT), batch("count", COUNT)]
    if destroy:
        tasks.append(DagonTask(
            TaskType.VOLUME, "Collect", action="destroy", volume=VOLUME,
            stage_out={"means": {"path": VOLUME + "/means",
                                 "type": "directory"}}))
        source = "workflow:///Collect/means"
    else:
        source = VOLUME + "/means"
    files = " ".join("%s/%s.txt" % (source, s) for s in STATIONS)
    report = batch("report", "cat " + files + " > report.txt")
    tasks.append(report)
    for task in tasks:
        wf.add_task(task)
    if not destroy:
        # A reference into the volume makes an edge to Gulf, not to the
        # writer: without Collect, order report after the writers by hand.
        for mean in means:
            report.add_dependency_to(mean)
    return wf, {task.name: task for task in tasks}


def means_of(task):
    return text(task, "report.txt").replace("\n", " | ").strip(" |")


with scratch("A2") as base:
    wf, t = build(base, "Volume", "local-directory",
                  emulate=False, destroy=True)
    wf.make_dependencies()
    print("Gulf after:", sorted({p.name for p in t["Gulf"].prevs}))
    print("Collect after:")
    print("  ", " ".join(sorted(p.name for p in t["Collect"].prevs)))
    wf.run()
    print("report:", means_of(t["report"]))
    print("count read", text(t["count"], "records.txt").strip(),
          "records from", [p.name for p in t["count"].stream_prevs])
    print("volume gulf:", t["Gulf"].released)
    check(all(task.status is Status.FINISHED for task in wf.tasks),
          "every task finished")
    check(means_of(t["report"]) == "NAP 15.50 | CAP 16.75 | ISC 15.75",
          "station means")
    check(text(t["count"], "records.txt").strip() == "12",
          "12 records crossed the stream")
    check(t["Gulf"].released == "destroyed by Collect",
          "Collect released the volume")

    em, e = build(base, "Emulated", "dagonfs", emulate=True, destroy=False)
    em.run()
    print("emulated:", means_of(e["report"]))
    print("volume gulf:", e["Gulf"].released)
    check(means_of(e["report"]) == means_of(t["report"]),
          "same result, other provider")
    check(e["Gulf"].released == "no task refers to it",
          "released by reference counting")
