# 05. Configuration

*dagon.ini sections, configuration dictionaries, the scratch base and logging, with the same workflow configured both ways*

DAGonStar in Practice - Part 1: Foundations of scientific workflows. Slides: [05-DAGonStar-Configuration.pptx](../lectures/05-DAGonStar-Configuration.pptx). Examples: [examples/05-configuration](../../examples/05-configuration/).

## 2. Today's lecture

**Outline**

1. Why configuration is separate from the graph
2. The dagon.ini file, section by section
3. Configuration as a dictionary
4. The scratch base and remove_dir
5. Logging
6. Running the same workflow both ways

**After this lecture you can**

- Write a minimal dagon.ini
- Build the same configuration as a Python dict
- Choose where task folders are created

## 3. Graph and configuration

*The graph says what to run. The configuration says where, with which credentials, and how much to keep.*

## 4. What goes where

**In the workflow code**

- Tasks and their commands
- Dependencies and references
- Task types
- Names used in URLs and checkpoints

**In the configuration**

- Scratch directory base
- Cluster partition, cloud keys, service URLs
- Clean-up policy, threads
- Logging levels and handlers

## 5. Why keep them apart

- **Portability** the same workflow runs on a laptop and on a cluster by changing the config
- **Secrets** keys and tokens stay out of the code and out of git
- **Sharing** colleagues use your workflow with their own paths
- **Testing** the examples point the scratch at a temporary directory

> **1** - *Workflow, many configs*
>
> Lecture 40 runs the same tasks over SSH by changing only the configuration.

## 6. dagon.ini

*An INI file read with configparser: sections in brackets, key = value lines.*

## 7. A minimal dagon.ini

[`examples/05-configuration/dagon.ini`](../../examples/05-configuration/dagon.ini)

```ini
; A minimal configuration for local workflows (lecture 05).
; scratch_dir_base is replaced by the example with a temporary directory.
[dagon_service]
use = False
route = http://localhost:57000

[ftp_pub]
ip = localhost

[batch]
scratch_dir_base = /tmp/
run_base =
remove_dir = False
threads = 2

[slurm]
partition =
```

- **dagon_service** optional REST service; off here
- **ftp_pub** address used to publish task folders
- **batch** scratch base, run base, clean-up, threads
- **slurm** default partition

## 8. The core sections

| Section | Key | Meaning |
|---|---|---|
| `batch` | `scratch_dir_base` | Where task folders are created |
| `batch` | `remove_dir` | Remove consumed folders (lecture 14) |
| `batch` | `threads` | Threads for parallel staging |
| `batch` | `run_base` | Prefix prepended to commands |
| `slurm` | `partition` | Default partition for SLURM tasks |
| `dagon_service` | `use, route` | Report status to a DAGon service |
| `ftp_pub` | `ip` | Host name published for HTTP/FTP movers |

## 9. Sections used later in the course

- **[llm] [faas] [web]** - Endpoints, models and limits of service tasks (lectures 25-30).
- **[iot] [agentic]** - Adapters, profiles and guardrails (lectures 31-35).
- **[docker] [kubernetes]** - Images, namespaces, clients (lectures 37-39).
- **[beeond] [prestage]** - HPC storage and staging policies (lectures 42-43).
- **[globus]** - Endpoints for GridFTP transfers (lecture 44).
- **[fair]** - Metadata profile of the products (lecture 45).

## 10. Logging sections

[`examples/05-configuration/dagon.ini`](../../examples/05-configuration/dagon.ini)

```ini
[loggers]
keys = root

[handlers]
keys = stream_handler

[formatters]
keys = formatter

[logger_root]
level = WARNING
handlers = stream_handler

[handler_stream_handler]
class = StreamHandler
level = WARNING
formatter = formatter
args = (sys.stderr,)

[formatter_formatter]
format = %(asctime)s %(name)-12s %(levelname)-8s %(message)s
```

- config_file triggers logging.config.fileConfig
- So the file needs loggers, handlers, formatters
- WARNING keeps the console quiet
- DEBUG shows every task step

## 11. A trap: fileConfig

- **Workflow(config_file=...)** also configures Python logging from the same file
- **Missing [loggers]** fileConfig raises KeyError: 'formatters'
- **Fix** include the three logging sections, as in this example
- **Dictionary configs** do not touch logging: your own setup is kept

> *The usual symptom*
>
> It means the logging sections are missing, not your workflow.

```
KeyError:
  'formatters'
```

## 12. Configuration as a dictionary

*The same sections and keys as nested Python dicts: no file, no logging side effect.*

## 13. config() in common/course.py

[`examples/common/course.py`](../../examples/common/course.py)

```python
def config(scratch, extra=None, remove_dir=False):
    """The configuration dictionary of a local workflow whose scratch is *scratch*."""
    value = {
        "batch": {"scratch_dir_base": str(scratch), "run_base": "", "threads": "2",
                  "remove_dir": str(remove_dir)},
        "dagon_service": {"use": "False"},
        "ftp_pub": {"ip": "localhost"},
        "slurm": {"partition": ""},
    }
    for section, options in (extra or {}).items():
        value.setdefault(section, {}).update(options)
    return value
```

- Values are strings, as configparser would return
- extra merges more sections, used in later lectures

## 14. When to use which

- **dagon.ini** a deployment: one file per machine, read by every workflow
- **dict** tests, notebooks, examples, generated configurations
- **Both** load the file, then override keys in Python
- **Never** commit real credentials in either form

> *Two keyword arguments*
>
> Use exactly one of them.

```
Workflow(name,
  config=dict)
Workflow(name,
  config_file=path)
```

## 15. Three layers of settings

- **Site** - dagon.ini of the machine: scratch, partitions, endpoints.
- **Workflow** - Dictionary or overrides chosen by the workflow author.
- **Task** - Keyword arguments of DagonTask: partition, image, timeout.

> **The most specific wins** a task argument overrides the section default for that task only.

## 16. The scratch base

*Every task folder is created under scratch_dir_base: choose it with care.*

## 17. Choosing scratch_dir_base

| Machine | Good choice | Avoid |
|---|---|---|
| Laptop | A temporary directory or ~/dagon-scratch | Your source tree |
| Workstation | A local SSD with space | A synced cloud folder |
| Cluster | The parallel scratch file system | $HOME, often small and slow |
| Course examples | tempfile.TemporaryDirectory | Fixed paths shared by runs |

## 18. get_scratch_dir_base and remove_dir

- **get_scratch_dir_base()** the base the workflow uses, from the config
- **Task folders** <base>/<timestamp>-<task>
- **get_remove_dir_op()** the remove_dir flag as a boolean
- **remove_dir True** consumed folders are renamed *-removed (lecture 14)
- **Default here** False: keep everything to inspect it

> **13** - *Digits of the timestamp*
>
> Milliseconds since the epoch: folders sort by creation time.

## 19. Hands-on: both ways

*Load the ini file, then build the dictionary, and run the same probe task with each.*

## 20. Two configurations, one probe

[`examples/05-configuration/configuration.py`](../../examples/05-configuration/configuration.py)

```python
with scratch("05") as base:
    ini = (HERE / "dagon.ini").read_text()
    ini = ini.replace("scratch_dir_base = /tmp/",
                      "scratch_dir_base = %s" % base.as_posix())
    (base / "dagon.ini").write_text(ini)

    from_file = Workflow("FromFile05", config_file=str(base / "dagon.ini"))
    sections = read_config(str(base / "dagon.ini"))
    print("sections:", ", ".join(s for s in sections if not s.startswith(
        ("logger", "handler", "formatter"))))
    print("batch:", dict(sections["batch"], scratch_dir_base="<scratch>"))
```

- The ini is copied and its scratch path replaced
- read_config parses the file into a dict
- Logging sections are filtered from the print
- scratch_dir_base hidden: it is a temp path

## 21. Running the probe

[`examples/05-configuration/configuration.py`](../../examples/05-configuration/configuration.py)

```python
from_dict = Workflow("FromDict05", config=config(base))
for wf in (from_file, from_dict):
    wf.add_task(DagonTask(TaskType.BATCH, "probe", "echo ok > ok.txt"))
    wf.run()
    task = wf.tasks[0]
    inside = Path(task.working_dir).parent == base
    print(wf.name, "| remove_dir:", wf.get_remove_dir_op(),
          "| task dir inside scratch:", inside)
    check(inside, "the scratch base decides where tasks run")
```

- Same task in both workflows
- The task folder must be inside the base
- check() makes it a test, not a print

## 22. Recorded output

Recorded output of `python examples/05-configuration/configuration.py`:

```text
sections: dagon_service, ftp_pub, batch, slurm
batch: {'scratch_dir_base': '<scratch>', 'run_base': '', 'remove_dir': 'False', 'threads': '2'}
FromFile05 | remove_dir: False | task dir inside scratch: True
FromDict05 | remove_dir: False | task dir inside scratch: True
```

- Four non-logging sections
- Values are strings
- Both workflows put the task inside the scratch
- remove_dir is False in both

## 23. Change the scratch

**Steps**

1. Copy dagon.ini to your home folder
2. Set scratch_dir_base to ~/dagon-scratch
3. Build a workflow with config_file pointing at it
4. Run the probe and list ~/dagon-scratch

**Run it**

```bash
python examples/\
  05-configuration/\
  configuration.py
```

**Watch for:** Both lines end with task dir inside scratch: True.

## 24. How a value reaches a task

1. **Source** - dagon.ini or the dict.
2. **Workflow** - Stores the sections.
3. **Task** - Reads its section when it runs.
4. **Launcher** - Paths and options are written into .dagon/.

## 25. Good habits

- **Commit a template** dagon.ini.example with placeholders, never the real file
- **Read secrets from the environment** or from a file outside the repository
- **Keep logging at WARNING** raise it to DEBUG only to debug
- **One scratch per experiment** so that runs never share folders
- **Document the sections** each lecture lists the keys it needs

> *Course convention*
>
> Examples use config(scratch, extra) so that no example needs a file.

## 26. Secrets: where they go

| Secret | Good place | Bad place |
|---|---|---|
| Cloud keys | Environment, or a file outside git | dagon.ini in the repository |
| Service tokens | A secret store, injected at run time | The command string of a task |
| SSH keys | ~/.ssh with mode 600 | The scratch folder |
| Course examples | Fake values marked not-a-secret | Real credentials of any kind |

## 27. This lecture's example

- **2** - Workflows, one per configuration style
- **4** - Configuration sections besides logging
- **0** - Files written outside the temporary scratch

## 28. Exercise

A. Set remove_dir = True in the copied ini and rerun
B. Print get_remove_dir_op() for both workflows
C. Add a [web] section with timeout = 5 via extra
D. Read it back from wf.cfg in Python

**Deliverable:** A modified configuration.py printing remove_dir True for the file and the timeout for the dict.

## 29. Check your understanding

1. Which key decides where task folders are created?
2. Why does a config_file need logging sections?
3. Why are the values in the dictionary strings?
4. Name two things that belong to the configuration and not to the workflow code.

<details><summary>Answers</summary>

1. scratch_dir_base in [batch].
2. Because Workflow calls logging.config.fileConfig on the same file.
3. Because they mimic what configparser returns from an INI file.
4. The scratch base, credentials, partitions, service URLs, clean-up policy, logging.

</details>

## 30. Key takeaways

1. Configuration says where and how; the graph says what
2. dagon.ini and dict carry the same sections
3. scratch_dir_base decides where task folders live
4. A config_file also configures logging

*Next: the first local task, line by line*

---

Raffaele Montella. CC0 1.0. Generated from `src/lectures/05.js`.
