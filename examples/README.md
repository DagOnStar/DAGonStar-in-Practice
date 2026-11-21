# Course examples

One folder per lecture. Each folder has a `README.md`, its scripts and their recorded output in
`output/`. The slides and the textbook include these files directly, so what they show is what the
code prints.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r examples/requirements.txt          # DAGonStar pinned to the tested commit
python tools/run_examples.py                      # run all, compare with output/*.txt
python examples/12-station-pipeline/station_pipeline.py
```

Every script runs in a fresh temporary scratch directory that it removes at the end, ends with its
own assertions, and needs no external service. Services that are not on a laptop are replaced by
mocks, local stand-ins or DAGonStar's portable emulation, and the output says so.

| Folder | Scripts |
|--------|---------|
| [`01-hello`](01-hello/) | `hello_workflow.py` |
| [`02-script-vs-dag`](02-script-vs-dag/) | `as_dag.py` |
| [`03-architecture`](03-architecture/) | `factory.py` |
| [`04-environment`](04-environment/) | `check_environment.py` |
| [`05-configuration`](05-configuration/) | `configuration.py` |
| [`06-first-task`](06-first-task/) | `first_task.py` |
| [`07-dag`](07-dag/) | `fan_out_fan_in.py` |
| [`08-dataflow`](08-dataflow/) | `workflow_references.py` |
| [`09-cycles`](09-cycles/) | `cycles.py` |
| [`10-scratch`](10-scratch/) | `inspect_scratch.py` |
| [`11-inspect`](11-inspect/) | `inspect_workflow.py` |
| [`12-station-pipeline`](12-station-pipeline/) | `station_pipeline.py` |
| [`13-staging`](13-staging/) | `staging_modes.py` |
| [`14-garbage`](14-garbage/) | `garbage_collection.py` |
| [`15-checkpoint`](15-checkpoint/) | `checkpoint_resume.py` |
| [`16-failures`](16-failures/) | `fail_and_resume.py` |
| [`17-async`](17-async/) | `async_events.py` |
| [`18-native`](18-native/) | `native_task.py` |
| [`19-native-bindings`](19-native-bindings/) | `native_bindings.py` |
| [`20-sweep`](20-sweep/) | `parameter_sweep.py` |
| [`21-ensemble`](21-ensemble/) | `ensemble.py` |
| [`22-meta`](22-meta/) | `meta_workflow.py` |
| [`23-dry-portable`](23-dry-portable/) | `dry_and_portable.py` |
| [`24-resumable-ensemble`](24-resumable-ensemble/) | `resumable_ensemble.py` |
| [`25-web-get`](25-web-get/) | `web_get.py` |
| [`26-web-upload`](26-web-upload/) | `web_upload.py` |
| [`27-llm`](27-llm/) | `llm_task.py` |
| [`28-llm-audit`](28-llm-audit/) | `llm_audit.py` |
| [`29-faas`](29-faas/) | `faas_mock.py` |
| [`30-faas-http`](30-faas-http/) | `faas_http.py` |
| [`31-iot-observe`](31-iot-observe/) | `iot_observe.py` |
| [`32-iot-actuate`](32-iot-actuate/) | `iot_actuate.py` |
| [`33-agentic-contract`](33-agentic-contract/) | `agentic_contract.py` |
| [`34-agentic-guardrails`](34-agentic-guardrails/) | `agentic_guardrails.py` |
| [`35-agentic-evaluation`](35-agentic-evaluation/) | `agentic_evaluation.py` |
| [`36-continuum`](36-continuum/) | `continuum.py` |
| [`37-docker`](37-docker/) | `docker_task.py` |
| [`38-apptainer`](38-apptainer/) | `apptainer_task.py` |
| [`39-orchestrators`](39-orchestrators/) | `kubernetes_nomad.py` |
| [`40-remote`](40-remote/) | `ssh_and_cloud.py` |
| [`41-slurm`](41-slurm/) | `slurm_tasks.py` |
| [`42-beeond`](42-beeond/) | `beeond.py` |
| [`43-prestage`](43-prestage/) | `prestage.py` |
| [`44-movers`](44-movers/) | `data_movers.py` |
| [`45-fair`](45-fair/) | `fair.py` |
| [`46-cwl`](46-cwl/) | `cwl_export.py` |
| [`47-operations`](47-operations/) | `operations.py` |
| [`48-capstone`](48-capstone/) | `capstone.py` |
| [`A1-dagonfs`](A1-dagonfs/) | `block_layout.py`, `dagonfs_workflow.py` |
| [`A2-volumes`](A2-volumes/) | `local_directory.py`, `volume_task.py` |
| [`A3-meta`](A3-meta/) | `meta_task.py` (engines in `engines/`) |
| [`A4-dagonweb`](A4-dagonweb/) | `dagonweb_document.py` |

Shared code:

- `common/course.py` - the scratch directory, the workflow factory, the dataset helpers and `check`;
- `common/agentic.py` - the agent profile and the quality-control contract of lectures 33-36 and 48;
- `common/services.py` - deterministic HTTP services on 127.0.0.1 for the web, LLM and FaaS lectures;
- `common/weather.py` - the Python functions that the native tasks import;
- `common/mock_scheduler.py` - a local stand-in for `sbatch` (lecture 43);
- `data/gulf_of_naples.csv` - twelve hourly observations from Naples, Capri and Ischia.
