"""Appendix A2: volume tasks - create a volume, share it through workflow://, stream, release.

The first run serves the volume with the local-directory adapter of local_directory.py:

    fetch -> Gulf (TaskType.VOLUME: create "gulf", stage in the observations)
    Gulf  -> mean_NAP, mean_CAP, mean_ISC   write into workflow:///Gulf/gulf/means/
    Gulf  -> split ~~stream~~> count        count reads each station's records while split runs
    all   -> Collect (destroy "gulf", stage out means/ into Collect's folder)
    Collect -> report                       reads workflow:///Collect/means/... like any folder

The second run builds the same graph for the dagonfs provider under portable emulation (a
local folder stands in for the volume: no DAGonFS is started) and has no destroy task, so the
volume is released by reference counting when its last user has finished, and report, which
reads the means inside the volume, is ordered after their writers by hand.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import local_directory  # noqa: F401  (registers the "local-directory" provider)
from dagon import Status
from dagon.task import DagonTask, TaskType
from common.course import STATIONS, check, fetch_observations, scratch, text, workflow

VOLUME = "workflow:///Gulf/gulf"
MEAN = ("awk -F, -v s={s} '$1==s{{t+=$3;n++}}END{{printf \"%s %.2f\\n\", s, t/n}}' "
        + VOLUME + "/inputs/observations.csv > " + VOLUME + "/means/{s}.txt")
SPLIT = ("for s in NAP CAP ISC; do grep ^$s " + VOLUME + "/inputs/observations.csv > $s.csv; "
         '"$DAGON_PYTHON" -m dagon.adhoc stream publish "$DAGON_STREAM_OUT" $s.csv; done')
COUNT = ('n=0; for item in $("$DAGON_PYTHON" -m dagon.adhoc stream items '
         "workflow:///split/stations?stream=gulf --into got); do "
         'n=$((n + $(wc -l < "$item"))); done; echo $n > records.txt')


def build(base, name, provider, emulate, destroy):
    wf = workflow(name, base / name, portable_emulation=emulate)
    fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations() + " && mkdir -p means")
    gulf = DagonTask(TaskType.VOLUME, "Gulf", provider=provider, volume="gulf",
                     stage_in={"inputs/observations.csv": "workflow:///fetch/outputs/observations.csv",
                               "means": {"path": "workflow:///fetch/means", "type": "directory"}})
    tasks = [fetch, gulf] + [DagonTask(TaskType.BATCH, "mean_" + s, MEAN.format(s=s)) for s in STATIONS]
    tasks += [DagonTask(TaskType.BATCH, "split", SPLIT), DagonTask(TaskType.BATCH, "count", COUNT)]
    if destroy:
        tasks.append(DagonTask(TaskType.VOLUME, "Collect", action="destroy", volume=VOLUME,
                               stage_out={"means": {"path": VOLUME + "/means", "type": "directory"}}))
        source = "workflow:///Collect/means"
    else:
        source = VOLUME + "/means"
    tasks.append(DagonTask(TaskType.BATCH, "report", "cat " + " ".join(
        "%s/%s.txt" % (source, s) for s in STATIONS) + " > report.txt"))
    for task in tasks:
        wf.add_task(task)
    if not destroy:
        # A reference into the volume makes an edge to the volume task, not to the task that
        # wrote the file: without Collect, report must be ordered after the writers by hand.
        for s in STATIONS:
            tasks[-1].add_dependency_to(tasks[2 + STATIONS.index(s)])
    return wf, {task.name: task for task in tasks}


with scratch("A2") as base:
    wf, t = build(base, "Volume", "local-directory", emulate=False, destroy=True)
    wf.make_dependencies()
    print("Gulf after:", sorted({p.name for p in t["Gulf"].prevs}))
    print("Collect after:", sorted(p.name for p in t["Collect"].prevs))
    print("bound to gulf:", sorted(task.name for task in t["Gulf"].filesystem.tasks))
    wf.run()
    print("report:", text(t["report"], "report.txt").replace("\n", " | ").strip(" |"))
    print("count read", text(t["count"], "records.txt").strip(), "records while split ran;",
          "streams from:", [p.name for p in t["count"].stream_prevs])
    print("volume gulf:", t["Gulf"].released)
    check(all(task.status is Status.FINISHED for task in wf.tasks), "every task finished")
    check(text(t["report"], "report.txt") == "NAP 15.50\nCAP 16.75\nISC 15.75\n", "station means")
    check(text(t["count"], "records.txt").strip() == "12", "12 records crossed the stream")
    check(t["Gulf"].released == "destroyed by Collect", "Collect released the volume")

    em, e = build(base, "Emulated", "dagonfs", emulate=True, destroy=False)
    em.run()
    print("emulated dagonfs report:", text(e["report"], "report.txt").replace("\n", " | ").strip(" |"))
    print("volume gulf:", e["Gulf"].released)
    check(text(e["report"], "report.txt") == text(t["report"], "report.txt"), "same result, other provider")
    check(e["Gulf"].released == "no task refers to it", "released by reference counting")
