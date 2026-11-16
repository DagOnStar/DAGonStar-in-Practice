# 47. Operating DAGonStar

*The DAGon service, JSON round trips, runner environments, platform helpers and packaged commands*

DAGonStar in Practice - Part 4: Infrastructure, FAIR and applications. Slides: [47-DAGonStar-Operating_DAGonStar.pptx](../lectures/47-DAGonStar-Operating_DAGonStar.pptx). Examples: [examples/47-operations](../../examples/47-operations/).

## 2. Today's lecture

**Outline**

1. From a script to an operated service
2. The DAGon service
3. Workflows as JSON documents
4. Runner environments
5. Platform helpers
6. Packaged commands and operations checklist

**After this lecture you can**

- Register workflows with a DAGon service
- Rebuild a workflow from its JSON
- Diagnose runner and shell problems

## 3. Operations

*A course script runs once; a production workflow runs every day, on several machines, for years.*

## 4. What operations need

- **Visibility** - Which workflows run, which tasks failed.
- **Portability** - Same workflow on laptops, servers, clusters.
- **Diagnostics** - Clear errors for missing tools and paths.
- **Upgrades** - Pinned versions; tested before switching.

## 5. The DAGon service

*An optional HTTP service that records workflows and task states, and resolves tasks across workflows.*

## 6. Service configuration

| Key in [dagon_service] | Meaning |
|---|---|
| `use` | True to register workflows; False (course default) |
| `route` | Base URL of the service |

> **Unavailable service** a workflow with use=True checks the route first; the course runs offline with use=False.

## 7. Registering a workflow

[`examples/47-operations/operations.py`](../../examples/47-operations/operations.py)

```python
service = config(base, {"dagon_service": {"use": "True",
                                          "route": "http://dagon-service.invalid"}})
with mock.patch("dagon.api.requests.head") as head, \
        mock.patch("dagon.api.requests.post", return_value=Created()) as post:
    registered = Workflow("Ops47", config=service)
    registered.add_task(DagonTask(TaskType.BATCH, "fetch", fetch_observations()))
print("service checked at:", head.call_args.args[0])
print("workflow id:", registered.workflow_id, "| calls:",
```

- requests.head and requests.post are mocked: the service answers id 7
- Creating the workflow and adding a task are two POST calls

## 8. Calls to the service

1. **HEAD** - route/check
2. **POST** - create workflow
3. **id** - 7 from the reply
4. **POST** - add_task/7
5. **Updates** - Task status

## 9. What the service gives

- **Registry** workflows and their tasks, by id
- **Status** updated as tasks run
- **Lookup** get_workflow_by_name, get_task
- **Cross-workflow** references to tasks of other workflows (lecture 08)
- **Without it** unknown tasks raise Dagon service is not available

> *Recorded output*
>
> Mocked replies, real client code.

```
workflow id: 7
| calls: create,
  add_task/7
```

## 10. Recorded output

Recorded output of `python examples/47-operations/operations.py`:

```text
service checked at: http://dagon-service.invalid/check
workflow id: 7 | calls: [['dagon-service.invalid', 'create'], ['add_task', '7']]
JSON round trip keeps the explicit edge: ['fetch']
runner PYTHONPATH keeps user entries first: True | package root appended: True
bash: /bin/bash | shell_path is a str: True
dagon-agent-runner --help: ok
```

- HEAD to /check
- Two POST calls
- Explicit edge kept
- PYTHONPATH order
- bash and the runner

## 11. Upgrading DAGonStar

| Step | Why |
|---|---|
| Read the changelog | Behaviour changes, new checks |
| Pin the new version in a test env | Keep production stable |
| Run all examples and your workflows | Catch regressions |
| Compare checkpoints and FAIR reports | Same results, same records |
| Switch production | Only after the comparison |

## 12. Service or offline

**With the service**

- Central registry of runs
- Cross-workflow lookups
- Status visible to others
- One more component to operate

**Offline (use=False)**

- No extra component
- References within a workflow or DAG_TPS
- Logs and checkpoints are the record
- The course default

## 13. JSON documents

*as_json and jsonload: save a workflow, rebuild it elsewhere.*

## 14. A round trip

[`examples/47-operations/operations.py`](../../examples/47-operations/operations.py)

```python
offline = Workflow("Ops47Offline", config=config(base))
fetch = DagonTask(TaskType.BATCH, "fetch", fetch_observations())
report = DagonTask(TaskType.BATCH, "report", "true")
offline.add_task(fetch)
offline.add_task(report)
report.add_dependency_to(fetch)
copy = Workflow("placeholder", config=config(base),
                jsonload=json.loads(json.dumps(offline.as_json())))
copy.make_dependencies()
print("JSON round trip keeps the explicit edge:", [t.name for t in copy.tasks[1].prevs])
```

- report depends on fetch only by an explicit edge (no reference)
- The rebuilt workflow keeps it: explicit_prevs travels in the JSON

## 15. Why round trips matter

- **Store** the workflow definition next to its results
- **Ship** a JSON document to another machine or service
- **Rebuild** Workflow(..., jsonload=document)
- **Edges** references are re-parsed; explicit edges come from explicit_prevs
- **Name** taken from the document, not the placeholder

> *Lecture 11*
>
> The same keys: name, id, host, tasks.

## 16. Runner environments

*Native, FaaS and agentic runners start python -m dagon.<runner> in a task folder.*

## 17. runner_environment

```
def runner_environment(extra=None, base=None):
    environment = dict(os.environ if base is None else base)
    entries = [e for e in environment.get("PYTHONPATH", "")
               .split(os.pathsep) if e]
    if PACKAGE_ROOT not in entries:
        entries.append(PACKAGE_ROOT)
    environment["PYTHONPATH"] = os.pathsep.join(entries)
    environment.update(dict(extra or {}))
    return environment
```

- Your entries first
- dagon's root appended
- Task variables last

## 18. Why append, not prepend

- **Problem** a source checkout run from a task folder: No module named 'dagon'
- **Fix** add the directory that holds the running dagon package
- **Append** your own PYTHONPATH entries are never shadowed
- **Installed** PACKAGE_ROOT is site-packages: harmless
- **Task variables** applied last

> *Recorded output*
>
> Order checked by the example.

```
user entries first: True
package root
 appended: True
```

## 19. Platform helpers

*Launchers need bash; paths must be strings the shell understands.*

## 20. Helpers

| Helper | Does |
|---|---|
| `bash_executable()` | DAGON_BASH if set, else a detected bash; clear error if none |
| `shell_path(p)` | A path as a string for shell commands |
| `join_command(args)` | Quote each argument for the shell |
| `quote(value)` | Quote one value |

## 21. Shells and systems

- **macOS** /bin/bash 3.2 works for launchers
- **Linux** /bin/bash
- **Windows** Git Bash or WSL; set DAGON_BASH if not found
- **No bash** an error names the problem before any task runs
- **Launchers** always bash, whatever your login shell

> *Recorded output*
>
> On the machine that recorded it.

```
bash: /bin/bash
```

## 22. Commands and checklists

*Installed with the package; checked with --help.*

## 23. Packaged commands

- **dagon-agent-runner** the agentic engine outside a workflow (used by CWL)
- **python -m dagon.native_runner** native tasks
- **python -m dagon.faas_runner** FaaS tasks, also from CWL
- **python -m dagon.iot.runner** IoT tasks
- **Check** each with --help after an upgrade

> *Recorded output*
>
> Found on PATH.

```
dagon-agent-runner
 --help: ok
```

## 24. An operations checklist

| Check | How |
|---|---|
| Version pinned | pip install dagonstar==<version> |
| Examples pass | python tools/run_examples.py |
| Scratch has space | df -h on scratch_dir_base |
| Old runs cleaned | Remove *-removed folders after checking |
| Secrets outside files | Only *_env names in dagon.ini |
| Service reachable | curl <route>/check, if used |

## 25. Logs and diagnosis

- **Workflow log** - Task start, end, staging, errors.
- **Task log** - .dagon/stdout.txt of each task.
- **Records** - native_result, faas_*, iot_*, evaluation.json.
- **Checkpoint** - Codes and folders of every task.

## 26. Run and inspect

**Steps**

1. Run the example
2. Set DAGON_BASH to a non-existent path and run again
3. Read the error
4. Print copy.as_json() and compare it with offline.as_json()

**Run it**

```bash
python examples/\
  47-operations/\
  operations.py
```

**Watch for:** An explicit DAGON_BASH is trusted as given: a wrong path fails when a launcher starts, with the path in the error.

## 27. This lecture's example

- **2** - Service calls
- **1** - Explicit edge kept
- **0** - Live services needed

## 28. Exercise

A. Save the station pipeline as JSON (lecture 11)
B. Rebuild it on another machine or in a new folder
C. Run it and compare checkpoints
D. Write a five-line operations checklist for your lab

**Deliverable:** The JSON, the comparison and the checklist.

## 29. Check your understanding

1. What does a workflow do first when the DAGon service is enabled?
2. How does a rebuilt workflow keep an explicit edge?
3. Why is the package root appended to PYTHONPATH?
4. How do you tell DAGonStar which bash to use?

<details><summary>Answers</summary>

1. It checks the service at route/check, then registers itself.
2. explicit_prevs is saved in as_json and restored by jsonload.
3. So runners find dagon from task folders without shadowing user entries.
4. Set the DAGON_BASH environment variable.

</details>

## 30. Key takeaways

1. The DAGon service registers workflows and tasks
2. JSON round trips keep references and explicit edges
3. Runners get a PYTHONPATH that finds dagon
4. Platform helpers and checklists make runs portable

*Next: the capstone*

---

Raffaele Montella. CC0 1.0. Generated from `src/lectures/47.js`.
