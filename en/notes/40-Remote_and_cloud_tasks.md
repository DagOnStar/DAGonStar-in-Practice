# 40. Remote and cloud tasks

*Running steps on other machines over SSH, safe remote commands, and provisioning cloud instances with an optional extra*

Workflows in Practice with DAGonStar - Part 4: Infrastructure, FAIR and applications. Slides: [40-DAGonStar-Remote_and_cloud_tasks.pptx](../lectures/40-DAGonStar-Remote_and_cloud_tasks.pptx). Examples: [examples/40-remote](../../examples/40-remote/).

## 2. Today's lecture

**Outline**

1. Why run a step elsewhere
2. Remote tasks over SSH
3. Quoting on the remote shell
4. Cloud tasks: instances on demand
5. Optional extras and lazy imports
6. Data between hosts

**After this lecture you can**

- Create a remote batch task
- Explain how remote commands are quoted
- Describe the life of a cloud instance

## 3. Remote execution

*The data or the hardware is on another machine: send the step there.*

## 4. Reasons to go remote

- **Data** - Observations stored on a lab server.
- **Hardware** - A GPU workstation or a login node.
- **Licences** - Software installed on one host only.
- **Elasticity** - A cloud VM for a peak of work.

> **Same task, another host** the launcher is the same; it is written and run over SSH.

## 5. Remote tasks

*Add ip, ssh_username and keypath: a BATCH task becomes a RemoteBatch.*

## 6. Three remote tasks

[`examples/40-remote/ssh_and_cloud.py`](../../examples/40-remote/ssh_and_cloud.py)

```python
default = Batch("collect", "hostname", ip="192.0.2.10",
                ssh_username="student", keypath="/tmp/key")
custom = RemoteTask("collect2", "hostname", ip="192.0.2.10",
                    ssh_username="student", keypath="/tmp/key", ssh_port=2200)
anonymous = RemoteTask("collect3", "hostname", ip="192.0.2.10", keypath="/tmp/key")
```

- Batch(..., ip=...) returns a RemoteBatch; ssh_port defaults to 22
- A RemoteTask with port 2200; SSHManager is mocked, so no connection is made

## 7. Arguments

| Argument | Meaning |
|---|---|
| `ip` | Host name or address |
| `ssh_username` | Remote user; without it no connection is opened |
| `keypath` | Private key file (made absolute) |
| `ssh_port` | Default 22 |
| `working_dir` | Remote folder; otherwise the scratch layout |
| `globusendpoint` | GridFTP endpoint for transfers |

## 8. Recorded output

Recorded output of `python examples/40-remote/ssh_and_cloud.py`:

```text
Batch(..., ip=...) builds RemoteBatch | ports: 22 2200
connections opened: 2 | without a username: None
quoted remote command: mkdir -p '/scratch/run dir; rm -rf ~/.dagon'
cloud task: CloudTask | node: None | ssh: None
without the extra: Cloud support requires the 'cloud' extra: python -m pip install 'dagonstar[cloud]'
```

- RemoteBatch; ports 22 and 2200
- Two connections, one task without
- Hostile path quoted
- CloudTask: nothing provisioned
- The cloud extra is missing

## 9. How a remote task runs

1. **Connect** - SSHManager with key.
2. **mkdir** - Remote scratch, quoted.
3. **Write** - Launcher over SSH.
4. **Run** - bash on the remote host.
5. **Collect** - mv to *-removed.

## 10. No username, no connection

- **Condition** ip and ssh_username both given
- **Otherwise** ssh_connection stays None
- **Use** build a task now, connect later (cloud tasks)
- **Recorded** without a username: None
- **Keys** keypath, never passwords

> *Recorded output*
>
> Three tasks, two connections.

```
connections opened: 2
without a username:
  None
```

## 11. Quoting

*Remote commands go through a shell: every path must be quoted.*

## 12. A hostile path

[`examples/40-remote/ssh_and_cloud.py`](../../examples/40-remote/ssh_and_cloud.py)

```python
sent = []
custom.workflow = SimpleNamespace(logger=SimpleNamespace(error=lambda *a: None))
custom.ssh_connection = SimpleNamespace(
    execute_command=lambda command: sent.append(command) or {"code": 0})
custom.working_dir = "/scratch/run dir; rm -rf ~"   # a hostile path
custom.mkdir_working_dir(custom.working_dir)
print("quoted remote command:", sent[0])
```

- The connection is replaced by a function that records commands
- The working directory contains ; rm -rf ~

## 13. Why it is safe

- **join_command** quotes every argument with shlex.quote
- **Result** mkdir -p '/scratch/run dir; rm -rf ~/.dagon'
- **The ;** is part of a file name, not a second command
- **Same rule** Docker, Slurm, staging, garbage collection
- **Lesson** never build shell commands by string concatenation

> *In mkdir_working_dir*
>
> Quoting is the default everywhere.

```
join_command(("mkdir",
 "-p", path))
```

## 14. Unquoted and quoted

**Unquoted**

- mkdir -p /scratch/run dir; rm -rf ~/.dagon
- Creates /scratch/run and ./dir
- Then deletes ~/.dagon
- A path became code

**Quoted**

- mkdir -p '/scratch/run dir; rm -rf ~/.dagon'
- Creates one oddly named folder
- Nothing else runs
- A path stays data

## 15. Remote garbage collection

- **on_garbage** mv the remote folder to *-removed
- **Checkpoint** updated with the new path
- **Nothing deleted** same policy as local tasks (lecture 14)
- **Quoted** mv with join_command
- **Clean up** periodically, after checking results

> *Over SSH*
>
> The same rule on every host.

```
mv dir dir-removed
```

## 16. Troubleshooting SSH

| Symptom | Likely cause |
|---|---|
| Permission denied (publickey) | Key not in authorized_keys, or wrong user |
| Connection refused | Wrong ssh_port, or sshd not running |
| Host key verification failed | Unknown host: connect once by hand |
| Cannot create scratch directory | Remote path not writable |
| Staging fails | No mover between the two hosts |

## 17. Cloud tasks

*A CLOUD task creates or finds an instance, then behaves like a remote task.*

## 18. A cloud task

[`examples/40-remote/ssh_and_cloud.py`](../../examples/40-remote/ssh_and_cloud.py)

```python
cloud = DagonTask(TaskType.CLOUD, "regional_model", "hostname", provider="dummy",
                  ssh_username="cloud-user", key_options={"key_path": "/tmp/key"},
                  instance_flavour={"image": "image-id", "size": "small"},
                  instance_name="dagon-course", stop_instance=True)
```

- provider: a libcloud provider; flavour: image and size; a name for the instance
- stop_instance: shut it down when no consumer needs it any more

## 19. Instance lifecycle

1. **Get** - Existing id, or create.
2. **Wait** - Until running.
3. **IP** - First public address.
4. **SSH** - Connect and run.
5. **Stop** - shutdown when unused.

## 20. Instance arguments

- **provider** a libcloud Provider: EC2, DigitalOcean, GCE...
- **instance_id** reuse a running instance
- **instance_flavour** image, size and provider options
- **key_options** how to create or import an SSH key pair
- **stop_instance** shutdown -h now when the reference count reaches 0

> *Pay only while needed*
>
> The reference count of lecture 14 decides when to stop.

## 21. Optional extras

*libcloud is not installed by default; the error says how to get it.*

## 22. Importing lazily

```
try:
    from dagon.cloud import CloudManager
except ImportError as exc:
    if exc.name and (exc.name == "libcloud"
                     or exc.name.startswith("libcloud.")):
        raise ImportError(
            "Cloud support requires the 'cloud' extra: "
            "python -m pip install 'dagonstar[cloud]'") from exc
    raise
```

- Imported only when run
- Clear install hint
- Other errors re-raised

## 23. The example's check

- **Simulate** builtins.__import__ refuses libcloud
- **Execute** the cloud task tries to import CloudManager
- **Result** the extra's install command, not a traceback
- **Before that** node is None: nothing provisioned
- **Portable mode** a cloud task runs locally instead

> *The fix*
>
> Printed by the error.

```
pip install
 'dagonstar[cloud]'
```

## 24. Data between hosts

*References to tasks on other hosts are staged by SCP, GridFTP or FTP.*

## 25. How data moves

| Producer and consumer | Mover |
|---|---|
| Same host | Workflow mover: COPY or LINK |
| Different hosts, GridFTP endpoint | GRIDFTP (Globus) |
| Different hosts, SSH | SCP |
| Different hosts, FTP server | FTP |

> **Lecture 44** the movers in detail and how to choose.

## 26. Run and try

**Steps**

1. Run the example
2. Change the hostile path to include $(whoami)
3. Read the quoted command: no substitution
4. Install dagonstar[cloud] in a virtualenv and run again

**Run it**

```bash
python examples/\
  40-remote/\
  ssh_and_cloud.py
```

**Watch for:** With libcloud installed the import succeeds, and the dummy provider would be used with real credentials only.

## 27. This lecture's example

- **3** - Remote tasks built
- **2** - SSH connections opened
- **0** - Instances provisioned

## 28. Exercise

A. If you have SSH access to a server, run fetch on it
B. Add a local consumer that counts the records
C. Check which mover staged the file
D. Otherwise, mock SSHManager and record the commands

**Deliverable:** The workflow, its output and the mover used (or the recorded commands).

## 29. Check your understanding

1. When does a remote task open an SSH connection?
2. How does DAGonStar keep a hostile path from running commands?
3. When is a cloud instance stopped?
4. What happens if libcloud is missing?

<details><summary>Answers</summary>

1. When both ip and ssh_username are given.
2. Every argument is quoted with join_command (shlex.quote).
3. When its reference count reaches 0 and stop_instance is True.
4. An ImportError tells you to install dagonstar[cloud].

</details>

## 30. Key takeaways

1. ip, ssh_username and keypath make a task remote
2. Every remote argument is quoted
3. Cloud tasks create, use and stop instances
4. Optional extras are imported lazily, with clear errors

*Next: Slurm*

---

Raffaele Montella. CC0 1.0. Generated from `src/lectures/40.js`.
