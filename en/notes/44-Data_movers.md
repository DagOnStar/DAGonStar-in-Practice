# 44. Data movers

*How the stager chooses COPY, LINK, SCP, FTP or GridFTP, and how NORMAL, PARALLEL and SLURM modes run the transfers*

DAGonStar in Practice - Part 4: Infrastructure, FAIR and applications. Slides: [44-DAGonStar-Data_movers.pptx](../lectures/44-DAGonStar-Data_movers.pptx). Examples: [examples/44-movers](../../examples/44-movers/).

## 2. Today's lecture

**Outline**

1. References become transfers
2. Same host: COPY or LINK
3. Different hosts: SCP, FTP, GridFTP
4. Hands-on: the mover the stager picks
5. Transfer modes
6. Strict loops and failures

**After this lecture you can**

- Predict the mover for a pair of tasks
- Choose COPY or LINK
- Pick a transfer mode for many files

## 3. The stager

*Every workflow:// reference becomes a transfer from the producer's folder to the consumer's.*

## 4. Choosing a mover

1. **Same IP?** - Workflow mover.
2. **GridFTP?** - Both endpoints.
3. **SCP?** - SSH active.
4. **FTP?** - Server active.

## 5. Movers

| DataMover | Command or service | When |
|---|---|---|
| `COPY` | cp -r | Same host (default) |
| `LINK` | ln -sf | Same host, no copy |
| `SCP` | scp over SSH | Different hosts |
| `GRIDFTP` | Globus transfer | Endpoints on both sides |
| `FTP` | FTP download | An FTP server is active |

## 6. Same host

*The workflow's data mover, copied to tasks at add_task unless they set their own.*

## 7. COPY or LINK

**COPY**

- An independent copy
- Safe if the producer is collected
- Costs time and space
- Default

**LINK**

- A symbolic link, instant
- No extra space
- Breaks if the producer's folder moves
- Consumers must not modify inputs

## 8. Setting the mover

- **Workflow** wf.set_data_mover(DataMover.LINK)
- **Order** call it before add_task (lecture 13)
- **Task** task.set_data_mover(...) for one task
- **Garbage collection** renames folders: links then dangle
- **Rule** LINK with remove_dir=False, or for read-only inputs

> *A trap*
>
> Collected producers break links: COPY is the safe default.

## 9. Different hosts

*The context script reports which services each host has; the stager uses the first that works.*

## 10. Context information

- **context.sh** run on each host (lecture 13)
- **ip** the host's address
- **SCP, FTP, GRIDFTP** active or none
- **endpoint** a Globus endpoint id, if any
- **user** the remote user

> *get_info()*
>
> Mocked in the example.

```
{"ip": "10.0.0.1",
 "SCP": "active",
 "FTP": "none",
 "GRIDFTP": "none"}
```

## 11. GridFTP via Globus

| Setting | Where |
|---|---|
| `clientid` | [globus] section of dagon.ini |
| `intermediate_endpoint` | [globus]: relay for hosts without direct access |
| `globusendpoint` | Per task: its endpoint id |
| `GlobusManager` | Receives source, destination, client, relay |

## 12. Hands-on

*Mocked tasks with chosen IPs and services; the stager generates real scripts.*

## 13. Mock tasks

[`examples/44-movers/data_movers.py`](../../examples/44-movers/data_movers.py)

```python
def task(ip, endpoint=None, remote=False):
    item = mock.Mock(spec=RemoteTask) if remote else mock.Mock()
    item.get_info.return_value = {"ip": ip, "SCP": "active", "FTP": "none",
                                  "GRIDFTP": "active" if endpoint else "none"}
    item.get_scratch_dir.return_value = item.working_dir = "/scratch/" + ip
    item.get_endpoint.return_value = endpoint
    item.get_user.return_value = "student"
    item.get_ip.return_value = ip
    return item
```

- Each mock reports an IP, its services and, optionally, a Globus endpoint
- remote=True makes the producer look like a RemoteTask

## 14. Four situations

[`examples/44-movers/data_movers.py`](../../examples/44-movers/data_movers.py)

```python
for mover in (DataMover.COPY, DataMover.LINK):
    script = Stager(mover, StagerMover.NORMAL, cfg).stage_in(
        task("10.0.0.1"), task("10.0.0.1"), "/scratch/dst", "outputs/obs.csv")
    verb = "cp -r" if "cp -r" in script else "ln -sf" if "ln -sf" in script else "?"
    print("same host, %-4s -> %s" % (mover.name, verb))

stager = Stager(DataMover.COPY, StagerMover.NORMAL, cfg)
script = stager.stage_in(task("10.0.0.2"), task("10.0.0.1", remote=True),
                         "/scratch/dst", "outputs/obs.csv")
print("different hosts     ->", stager.last_data_mover.name,
      "| uses", "student@10.0.0.1" if "student@10.0.0.1" in script else "?")

with mock.patch("dagon.communication.data_transfer.GlobusManager") as globus:
    stager.stage_in(task("10.0.0.2", endpoint="ep-hpc"), task("10.0.0.1", endpoint="ep-lab"),
                    "/scratch/dst", "outputs/obs.csv")
print("Globus endpoints    ->", stager.last_data_mover.name,
```

- Same host with COPY and LINK; different hosts; both with Globus endpoints
- last_data_mover says which mover was chosen

## 15. Recorded output

Recorded output of `python examples/44-movers/data_movers.py`:

```text
same host, COPY -> cp -r
same host, LINK -> ln -sf
different hosts     -> SCP | uses student@10.0.0.1
Globus endpoints    -> GRIDFTP | manager: ('ep-lab', 'ep-hpc', 'course-client', 'ep-relay')
strict loop records failures: True
modes: {'NORMAL': 0, 'PARALLEL': 1, 'SLURM': 2}
```

- cp -r and ln -sf
- SCP as student@10.0.0.1
- GridFTP with four arguments
- Strict loop
- Three modes

## 16. Decisions

| Situation | Mover |
|---|---|
| Same IP, workflow COPY | COPY: cp -r |
| Same IP, workflow LINK | LINK: ln -sf |
| Different IPs, SSH active | SCP |
| Different IPs, both with Globus endpoints | GRIDFTP |

## 17. Staged inputs in the consumer

- **Destination** inside the consumer's own folder
- **Command** the reference is rewritten to the staged path
- **Producer** untouched: consumers never write into it
- **Count** the producer's reference count is decremented after use
- **Then** garbage collection may rename the producer (lecture 14)

> *References are copies*
>
> Each consumer gets its own view of the input.

## 18. Moving data at scale

- **Fewer, larger files** - Archive many small files before moving them.
- **Move compute** - Run the consumer where the data are.
- **Shared file systems** - LINK, or no staging, on one cluster.
- **Pre-stage** - Transfer before asking for cores (lecture 43).

## 19. Transfer modes

*How the transfer commands themselves are run.*

## 20. StagerMover

| Mode | Value | Runs transfers |
|---|---|---|
| `NORMAL` | `0` | One after another in the launcher |
| `PARALLEL` | `1` | With GNU parallel, -j threads |
| `SLURM` | `2` | As Slurm jobs: sbatch, then squeue |

## 21. Choosing a mode

- **NORMAL** - Few files: simplest, default.
- **PARALLEL** - Many files on one host: GNU parallel needed.
- **SLURM** - Huge transfers on a cluster: jobs of their own.
- **Measure** - Time a staging with each mode before choosing.

## 22. Failures

*A transfer loop over many files must not hide one failure.*

## 23. A strict loop

[`examples/44-movers/data_movers.py`](../../examples/44-movers/data_movers.py)

```python
strict = stager.generate_command("/scratch/src dir/*", "/scratch/dst",
                                 'cp -r "$file" "$dst"', StagerMover.NORMAL.value, strict=True)
print("strict loop records failures:", "dagon_stage_status=1" in strict)
print("modes:", {m.name: m.value for m in StagerMover})
```

- generate_command with strict=True for a folder with a space
- The generated loop records any failure in dagon_stage_status

## 24. Why strict

- **A for loop** returns the status of its last command
- **Without care** an early failed copy is forgotten
- **Strict** dagon_stage_status=1 on any failure
- **Then** the launcher exits non-zero: the task FAILS
- **Quoting** the source with a space stays one path

> *Recorded output*
>
> No silent partial staging.

```
strict loop records
failures: True
```

## 25. Troubleshooting

| Symptom | Likely cause |
|---|---|
| No such file in inputs | Reference path wrong, or producer collected |
| Dangling link | LINK with a collected producer |
| scp: permission denied | Key or user wrong on the producer host |
| Globus transfer never ends | Endpoint not activated |
| parallel: command not found | PARALLEL mode without GNU parallel |

## 26. Run and vary

**Steps**

1. Run the example
2. Make the remote producer report SCP none and FTP active
3. Run again: which mover?
4. Print the full SCP script

**Run it**

```bash
python examples/\
  44-movers/\
  data_movers.py
```

**Watch for:** The stager walks the list in order: GridFTP, SCP, FTP; the first service both sides support wins.

## 27. This lecture's example

- **5** - Movers
- **3** - Transfer modes
- **4** - Situations tested

## 28. Exercise

A. Set the workflow mover to LINK in the station pipeline (lecture 12)
B. Enable remove_dir and run
C. Find the dangling link
D. Fix it two ways

**Deliverable:** The broken run, the dangling link and the two fixes.

## 29. Check your understanding

1. Which mover is used between two tasks on the same host?
2. When does the stager choose GridFTP?
3. What does PARALLEL mode need?
4. Why use a strict loop?

<details><summary>Answers</summary>

1. The workflow's data mover: COPY (cp -r) by default, or LINK (ln -sf).
2. When both tasks have Globus endpoints and GridFTP is active.
3. GNU parallel on the host running the launcher.
4. So that one failed transfer among many fails the staging instead of being hidden.

</details>

## 30. Key takeaways

1. References become transfers chosen by the stager
2. Same host: COPY or LINK; other hosts: GridFTP, SCP, FTP
3. NORMAL, PARALLEL and SLURM run transfers differently
4. Strict loops make every failed transfer visible

*Next: FAIR workflows*

---

Raffaele Montella. CC0 1.0. Generated from `src/lectures/44.js`.
