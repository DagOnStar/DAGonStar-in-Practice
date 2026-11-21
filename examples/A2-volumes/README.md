# A2-volumes

## `local_directory.py`

Appendix A2: a complete ad-hoc file-system adapter, and workflow- and task-scope volumes.

LocalDirectory serves a plain local directory through DAGonStar's common ad-hoc
interface (dagon.adhoc).  One class and one register_provider() call are all a new
storage system needs: neither DAGonStar nor the storage software changes.  The
directory is real, so the example needs no DAGonFS, MPI or FUSE.  The other A2
example imports this module to serve its volumes.

The workflow shares one workflow-scope volume between fetch and mean_CAP (its path
is exported as $GULF) and gives mean_CAP a private task-scope volume as well.

```bash
python examples/A2-volumes/local_directory.py
```

Recorded output: [`output/local_directory.txt`](output/local_directory.txt).

## `volume_task.py`

Appendix A2: volume tasks - create a volume, share it, stream, release.

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

```bash
python examples/A2-volumes/volume_task.py
```

Recorded output: [`output/volume_task.txt`](output/volume_task.txt).
