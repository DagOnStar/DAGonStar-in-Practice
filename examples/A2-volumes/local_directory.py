"""Appendix A2: a complete ad-hoc file-system adapter, and workflow- and task-scope volumes.

LocalDirectory serves a plain local directory through DAGonStar's common ad-hoc
interface (dagon.adhoc).  One class and one register_provider() call are all a new
storage system needs: neither DAGonStar nor the storage software changes.  The
directory is real, so the example needs no DAGonFS, MPI or FUSE.  The other A2
example imports this module to serve its volumes.

The workflow shares one workflow-scope volume between fetch and mean_CAP (its path
is exported as $GULF) and gives mean_CAP a private task-scope volume as well.
"""
import os
import shutil
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dagon.adhoc import AdHocFileSystem, register_provider


class LocalDirectory(AdHocFileSystem):
    """A directory created when the resource starts and removed when it stops."""

    provider = "local-directory"
    access = "posix"                 # tasks open its paths with ordinary file calls
    supports_streaming = True        # so the provider-neutral stream store works on it

    def __init__(self, workflow, name="default", path=None):
        super().__init__(workflow, name)
        self.path = path or os.path.join(workflow.get_scratch_dir_base(), ".volume-" + name)

    @property
    def task_path(self):
        return self.path             # becomes $DAGON_ADHOC_<NAME>_PATH in bound tasks

    def start(self):
        if self.started or self.workflow.portable_emulation:
            return
        os.makedirs(self.path, exist_ok=True)
        self._started = True

    def is_ready(self):
        return self.started and os.path.isdir(self.path)

    def stop(self):
        if not self.started:
            return None
        self._started = False
        shutil.rmtree(self.path, ignore_errors=True)
        return 0


register_provider("local-directory", LocalDirectory, replace=True)


def main():
    from dagon.task import DagonTask, TaskType
    from common.course import DATA, check, scratch, text, workflow

    with scratch("A2") as base:
        wf = workflow("Adhoc", base)
        fetch = DagonTask(TaskType.BATCH, "fetch", 'cp %s "$GULF/observations.csv"' % DATA)
        mean = DagonTask(TaskType.BATCH, "mean_CAP",
                         'grep ^CAP "$GULF/observations.csv" > "$DAGON_ADHOC_TMP_PATH/cap.csv" && '
                         "awk -F, '{t+=$3;n++}END{printf \"CAP %.2f\\n\", t/n}' "
                         '"$DAGON_ADHOC_TMP_PATH/cap.csv" > CAP.txt && echo "$DAGON_ADHOC_NAMES" > names.txt')
        wf.add_task(fetch)
        wf.add_task(mean)
        mean.add_dependency_to(fetch)                  # no workflow:// reference: say the order
        shared = wf.create_adhoc_filesystem("local-directory", name="gulf", export="GULF")
        shared.bind(fetch)
        shared.bind(mean)
        private = mean.create_adhoc_filesystem("local-directory", name="tmp")
        wf.run()

        print("scopes:", shared.metadata()["scope"], "and", private.metadata()["scope"])
        print("mean_CAP bound to:", text(mean, "names.txt").strip())
        print("result:", text(mean, "CAP.txt").strip())
        print("after the run: gulf exists =", os.path.exists(shared.path),
              "| tmp exists =", os.path.exists(private.path))
        check(text(mean, "CAP.txt").strip() == "CAP 16.75", "Capri mean from the shared volume")
        check(text(mean, "names.txt").split() == ["gulf,tmp"], "both volumes bound to mean_CAP")
        check(not shared.started and not private.started, "both volumes stopped")
        check(not os.path.exists(shared.path) and not os.path.exists(private.path), "both directories removed")


if __name__ == "__main__":
    main()
