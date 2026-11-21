# A3-meta

## `meta_task.py`

Appendix A3: meta-tasks - run workflows of other engines as DAGonStar tasks.

    fetch -> means (TaskType.META, command adapter: engines/station_engine.py)
    means -> warmest
    fetch -> records (TaskType.META, cwl adapter: engines/count_records.cwl)

Data moves only through workflow:// references; the engines are never
modified.  A second run with the same checkpoint file reuses the meta-task
after re-verifying its specification, workflow and data digests.  A Nextflow
meta-task then runs under portable emulation: the mock engine writes
placeholders, so neither Nextflow nor a network connection is needed.  The
CWL step needs cwltool (pip install cwltool) and is skipped without it.

```bash
python examples/A3-meta/meta_task.py
```

Recorded output: [`output/meta_task.txt`](output/meta_task.txt).
