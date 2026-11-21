# 04. Installing and checking the environment

*A pinned, reproducible installation of DAGonStar and a script that proves it works*

DAGonStar in Practice - Part 1: Foundations of scientific workflows. Slides: [04-DAGonStar-Installing_and_checking_the_environment.pptx](../lectures/04-DAGonStar-Installing_and_checking_the_environment.pptx). Examples: [examples/04-environment](../../examples/04-environment/).

## 2. Today's lecture

**Outline**

1. What DAGonStar needs
2. Virtual environments
3. Pinning the version
4. Optional extras
5. The environment check
6. Troubleshooting

**After this lecture you can**

- Install DAGonStar in a fresh virtual environment
- Explain why the version is pinned to a commit
- Run and read the environment check

## 3. Requirements

*Python, a bash shell, and optional clients for the task types you actually use.*

## 4. What you need

| Component | Why | Check |
|---|---|---|
| Python 3.8+ | The API and the task threads | `python3 --version` |
| bash | Every launcher is a bash script | `bash --version` |
| git | Clone the course and DAGonStar | `git --version` |
| docker, kubernetes | Container task types (optional) | `pip show docker` |
| cwltool | Validate CWL exports (lecture 46) | `cwltool --version` |

> **Linux and macOS work out of the box** on Windows use WSL 2, where bash and POSIX paths are native.

## 5. Supported platforms

- **Laptop** - macOS or Linux; every example of the course runs here.
- **Workstation** - More cores: larger sweeps and ensembles.
- **Cluster login node** - Slurm tasks, BeeOND and pre-staging (lectures 41-43).
- **Container** - A Python image with the requirements file installed.

## 6. The course repository

| Folder | Contents |
|---|---|
| `examples/` | One folder per lecture: scripts, README, recorded output |
| `examples/common/` | Helpers, native functions, mock services |
| `examples/data/` | The Gulf of Naples observations |
| `en/lectures/` | The 48 decks and the appendix deck |
| `en/notes/` | Lecture notes generated from the same sources |
| `en/textbook/` | The textbook, LaTeX and PDF |
| `src/, tools/` | Deck generator; the example runner |

## 7. Virtual environments

*One environment per project: the versions you test with are the versions you run with.*

## 8. Why a virtual environment

- **Isolation** packages for this course do not clash with others
- **Reproducibility** requirements.txt recreates exactly the same set
- **No root** everything installs inside .venv in the repository
- **Disposable** delete .venv and recreate it in a minute
- **IDE** PyCharm or VS Code point their interpreter at .venv/bin/python

> *Two commands*
>
> The prompt shows (.venv) while it is active.

```
python3 -m venv .venv
. .venv/bin/activate
```

## 9. The pinned requirements

[`examples/requirements.txt`](../../examples/requirements.txt)

```text
# The virtual environment that runs every example of the course.
# DAGonStar is pinned to the commit the course was tested against (v3.0.0).
dagonstar[docker,kubernetes] @ git+https://github.com/DagOnStar/dagonstar@f62ceea7757ae313ce8d7fc6130896c9e7e83326
# Optional: validates the CWL export of lecture 46 and runs the CWL meta-task of Appendix A3.
cwltool==3.2.20260413085819
```

- dagonstar from git, pinned to a commit
- Extras docker and kubernetes for lectures 37-39
- cwltool pinned to the tested release
- pip install -r examples/requirements.txt

## 10. Pinning: commit or version

**dagonstar @ <commit>**

- Exactly the code the slides were tested with
- Immune to later pushes on a branch
- Works for unreleased fixes
- Explicit upgrade: change one hash

**dagonstar>=3.0**

- Picks up new releases automatically
- May change behaviour under your feet
- Outputs may differ from the slides
- Fine for your own projects later

## 11. Installing from a checkout

- **Clone** git clone https://github.com/DagOnStar/dagonstar
- **Editable** pip install -e ./dagonstar[docker,kubernetes]
- **Effect** changes to the checkout are seen without reinstalling
- **Use it** to read the code while you run the examples
- **Course default** the pinned git URL in requirements.txt

> *Same code, two ways*
>
> An editable checkout at the pinned commit gives the same outputs as the requirements file.

## 12. Optional extras

*Task types that talk to external systems need their client libraries.*

## 13. Extras and the task types that use them

| Package | Task types | Without it |
|---|---|---|
| `docker` | DOCKER | ImportError when the task is built |
| `kubernetes` | KUBERNETES | ImportError when the task is built |
| `libcloud` | CLOUD | Cloud tasks unavailable |
| `globus_sdk` | GRIDFTP mover | Globus transfers unavailable |
| `cwltool` | none: validation | saveAsCWL works, validation does not |

> **Lazy imports** a missing extra never breaks workflows that do not use it.

## 14. What runs without any service

- **Batch and native tasks** always local
- **Web, LLM, FaaS** against local mock servers in examples/common/services.py
- **IoT and agentic** with the built-in mock adapters
- **Docker, Kubernetes, Nomad** with mocked clients in the examples
- **Slurm** with a mock sbatch/squeue on the PATH
- **Portable emulation** every type, locally (lecture 23)

> **0** - *External services needed*
>
> That is what makes every output on the slides reproducible on your laptop.

## 15. Upgrading the pin

- **Edit** replace the commit hash in examples/requirements.txt
- **Reinstall** pip install -r examples/requirements.txt
- **Run** python tools/run_examples.py
- **Read the diffs** each changed output names a lecture to revise
- **Record** python tools/run_examples.py --record once the slides are updated

> *Outputs are a contract*
>
> A new DAGonStar version is accepted only when every recorded output is explained.

## 16. The environment check

*A script that fails loudly if the installation is not usable.*

## 17. check_environment.py

[`examples/04-environment/check_environment.py`](../../examples/04-environment/check_environment.py)

```python
try:
    installed = version("dagonstar")
except PackageNotFoundError:
    installed = "not installed (checkout on sys.path)"

print("Python", platform.python_version(), "on", platform.system())
print("dagonstar", installed, "from", Path(dagon.__file__).parent.name)
print("bash:", bash_executable())
print("task types:", len(TaskType))
OPTIONAL = ("docker", "kubernetes", "libcloud", "globus_sdk", "cwltool")
for name in OPTIONAL:
    found = importlib.util.find_spec(name) is not None
    print("  optional %-11s %s" % (name, "present" if found else "absent"))
check(sys.version_info >= (3, 8), "DAGonStar needs Python 3.8 or later")
check(Path(bash_executable()).exists(), "a bash shell runs the launchers")
```

- Reads the installed version
- bash_executable: the shell launchers use
- len(TaskType): the registry loaded
- find_spec: is an extra importable?

## 18. The recorded check

Recorded output of `python examples/04-environment/check_environment.py`:

```text
Python 3.12.10 on Darwin
dagonstar 3.0.0 from dagon
bash: /bin/bash
task types: 16
  optional docker      present
  optional kubernetes  present
  optional libcloud    present
  optional globus_sdk  present
  optional cwltool     present
```

- Your Python version may differ
- dagonstar must be 3.0.0
- task types: 16
- Absent extras are fine unless you need them

## 19. bash_executable()

- **Purpose** find the bash that runs .dagon/launcher.sh
- **Unix** usually /bin/bash
- **Windows** WSL or Git Bash, found by dagon.platform_support
- **Fails** if no bash exists: no BATCH task can run
- **Why it matters** launchers use bash features such as set -o pipefail

> *One line of the check*
>
> The second check() asserts the file exists.

```
bash: /bin/bash
```

## 20. Run the check

**Steps**

1. Activate the virtual environment
2. Run the check from the repository root
3. Compare with the recorded output
4. Run the whole test suite of the course

**Run it**

```bash
python examples/\
  04-environment/\
  check_environment.py
python tools/\
  run_examples.py
```

**Watch for:** run_examples prints one line per example and a final count: 0 failed.

## 21. The course test runner

[`examples/../tools/run_examples.py`](../../examples/../tools/run_examples.py)

```python
done = subprocess.run([sys.executable, str(script)], cwd=str(ROOT), env=env,
                      capture_output=True, text=True, timeout=600)
took = time.monotonic() - started
name = "%s/%s" % (folder.name, script.name)
expected = folder / "output" / (script.stem + ".txt")
if done.returncode:
    failed.append(name)
    print("FAIL %-50s %5.1fs\n%s" % (name, took, done.stderr[-2000:]))
    continue
if record:
    expected.parent.mkdir(exist_ok=True)
    expected.write_text(done.stdout)
    write_readme(folder)
    status = "rec "
elif not expected.is_file() or expected.read_text() != done.stdout:
    changed.append(name)
    status = "diff"
```

## 22. Troubleshooting

*Most installation problems are the wrong interpreter or a missing extra.*

## 23. Common problems

| Symptom | Likely cause | Fix |
|---|---|---|
| ModuleNotFoundError: dagon | Wrong interpreter | Activate .venv, check which python |
| ImportError: docker | Extra missing | pip install docker |
| Version is not 3.0.0 | Old install shadows the pin | pip install --force-reinstall -r ... |
| bash not found | Native Windows Python | Use WSL 2 |
| Permission denied in /tmp | Scratch on a read-only disk | Set scratch_dir_base (lecture 05) |

## 24. Where to look

- **pip show dagonstar** version and location
- **python -c 'import dagon; print(dagon.__file__)'** which copy is imported
- **which python** the interpreter on the PATH
- **dagon logger** warnings go to stderr; set the level in dagon.ini
- **The examples** the output files are the reference

> *Rule*
>
> Always compare with a recorded output before changing code.

## 25. From zero to a working setup

1. **Clone** - Get the course repository.
2. **Venv** - Create and activate .venv.
3. **Install** - pip install the pinned requirements.
4. **Check** - Run the environment check.
5. **Test** - Run every example and compare.

## 26. What the test runner verifies

- **50** - Example scripts, all lectures plus the appendix
- **0** - Expected differences from the recorded outputs
- **1** - Command to run them all

> **Run it after any change** a different line in any output shows exactly which lecture is affected.

## 27. A reproducibility checklist

- **Pinned code** - dagonstar and cwltool at fixed versions.
- **Versioned data** - The dataset lives in the repository.
- **No hidden state** - Each run uses a fresh temporary scratch.
- **Recorded results** - Outputs in git; differences are reviewed.

## 28. Exercise

A. Create a fresh .venv and install the requirements
B. Run check_environment.py and save its output
C. Uninstall cwltool and run the check again
D. Run tools/run_examples.py 01 02 03 04

**Deliverable:** The two outputs of the check, before and after removing cwltool, and the runner summary.

## 29. Check your understanding

1. Why is dagonstar pinned to a commit instead of a version range?
2. Which task types need an optional extra?
3. What does bash_executable() return and why is it needed?
4. What does tools/run_examples.py compare?

<details><summary>Answers</summary>

1. So that the code is exactly the one the slides and outputs were tested with.
2. DOCKER (docker), KUBERNETES (kubernetes), CLOUD (libcloud); the GRIDFTP mover needs globus_sdk.
3. The path of the bash shell that runs every task launcher.
4. The standard output of each example with the recorded output/<script>.txt.

</details>

## 30. Key takeaways

1. One virtual environment per project
2. DAGonStar pinned to the tested commit
3. Extras only for the task types you use
4. check_environment.py and run_examples.py prove the setup

*Next: configuration with dagon.ini and dictionaries*

---

Raffaele Montella. CC0 1.0. Generated from `src/lectures/04.js`.
