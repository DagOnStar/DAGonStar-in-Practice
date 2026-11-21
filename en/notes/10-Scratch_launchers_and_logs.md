# 10. Scratch, launchers and logs

*Opening a task folder: the generated launcher, the context script, staged inputs, stdout and the logger*

Workflows in Practice with DAGonStar - Part 1: Foundations of scientific workflows. Slides: [10-DAGonStar-Scratch_launchers_and_logs.pptx](../lectures/10-DAGonStar-Scratch_launchers_and_logs.pptx). Examples: [examples/10-scratch](../../examples/10-scratch/).

## 2. Today's lecture

**Outline**

1. The scratch tree of a run
2. The .dagon folder
3. The launcher, section by section
4. The context script
5. stdout, exit codes and the logger
6. Debugging a task by hand

**After this lecture you can**

- Find every file DAGonStar writes for a task
- Read a launcher and map it to the task's command
- Rerun a task by hand to debug it

## 3. The scratch tree

*Every task folder sits under scratch_dir_base; everything DAGonStar adds lives in its .dagon subfolder.*

## 4. inspect_scratch.py

[`examples/10-scratch/inspect_scratch.py`](../../examples/10-scratch/inspect_scratch.py)

```python
with scratch("10") as base:
    wf = workflow("Scratch10", base)
    fetch = DagonTask(TaskType.BATCH, "fetch",
                      fetch_observations() + " && echo copied 12 records")
    mean = DagonTask(TaskType.BATCH, "mean", station_mean(
        "NAP", "workflow:///fetch/outputs/observations.csv", "outputs/mean.txt"))
    wf.add_task(fetch)
    wf.add_task(mean)
    wf.run()
```

- fetch prints a line after copying: it goes to its stdout.txt
- mean reads fetch's output through a reference

## 5. The files of the consumer

Recorded output of `python examples/10-scratch/inspect_scratch.py`:

```text
files of the consumer task:
   .dagon/context.sh
   .dagon/inputs/Scratch10/fetch/outputs/observations.csv
   .dagon/launcher.sh
   .dagon/ssh_key
   .dagon/ssh_key.pub
   .dagon/stdout.txt
   outputs/mean.txt
```

- context.sh: machine discovery
- inputs/: staged files
- launcher.sh: what ran
- ssh_key pair: for remote movers
- stdout.txt: captured output

## 6. The .dagon folder

| File | Written by | Purpose |
|---|---|---|
| `launcher.sh` | the task | Stage inputs, run the command, report the code |
| `context.sh` | the task | Discover IP, user and services of the machine |
| `inputs/<wf>/<task>/...` | the stager | Copies or links of referenced files |
| `stdout.txt` | the launcher | Output of the command, through tee |
| `ssh_key, ssh_key.pub` | the task | Key pair for SCP/SFTP staging between hosts |

## 7. Folder names

- **Pattern** <timestamp>-<task name>
- **Timestamp** 13 digits: milliseconds since the epoch
- **Sorting** ls lists task folders in creation order
- **Uniqueness** two runs of the same workflow never share a folder
- **Course helper** where(task) strips the timestamp for stable output

> *A real folder name*
>
> Printed as <ts>-mean on the slides.

```
1794842707178-mean
```

## 8. The launcher

*A bash script generated for every task: read it once and debugging becomes easy.*

## 9. launcher.sh, abridged

```
#! /bin/bash
# This is the DagOn launcher script
code=0
# Change the current directory to the working directory
cd <scratch>/<ts>-mean
# Start staging in
# Create the destination directory
mkdir -p <task>/.dagon/inputs/Scratch10/fetch//outputs
# Add the copy command
#   src=<scratch>/<ts>-fetch//outputs/observations.csv
#   cmd="cp -r \"$file\" \"$dst\""   mode=0: sequential
# Wait for all sbatch jobs to complete
# Invoke the command
mkdir -p outputs && awk ... <task>/.dagon/inputs/... \
  > outputs/mean.txt | tee <task>/.dagon/stdout.txt
(exit "${PIPESTATUS[0]}")
# Perform post process
exit $code
```

- Each section starts with a comment
- Staging is part of the launcher
- The command is the rewritten one
- code collects any failure

## 10. The sections, read by the example

Recorded output of `python examples/10-scratch/inspect_scratch.py`:

```text
launcher steps: Change the current directory to the working directory | Start staging in | Create the destination directory | Add the copy command | Wait for all sbatch jobs to complete | Invoke the command | Perform post process
rewritten input: <task>/.dagon/inputs/Scratch10/fetch//outputs/observations.csv
```

- The comment lines, in order
- Wait for sbatch: used when staging in SLURM mode
- The rewritten input points into .dagon/inputs

## 11. Launcher sections

1. **cd** - Into the task's working directory.
2. **Stage in** - mkdir the destination, copy each input.
3. **Wait** - For staging jobs submitted to Slurm.
4. **Invoke** - The rewritten command, through tee.
5. **Post** - Exit with the collected code.

## 12. Exit codes

- **code=0** at the start of the launcher
- **After each step** if [ $? -ne 0 ]; then code=1; fi
- **PIPESTATUS[0]** the exit code of your command, not of tee
- **exit $code** non-zero if any step failed
- **Task** a non-zero exit makes the task FAILED

> *Why this line*
>
> Without it, tee would hide a failing command.

```
(exit "${PIPESTATUS[0]}")
```

## 13. Stager modes inside the launcher

- **mode=0 NORMAL** - eval the copy command for each input, in sequence.
- **mode=1 PARALLEL** - GNU parallel with -j jobs: the threads key of [batch].
- **mode=2 SLURM** - One sbatch job per copy, then wait with squeue.

> **Same script, three behaviours** the mode is written into the launcher by the stager.

## 14. The context script

*Before running, DAGonStar discovers what kind of machine the task is on.*

## 15. What context.sh discovers

- **Machine type** cluster node, cluster frontend or single machine
- **Addresses** public IP and private IP
- **Services** whether sshd, ftpd or a SkyCDS client are available
- **User** the account running the task
- **Why** remote movers need to know how to reach a task's folder

> *Network access*
>
> context.sh may query a public IP service; offline it falls back to local addresses.

## 16. Local and remote tasks

**Same machine**

- Producer and consumer folders are both local
- cp or ln is enough
- context mostly informative
- All course examples run like this

**Different machines**

- The consumer must reach the producer's host
- SCP, SFTP, HTTP or GridFTP
- context decides address and protocol
- Lecture 40 and 44

## 17. Output and logs

*Two channels: what the command prints, and what DAGonStar logs about the run.*

## 18. Reading stdout and the launcher

[`examples/10-scratch/inspect_scratch.py`](../../examples/10-scratch/inspect_scratch.py)

```python
print("stdout of the producer:",
      Path(fetch.working_dir, ".dagon", "stdout.txt").read_text().strip())
launcher = (folder / ".dagon" / "launcher.sh").read_text()
steps = [line[2:] for line in launcher.splitlines()
         if line.startswith("# ") and "DagOn" not in line]
print("launcher steps:", " | ".join(steps))
command = next(l for l in launcher.splitlines() if l.startswith("mkdir -p outputs && awk"))
staged = next(w for w in command.split() if w.endswith(".csv"))
print("rewritten input:", staged.replace(str(folder), "<task>"))
check("# Invoke the command" in launcher, "the launcher is kept for audit")
```

- stdout.txt of fetch contains the echo
- The launcher is read like any text file

## 19. Where messages go

| Channel | Contains | Where |
|---|---|---|
| stdout of the command | What your program prints | <task>/.dagon/stdout.txt |
| Files of the command | Your outputs | <task>/outputs/... |
| dagon logger | Status changes, errors, tracebacks | stderr, configured in dagon.ini |
| Events | Your own listeners (lecture 17) | Wherever you send them |

## 20. The logger

- **Name** dagon, from logging.getLogger
- **Levels** DEBUG shows every step; WARNING only problems
- **Configured** by fileConfig when config_file is used
- **Programmatic** logging.getLogger('dagon').setLevel(logging.DEBUG)
- **Examples** keep the default; failing examples silence it on purpose

> *See everything*
>
> Very verbose: one line per step of every task.

```
import logging
logging.basicConfig(
  level=logging.DEBUG)
```

## 21. Debugging by hand

*A failed task folder is a complete, reproducible environment: rerun the launcher yourself.*

## 22. Rerun a task

**Steps**

1. Keep the scratch: use a fixed folder instead of scratch()
2. Run the workflow, find the failed task folder
3. cd into it and read .dagon/launcher.sh
4. Run bash .dagon/launcher.sh and read the error
5. Fix the command in the workflow and rerun

**Run it**

```bash
cd <scratch>/<ts>-mean
bash .dagon/launcher.sh
echo $?
```

**Watch for:** The same output and exit code that DAGonStar saw, with nothing hidden.

## 23. Debugging checklist

| Question | Look at |
|---|---|
| Did the inputs arrive? | .dagon/inputs/ |
| What command ran? | the Invoke section of launcher.sh |
| What did it print? | .dagon/stdout.txt |
| What exit code? | bash launcher.sh; echo $? |
| What did DAGonStar say? | the dagon logger at DEBUG |

## 24. Keeping or removing scratch

- **Development** keep every folder: remove_dir False
- **Production** remove consumed folders: remove_dir True (lecture 14)
- **Disk** ensembles create many folders: plan the space
- **Privacy** scratch may hold copies of sensitive inputs
- **Course examples** scratch() deletes the temporary tree at the end

> **7** - *Files in this consumer's folder*
>
> One output and six written by DAGonStar.

## 25. Scratch and security

- **Private keys** - ssh_key is a private key: keep scratch readable only by you.
- **Copies of inputs** - Staged files duplicate data: mind licences and personal data.
- **Commands** - launcher.sh contains the full command: never put secrets in it.
- **Clean-up** - Remove scratch of sensitive runs as soon as results are stored.

## 26. One task, many files

- **1** - Output file written by your command
- **5** - Files in .dagon besides staged inputs
- **1** - Staged input for one reference

## 27. The audit check

[`examples/10-scratch/inspect_scratch.py`](../../examples/10-scratch/inspect_scratch.py)

```python
command = next(l for l in launcher.splitlines() if l.startswith("mkdir -p outputs && awk"))
staged = next(w for w in command.split() if w.endswith(".csv"))
print("rewritten input:", staged.replace(str(folder), "<task>"))
check("# Invoke the command" in launcher, "the launcher is kept for audit")
```

- The Invoke line is found in the launcher
- The staged CSV path is printed with <task> for the folder

## 28. Exercise

A. Run the example with a fixed scratch folder
B. Open both task folders and list their .dagon files
C. Break the awk command and rerun the launcher by hand
D. Find the error message and the exit code

**Deliverable:** A short report: the tree of the two folders and the exit code of the broken launcher.

## 29. Check your understanding

1. Where does the output of a task's command go?
2. Why does the launcher contain (exit "${PIPESTATUS[0]}")?
3. What does context.sh discover and why?
4. How do you reproduce a failed task exactly?

<details><summary>Answers</summary>

1. Into its files, and its standard output into .dagon/stdout.txt through tee.
2. So that the exit code is the command's, not tee's.
3. Machine type, IP addresses, available services and user, so that other tasks can reach its folder.
4. cd into its working directory and run bash .dagon/launcher.sh.

</details>

## 30. Key takeaways

1. Each task folder has a .dagon subfolder
2. launcher.sh stages inputs, runs the rewritten command, reports the code
3. context.sh discovers how to reach the machine
4. Rerun the launcher by hand to debug

*Next: serialising and inspecting workflows*

---

Raffaele Montella. CC0 1.0. Generated from `src/lectures/10.js`.
