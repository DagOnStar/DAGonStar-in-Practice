# 23. Dry runs and portable emulation

*Planning a workflow without executing it, and running cluster task types on a laptop*

Workflows in Practice with DAGonStar - Part 2: Execution, data and recovery. Slides: [23-DAGonStar-Dry_runs_and_portable_emulation.pptx](../lectures/23-DAGonStar-Dry_runs_and_portable_emulation.pptx). Examples: [examples/23-dry-portable](../../examples/23-dry-portable/).

## 2. Today's lecture

**Outline**

1. Two ways not to run for real
2. Dry runs: set_dry(True)
3. What a dry run leaves behind
4. Portable emulation
5. A SLURM task on a laptop
6. When to use which

**After this lecture you can**

- Plan a workflow with a dry run
- Run a scheduler task locally with portable emulation
- Explain what each mode skips

## 3. Not running for real

*Before spending hours of cluster time, check the graph, the folders and the commands.*

## 4. Dry run and portable emulation

**Dry run**

- Builds folders and launchers
- Executes no command
- Statuses still reach FINISHED
- Answers: is the plan right?

**Portable emulation**

- Executes every command locally, with bash
- Ignores the backend: no sbatch, no Docker
- References point at producers' folders
- Answers: do the commands work?

## 5. Dry runs

*wf.set_dry(True): every task goes through its life cycle, but no launcher is executed.*

## 6. A dry run

[`examples/23-dry-portable/dry_and_portable.py`](../../examples/23-dry-portable/dry_and_portable.py)

```python
with scratch("23") as base:
    dry = workflow("Dry23", base)
    dry.set_dry(True)
    fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations())
    dry.add_task(fetch)
    dry.run()
    made = sorted(p.name for p in Path(fetch.working_dir).iterdir())
    print("dry run:", fetch.status.name, "| folder holds only", made)
    check(made == [".dagon"], "nothing was executed")
```

- set_dry(True) before run()
- The task folder exists but holds only .dagon: the launcher was written, never run

## 7. Where the dry flag acts

```
self.workflow._fire_event("on_task_execute_start", self)
if self.workflow.dry is False:
    start_time = time()
    self.result = self.on_execute(launcher_script,
                                  "launcher.sh")
    ...
# otherwise: the launcher is prepared and saved,
# nothing runs, the task is still FINISHED
```

- Staging plan and launcher are built
- on_execute is skipped
- Events still fire

## 8. What a dry run checks

- **Graph** edges, references and cycles are resolved
- **Names** every reference finds its producer
- **Folders** the scratch base is writable
- **Launchers** every command is written into .dagon/launcher.sh
- **Not checked** whether any command would succeed

> *Recorded output*
>
> A plan, not a result.

```
dry run: FINISHED
| folder holds
  only ['.dagon']
```

## 9. Reading a dry run

| Look at | To check |
|---|---|
| Status of every task | The graph was walked to the end |
| .dagon/launcher.sh | The rewritten commands and staging |
| The JSON export | Names, types and edges |
| Event log | The order tasks would follow |
| Pre-staged SLURM tasks | A side-effect-free plan (lecture 43) |

## 10. Dry runs and checkpoints

- **Folders** created, so a dry run leaves a scratch tree
- **Checkpoint records** dry tasks never executed: do not resume real runs from them
- **Separate files** use a different checkpoint_file for planning
- **Pre-staged tasks** their dry run creates no folder at all (lecture 43)
- **Clean-up** delete the dry scratch after reviewing it

> *Plans are not results*
>
> Keep dry and real runs apart on disk.

## 11. Portable emulation

*Workflow(..., portable_emulation=True): every command task runs locally with bash, whatever its type.*

## 12. A SLURM task on a laptop

[`examples/23-dry-portable/dry_and_portable.py`](../../examples/23-dry-portable/dry_and_portable.py)

```python
portable = workflow("Portable23", base, portable_emulation=True)
portable.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
model = DagonTask(TaskType.SLURM, "mean_ISC",
                  station_mean("ISC", SOURCE, "outputs/mean.txt"),
                  partition="compute", ntasks=4, time="00:10:00")
portable.add_task(model)
portable.run()
print("portable:", type(model).__name__, model.status.name,
      "| result:", text(model, "outputs/mean.txt").strip())
check(text(model, "outputs/mean.txt").strip() == "ISC 15.75", "Ischia")
```

- mean_ISC is a SLURM task with partition, ntasks and time
- No sbatch exists here: emulation runs the command with bash

## 13. Recorded output

Recorded output of `python examples/23-dry-portable/dry_and_portable.py`:

```text
dry run: FINISHED | folder holds only ['.dagon']
portable: Slurm FINISHED | result: ISC 15.75
```

- Dry: FINISHED, nothing executed
- Portable: still a Slurm object
- Result computed locally: ISC 15.75

## 14. execute_portable

```
def execute_portable(self):
    if self.reuse_checkpoint():
        return
    self.working_dir = <scratch>/<ts>-<name>
    self.initialize_checkpoint()
    completed = subprocess.run(
        [bash_executable(), "-c", self.portable_command()],
        cwd=self.working_dir, capture_output=True)
    self.workflow.checkpoints[key]["code"] = \
        completed.returncode
    if completed.returncode:
        raise RuntimeError("Portable task failed")
```

- No launcher, no backend
- Checkpoints still work
- Failures still fail

## 15. References in portable mode

- **No staging** nothing is copied into .dagon/inputs
- **Rewriting** workflow:///fetch/x becomes <fetch working_dir>/x
- **Direct read** the consumer reads the producer's file in place
- **Consequence** a consumer must not modify its inputs
- **Same results** for commands that only read their inputs

> *portable_command()*
>
> Replaces each reference to a predecessor with its real path.

## 16. What portable emulation is for

- **Teaching** - Every task type of this course runs on a laptop.
- **Development** - Debug SLURM and container workflows without a cluster.
- **CI** - Run the workflow in a test pipeline on every commit.
- **Review** - A colleague reproduces the logic without your accounts.

> **Structured tasks** LLM, FaaS and IoT tasks emulate their services too (lectures 27-32).

## 17. Real and emulated SLURM task

| Step | Real | Emulated |
|---|---|---|
| Folder | <scratch>/<ts>-mean_ISC | Same |
| Inputs | Staged into .dagon/inputs | Read in place |
| Submission | sbatch launcher.sh | none |
| Execution | On a compute node | bash -c on this machine |
| Options | partition, ntasks, time used | Ignored |
| Checkpoint | Recorded | Recorded |

## 18. Hands-on

*Plan, then emulate, then run for real.*

## 19. Plan and emulate

**Steps**

1. Run the example
2. Keep the dry scratch and read the launcher
3. Change the SLURM command to a typo
4. Run again: the dry part still passes, the portable part fails

**Run it**

```bash
python examples/\
  23-dry-portable/\
  dry_and_portable.py
```

**Watch for:** A dry run cannot see a broken command; emulation can.

## 20. A safe path to production

1. **Dry** - Graph and launchers.
2. **Portable** - Commands, locally.
3. **Small real** - One member on the cluster.
4. **Full** - Every member, with checkpoints.

## 21. Choosing

*Dry runs are free and catch structure errors; emulation costs local time and catches command errors.*

## 22. Which one catches what

| Error | Dry run | Portable | Real run |
|---|---|---|---|
| Unknown task in a reference | yes | yes | yes |
| Cycle | yes | yes | yes |
| Typo in a command | no | yes | yes |
| Wrong partition name | no | no | yes |
| Missing container image | no | no | yes |
| Slow or memory-hungry task | no | partly | yes |

## 23. Limits of emulation

- **Resources** ntasks=4 and time limits are ignored
- **Environment** the cluster's modules and paths are not there
- **Data** cluster-only inputs must be replaced by samples
- **Performance** tells nothing about speed on the cluster
- **Remote** SSH and cloud tasks also run locally

> **≈** - *Same logic, different machine*
>
> Emulation tests the workflow, not the platform.

## 24. Dry runs in meta-workflows

- **DAG_TPS.set_dry(True)** sets the flag on every workflow
- **Plan** a whole campaign before submitting anything
- **Per workflow** wf.set_dry(True) on one part plans only that part
- **Review** the launchers of all workflows together

> *One call*
>
> Lecture 22's campaign, planned.

```
campaign.set_dry(True)
```

## 25. Switching modes with a flag

```
import os
PORTABLE = os.environ.get("DAGON_PORTABLE") == "1"

wf = workflow("Campaign", base,
              portable_emulation=PORTABLE)
if os.environ.get("DAGON_DRY") == "1":
    wf.set_dry(True)

# DAGON_DRY=1 python campaign.py       plan
# DAGON_PORTABLE=1 python campaign.py  laptop
# python campaign.py                   cluster
```

- One script, three modes
- The variable names are your choice
- No code edits between stages

## 26. This lecture's example

- **2** - Workflows: one dry, one portable
- **0** - Commands run by the dry workflow
- **0** - Calls to sbatch by the portable one

## 27. Course examples and real deployments

**In this course**

- Portable emulation for SLURM in this lecture
- Mocks for Docker, Kubernetes, Slurm in Part 4
- Local services for web, LLM, FaaS
- Every output reproducible

**In a real deployment**

- portable_emulation=False
- Real schedulers, registries and services
- Credentials from the configuration
- Outputs depend on the platform

## 28. Exercise

A. Dry-run the station pipeline of lecture 12
B. List every launcher it wrote
C. Make all summaries SLURM tasks and run with emulation
D. Compare the report with lecture 12

**Deliverable:** The list of launchers and the emulated report, identical to the BATCH version.

## 29. Check your understanding

1. What does a dry run execute?
2. What does portable emulation do with a SLURM task?
3. Why is no file staged in portable mode?
4. Which errors does a dry run miss?

<details><summary>Answers</summary>

1. No command: launchers are written, nothing is run.
2. Runs its command locally with bash in its folder, ignoring the scheduler.
3. References are rewritten to the producers' own files, which are read in place.
4. Errors inside commands, wrong platform options, missing images, performance problems.

</details>

## 30. Key takeaways

1. set_dry(True) walks the graph and writes launchers only
2. portable_emulation=True runs every task locally with bash
3. Emulated references read producers' files in place
4. Dry, portable, small real, full: a safe path to production

*Next: a resumable ensemble*

---

Raffaele Montella. CC0 1.0. Generated from `src/lectures/23.js`.
