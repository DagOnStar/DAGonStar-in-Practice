# 13. Staging modes

*COPY, LINK and DONTMOVE on the same graph, how the stager chooses a mover, and the NORMAL, PARALLEL and SLURM modes*

DAGonStar in Practice - Part 2: Execution, data and recovery. Slides: [13-DAGonStar-Staging_modes.pptx](../lectures/13-DAGonStar-Staging_modes.pptx). Examples: [examples/13-staging](../../examples/13-staging/).

## 2. Today's lecture

**Outline**

1. What staging is for
2. How the stager chooses a mover
3. COPY, LINK and DONTMOVE compared
4. Stager modes: NORMAL, PARALLEL, SLURM
5. Hands-on: one graph, three movers
6. Choosing a mover

**After this lecture you can**

- Set the data mover of a workflow
- Predict the effect of each local mover
- Explain why DONTMOVE makes the consumer fail here

## 3. Staging

*A task never reads another task's folder directly: its inputs are brought into its own folder first.*

## 4. Why stage at all

- **Isolation** a consumer cannot damage the producer's files
- **Location** producer and consumer may be on different machines
- **Uniform paths** the command always reads from .dagon/inputs/...
- **Audit** the launcher records how each input arrived
- **Clean-up** producer folders can be collected after staging (lecture 14)

> **1** - *Rule*
>
> Inputs arrive in the consumer's folder before its command starts.

## 5. How a mover is chosen

```
data_mover = DataMover.DONTMOVE
if dst_info is not None and src_info is not None:
    if dst_info["ip"] == src_info["ip"]:
        data_mover = self.data_mover     # COPY by default
    else:
        for p in ["GRIDFTP", "SCP", "FTP"]:
            if src_info[p] is ACTIVE:
                data_mover = DataMover[p]
                ...
else:                                     # best effort
    data_mover = self.data_mover
```

- Same host: the configured mover
- Different hosts: the first active protocol
- GRIDFTP needs Globus endpoints
- Default: COPY

## 6. Movers for other places

- **SCP, SFTP, FTP** - Producer on another host reachable over SSH or FTP.
- **HTTP, HTTPS** - Producer folder published by a web server.
- **GRIDFTP** - Globus endpoints and a client id in [globus].
- **SKYCDS, DYNOSTORE** - Research data stores, with upload and download.

> **Lecture 44** the remote movers, with the station data and mocked endpoints.

## 7. Local movers

*On one machine the choice is between a copy, a link, or trusting that the path already works.*

## 8. COPY, LINK, DONTMOVE

| Mover | Command in the launcher | Consumer sees | Cost |
|---|---|---|---|
| COPY | `cp -r "$file" "$dst"` | An independent copy | Time and disk |
| LINK | `ln -sf "$file" "$dst"` | A symbolic link | Almost free |
| DONTMOVE | `(nothing)` | A path to a missing file | Free, but fails |

## 9. COPY or LINK

**COPY**

- Safe: the consumer may modify its input
- Survives removal of the producer's folder
- Doubles the disk space
- Slow for large files

**LINK**

- Instant, no extra space
- The consumer must not write to the input
- Breaks if the producer's folder is removed
- Same file system only

## 10. DONTMOVE

- **What it does** rewrites the URL into the staged path, moves nothing
- **On one machine** the staged path does not exist: the consumer fails
- **When it is useful** data already present at that path by other means
- **Examples** a shared file system with pre-placed inputs, BeeOND, pre-staging
- **Lesson** DONTMOVE is a promise you must keep yourself

> *This lecture's run*
>
> Exactly as expected.

```
DONTMOVE staged=none
  consumer=FAILED
```

## 11. Hands-on

*The same two-task graph run three times, once per mover.*

## 12. staging_modes.py

[`examples/13-staging/staging_modes.py`](../../examples/13-staging/staging_modes.py)

```python
def run(mover):
    with scratch("13") as base:
        wf = workflow("Staging13", base)
        wf.set_data_mover(mover)
        fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations())
        mean = DagonTask(TaskType.BATCH, "mean",
                         station_mean("ISC", SOURCE, "outputs/mean.txt"))
        wf.add_task(fetch)
        wf.add_task(mean)
        wf.run()
        staged = list(Path(mean.working_dir, ".dagon", "inputs").rglob("*.csv"))
        kind = ("none" if not staged else
                "symlink" if staged[0].is_symlink() else "copy")
        print("%-8s staged=%-7s consumer=%s" % (mover.name, kind, mean.status.name))
        return kind, mean.status.name
```

- set_data_mover applies to every task of the workflow
- The staged CSV is classified as a copy, a link or missing

## 13. Three runs, three checks

[`examples/13-staging/staging_modes.py`](../../examples/13-staging/staging_modes.py)

```python
results = {mover.name: run(mover)
           for mover in (DataMover.COPY, DataMover.LINK, DataMover.DONTMOVE)}
check(results["COPY"] == ("copy", "FINISHED"), "COPY materialises a copy")
check(results["LINK"] == ("symlink", "FINISHED"), "LINK creates a symlink")
check(results["DONTMOVE"] == ("none", "FAILED"), "DONTMOVE moves nothing")
```

- A dict comprehension runs the graph per mover
- Each result is checked: the example fails if a mover changes behaviour

## 14. Recorded output

Recorded output of `python examples/13-staging/staging_modes.py`:

```text
COPY     staged=copy    consumer=FINISHED
LINK     staged=symlink consumer=FINISHED
DONTMOVE staged=none    consumer=FAILED
```

- COPY: a real file
- LINK: a symlink
- DONTMOVE: nothing, the consumer fails
- The ISC mean is 15.75 in the first two

## 15. Why the failure is silent

- **logging.disable** the example silences the expected traceback
- **run()** returns normally even though mean FAILED
- **Status** the only signal is mean.status
- **In your workflows** leave logging on and check statuses
- **Lecture 16** failure propagation in detail

> *Only in examples*
>
> Used where a failure is the point of the demo.

```
logging.disable(
  logging.CRITICAL)
```

## 16. Compare the launchers

**Steps**

1. Keep the scratch of the COPY and LINK runs
2. Open .dagon/launcher.sh in each consumer
3. Find the Add the copy / link command section
4. Run ls -l in .dagon/inputs/... for both

**Run it**

```bash
python examples/\
  13-staging/\
  staging_modes.py
```

**Watch for:** cp -r in one launcher, ln -sf in the other; ls -l shows an arrow for the link.

## 17. Stager modes

*How the transfers of one task are executed: one by one, in parallel, or as cluster jobs.*

## 18. StagerMover

| Mode | Value | Launcher behaviour | When |
|---|---|---|---|
| `NORMAL` | 0 | eval each copy in sequence | Few inputs: the default |
| `PARALLEL` | 1 | GNU parallel -j<threads> over the files | Many small files, one node |
| `SLURM` | 2 | sbatch one job per copy, wait with squeue | Big transfers on a cluster |

> **Set it with set_stager_mover** per workflow or per task. threads in [batch] is the parallel width.

## 19. The generated loop

```
for file in $src
do
cmd="cp -r \"$file\" \"$dst\""
case $mode in
    1) find $src -type f,l | parallel -j$jobs "$cmd"; break ;;
    2) job_id=$(sbatch --job-name=stagein ... --wrap="$cmd" \
                | awk '{print $4}')
       job_ids+=($job_id) ;;
    *) eval "$cmd" ;;
esac
done
```

- mode comes from the stager mover
- jobs from threads in [batch]
- SLURM mode waits for the jobs before invoking the command

## 20. Requirements of each mode

- **NORMAL** - bash and cp or ln. Nothing else.
- **PARALLEL** - GNU parallel installed on the machine running the launcher.
- **SLURM** - sbatch and squeue: a Slurm login or compute node.

## 21. Choosing

*Small data: COPY. Large read-only data on one file system: LINK. Pre-placed data: DONTMOVE.*

## 22. A decision table

| Situation | Mover | Mode |
|---|---|---|
| Laptop, small files | COPY | NORMAL |
| Large read-only inputs, same disk | LINK | NORMAL |
| Thousands of small files | COPY | PARALLEL |
| Cluster scratch, very large inputs | COPY | SLURM |
| Inputs already on BeeOND or pre-staged | DONTMOVE | n/a |
| Different hosts | SCP, SFTP or GRIDFTP | NORMAL |

## 23. Per-task settings

- **Workflow-wide** wf.set_data_mover(DataMover.LINK), before add_task
- **One task** task.set_data_mover(DataMover.COPY)
- **The task wins** add_task copies the workflow mover only if the task has none
- **Typical** LINK everywhere, COPY for the one task that edits its input
- **Stager mode** set_stager_mover(StagerMover.PARALLEL) the same way

> *Imports*
>
> DataMover is also re-exported by dagon.

```
from dagon import DataMover
from dagon.stager.base \
  import StagerMover
```

## 24. Order matters

```
# add_task in dagon/__init__.py
if task.data_mover is None:
    task.set_data_mover(self.data_mover)

# so this works:
wf.set_data_mover(DataMover.LINK)
wf.add_task(fetch)          # fetch gets LINK

# and this does not change fetch:
wf.add_task(fetch)          # fetch gets COPY
wf.set_data_mover(DataMover.LINK)
```

- The mover is copied when the task is added
- Set it first, as staging_modes.py does
- Or set it on each task

## 25. What the example shows

- **3** - Movers on the same graph
- **2** - Runs that finish
- **1** - Run that fails by design

## 26. Pitfalls

- **LINK and remove_dir** the producer folder is renamed: links dangle
- **LINK across machines** a symlink to a path that exists only elsewhere
- **PARALLEL without parallel** the launcher fails at staging
- **SLURM mode on a laptop** sbatch: command not found
- **Huge COPY on a small disk** the scratch fills up mid-run

> *Test small first*
>
> Run the graph on a sample before staging terabytes.

## 27. From reference to staged file

1. **Parse** - workflow:///fetch/...
2. **Choose** - Same host: COPY.
3. **Generate** - Write cp -r in the launcher.
4. **Run** - The copy lands in .dagon/inputs.
5. **Rewrite** - The command reads the copy.

## 28. Exercise

A. Add DataMover.LINK with remove_dir True and run
B. Observe what happens to the link after collection
C. Run the COPY case with StagerMover.PARALLEL
D. Check whether GNU parallel is installed on your machine

**Deliverable:** A table of the four runs: mover, mode, staged kind and consumer status, with a sentence explaining each.

## 29. Check your understanding

1. Which mover is the default on a single machine?
2. Why does the DONTMOVE consumer fail in this lecture?
3. What is the difference between a data mover and a stager mode?
4. When does the stager choose SCP instead of the configured mover?

<details><summary>Answers</summary>

1. COPY.
2. Its command reads the staged path, but nothing was moved there.
3. The mover decides how a file is transferred; the mode decides how the transfers are executed.
4. When producer and consumer are on different hosts and SCP is the first active protocol found.

</details>

## 30. Key takeaways

1. Inputs are staged into .dagon/inputs before the command runs
2. Same host: the configured mover, COPY by default
3. LINK is cheap but fragile; DONTMOVE only rewrites paths
4. NORMAL, PARALLEL and SLURM decide how transfers run

*Next: garbage collection of task folders*

---

Raffaele Montella. CC0 1.0. Generated from `src/lectures/13.js`.
