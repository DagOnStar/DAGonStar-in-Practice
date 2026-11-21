# 38. Apptainer tasks

*Containers on HPC without a daemon: SIF images, overlays, bind mounts and staging*

Workflows in Practice with DAGonStar - Part 4: Infrastructure, FAIR and applications. Slides: [38-DAGonStar-Apptainer_tasks.pptx](../lectures/38-DAGonStar-Apptainer_tasks.pptx). Examples: [examples/38-apptainer](../../examples/38-apptainer/).

## 2. Today's lecture

**Outline**

1. Why Apptainer on clusters
2. The APPTAINER task
3. SIF images: build or reuse
4. Overlays, binds and the working directory
5. Hands-on: the commands DAGonStar runs
6. Remote Apptainer

**After this lecture you can**

- Run a step in an Apptainer image
- Choose between building and reusing a SIF
- Read the apptainer exec command line

## 3. Apptainer

*Formerly Singularity: containers that run as the user, with no root daemon.*

## 4. Docker and Apptainer

**Docker**

- Root daemon
- Common on laptops and clouds
- Images in registries
- Rarely allowed on HPC

**Apptainer**

- No daemon, runs as you
- Standard on HPC clusters
- Single-file SIF images
- Can pull docker:// images

## 5. Why it fits HPC

- **Security** - Your user inside, your permissions outside.
- **Files** - One .sif file on the shared file system.
- **MPI and GPUs** - Host libraries and devices bound in.
- **Schedulers** - Runs inside a Slurm job like any program.

## 6. The APPTAINER task

*Image, binds, overlay size and a temporary directory.*

## 7. Creating an Apptainer task

[`examples/38-apptainer/apptainer_task.py`](../../examples/38-apptainer/apptainer_task.py)

```python
task = DagonTask(TaskType.APPTAINER, "roms", "python run_roms.py",
                 image="docker://python:3.12-slim", tmp_dir=str(base))
print("type:", type(task).__name__, isinstance(task, ApptainerTask))
```

- image: a docker:// URI
- tmp_dir: where SIF and overlay go
- Default image: docker://ubuntu:20.04
- A Batch subclass

## 8. Arguments

| Argument | Meaning |
|---|---|
| `image` | docker://..., another URI, or a path to a .sif |
| `bind_paths` | Extra host paths to bind into the container |
| `overlay_size` | Writable overlay in MB (default 1024) |
| `tmp_dir` | Directory for temporary files |
| `remove` | Clean up container files when collected |
| `ip, ssh_username, keypath` | RemoteApptainerTask on another host |

## 9. SIF images

*Build once from a URI, or point at a .sif that already exists.*

## 10. _prepare_sif_image

```
if self.image.endswith(".sif"):
    if os.path.exists(self.image):
        self.sif_file = self.image          # reuse
    else:
        raise FileNotFoundError("SIF file not found: " + self.image)
else:
    self.sif_file = os.path.join(self.work_dir, self.name + ".sif")
    build_cmd = ["apptainer", "build", self.sif_file, self.image]
    # on failure, retried once with sudo
```

- A .sif is reused
- A missing .sif is an error
- A URI is built per task

## 11. Build or reuse

- **Building** slow, needs network, done in the task folder
- **Reusing** instant: a .sif on the shared file system
- **Practice** build once, store in a project directory
- **Workflow** image="/projects/meteo/roms.sif"
- **Record** the SIF's sha256 with the results

> *Recorded output*
>
> An existing .sif is used as it is.

```
prebuilt SIF rebuilt:
  False
```

## 12. Running

*Every command runs through apptainer exec with an overlay and bind mounts.*

## 13. exec_in_container

```
exec_cmd = ["apptainer", "exec"]
exec_cmd.extend(["--overlay", self.overlay_file])
for bind_path in self.bind_paths:
    exec_cmd.extend(["--bind", bind_path])
exec_cmd.extend(["--bind", self.work_dir + ":" + self.container_work_dir])
exec_cmd.extend(["--bind", self.staging_dir + ":/staging"])
exec_cmd.extend(["--pwd", self.container_work_dir])
exec_cmd.extend([self.sif_file, "bash", "-c", command])
```

- A writable overlay
- Your binds first
- Work dir and staging
- Start in the work dir

## 14. Flags

| Flag | Purpose |
|---|---|
| `--overlay` | A writable layer on a read-only image |
| `--bind host:ctr` | Make a host directory visible inside |
| `--pwd` | Start the command in the container work dir |
| `bash -c` | Run the command string |

## 15. Lifecycle

1. **SIF** - Build or reuse.
2. **Overlay** - Create a writable layer.
3. **Stage in** - Copy inputs via /staging.
4. **Exec** - Run the command.
5. **Clean** - On collection.

## 16. Hands-on

*subprocess.run is mocked: we read the exact commands DAGonStar would run.*

## 17. Capturing the commands

[`examples/38-apptainer/apptainer_task.py`](../../examples/38-apptainer/apptainer_task.py)

```python
done = mock.Mock(stdout="ok", stderr="", returncode=0)
quiet = redirect_stdout(io.StringIO())     # the backend reports progress
with quiet, mock.patch("dagon.apptainer_task.subprocess.run", return_value=done) as run:
    task._prepare_sif_image()
    build = list(run.call_args[0][0])
    task.overlay_file = os.path.join(str(base), "overlay.img")
    task.staging_dir = os.path.join(str(base), "staging")
    task.bind_paths = []
    task.exec_in_container("python run_roms.py")
    execute = list(run.call_args[0][0])
```

- The mock records the argument lists passed to subprocess.run
- Overlay and staging paths are set by hand, as pre_process_command would

## 18. Recorded output

Recorded output of `python examples/38-apptainer/apptainer_task.py`:

```text
type: ApptainerTask True
build: apptainer build docker://python:3.12-slim
exec flags: ['--overlay', '--bind', '--bind', '--pwd']
image file: .sif
prebuilt SIF rebuilt: False
```

- An ApptainerTask
- apptainer build from docker://
- overlay, two binds, pwd
- A .sif file
- Prebuilt SIF not rebuilt

## 19. Reading the exec flags

- **--overlay** one writable layer
- **--bind, --bind** work dir and staging (no extra binds here)
- **--pwd** the container work dir
- **Then** the SIF, bash -c and the command
- **Add** bind_paths=["/data/era5"] for inputs outside the scratch

> *Recorded output*
>
> Flags in order.

```
['--overlay', '--bind',
 '--bind', '--pwd']
```

## 20. Cleaning up

- **on_garbage** cleanup_container, then the usual handling
- **remove=True** the container work folder is deleted
- **remove=False** default: files stay for inspection
- **References** SIF, overlay and staging paths cleared
- **A prebuilt .sif** is never deleted: it is not in the work folder

> *Overlays are big*
>
> Use remove=True in long workflows.

## 21. Image sources

| image | Meaning |
|---|---|
| `docker://python:3.12-slim` | Pull from a Docker registry and build a SIF |
| `library://...` | Pull from a Sylabs library |
| `/projects/x/model.sif` | Use an existing SIF file |
| `Default` | docker://ubuntu:20.04 |

## 22. Remote and HPC

*RemoteApptainerTask runs the same commands over SSH; Slurm runs them on compute nodes.*

## 23. RemoteApptainerTask

- **ip given** DagonTask returns the remote class
- **Commands** the same, sent through the SSH connection
- **SIF check** test -f on the remote host
- **Files** exported and imported via the staging folder
- **Typical** a login node of a cluster

> *Same task, another host*
>
> The workflow script does not change.

## 24. Apptainer and Slurm

- **Option A** - SLURM task whose command is apptainer exec ... (lecture 41).
- **Option B** - APPTAINER task on a login node for light steps.
- **GPUs** - apptainer exec --nv in the command.
- **MPI** - Host MPI bound in: same version inside and out.

## 25. Troubleshooting

| Symptom | Likely cause |
|---|---|
| apptainer: command not found | Module not loaded: module load apptainer |
| build fails | No fakeroot; build elsewhere and copy the .sif |
| SIF file not found | Wrong path or not on the shared file system |
| No space left | overlay_size or tmp_dir too small |
| File not found inside | Add the directory to bind_paths |

## 26. Run it for real

**Steps**

1. Run the example
2. On a machine with Apptainer: apptainer build roms.sif docker://python:3.12-slim
3. Set image to the .sif path
4. Run a workflow with the task and read its log

**Run it**

```bash
python examples/\
  38-apptainer/\
  apptainer_task.py
```

**Watch for:** With a prebuilt SIF the task starts in seconds; building from docker:// takes minutes the first time.

## 27. This lecture's example

- **1** - Build command captured
- **4** - Flags on apptainer exec
- **0** - Rebuilds of a prebuilt SIF

## 28. Exercise

A. Add bind_paths=["/data"] and record the new exec flags
B. Point image at a missing .sif and catch the error
C. Write the SLURM version of the command (lecture 41)
D. Compare both approaches in two sentences

**Deliverable:** The flags, the error message and the comparison.

## 29. Check your understanding

1. Why is Apptainer preferred over Docker on HPC?
2. When is a SIF image not rebuilt?
3. What does --overlay provide?
4. How do you make /data visible inside the container?

<details><summary>Answers</summary>

1. It needs no root daemon and runs with the user's own permissions.
2. When image is a path to an existing .sif file.
3. A writable layer on top of the read-only image.
4. Add it to bind_paths: --bind /data.

</details>

## 30. Key takeaways

1. Apptainer runs containers as the user, without a daemon
2. SIF images are built from URIs or reused from files
3. Commands run with an overlay, binds and a pwd
4. The same task works remotely and under Slurm

*Next: Kubernetes and Nomad*

---

Raffaele Montella. CC0 1.0. Generated from `src/lectures/38.js`.
