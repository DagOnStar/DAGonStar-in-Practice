# Lecture notes

One Markdown file per lecture, slide by slide, generated from the same sources as the decks in `../lectures`.
Code excerpts are read from `examples/`; outputs are those recorded by `tools/run_examples.py --record`.

| # | Lecture | Part |
|---|---------|------|
| 01 | [Scientific workflows for AI–HPC](01-Scientific_workflows_for_AI_HPC.md) | 1 |
| 02 | [From scripts to workflows](02-From_scripts_to_workflows.md) | 1 |
| 03 | [DAGonStar architecture](03-DAGonStar_architecture.md) | 1 |
| 04 | [Installing and checking the environment](04-Installing_and_checking_the_environment.md) | 1 |
| 05 | [Configuration](05-Configuration.md) | 1 |
| 06 | [The first local task](06-The_first_local_task.md) | 1 |
| 07 | [Control dependencies](07-Control_dependencies.md) | 1 |
| 08 | [Data dependencies with workflow://](08-Data_dependencies_with_workflow.md) | 1 |
| 09 | [Validating graphs and cycles](09-Validating_graphs_and_cycles.md) | 1 |
| 10 | [Scratch, launchers and logs](10-Scratch_launchers_and_logs.md) | 1 |
| 11 | [Serialising and inspecting workflows](11-Serialising_and_inspecting_workflows.md) | 1 |
| 12 | [The station pipeline](12-The_station_pipeline.md) | 1 |
| 13 | [Staging modes](13-Staging_modes.md) | 2 |
| 14 | [Garbage collection](14-Garbage_collection.md) | 2 |
| 15 | [Checkpointing](15-Checkpointing.md) | 2 |
| 16 | [Failures](16-Failures.md) | 2 |
| 17 | [Asynchronous runs and events](17-Asynchronous_runs_and_events.md) | 2 |
| 18 | [Native tasks](18-Native_tasks.md) | 2 |
| 19 | [Native bindings](19-Native_bindings.md) | 2 |
| 20 | [Parameter sweeps](20-Parameter_sweeps.md) | 2 |
| 21 | [Ensembles](21-Ensembles.md) | 2 |
| 22 | [Meta-workflows](22-Meta_workflows.md) | 2 |
| 23 | [Dry runs and portable emulation](23-Dry_runs_and_portable_emulation.md) | 2 |
| 24 | [A resumable ensemble](24-A_resumable_ensemble.md) | 2 |
| 25 | [Web tasks](25-Web_tasks.md) | 3 |
| 26 | [Uploads, authentication and failures](26-Uploads_authentication_and_failures.md) | 3 |
| 27 | [LLM tasks](27-LLM_tasks.md) | 3 |
| 28 | [Responsible LLM tasks](28-Responsible_LLM_tasks.md) | 3 |
| 29 | [FaaS tasks](29-FaaS_tasks.md) | 3 |
| 30 | [FaaS over HTTP](30-FaaS_over_HTTP.md) | 3 |
| 31 | [IoT observation tasks](31-IoT_observation_tasks.md) | 3 |
| 32 | [IoT configuration and actuation](32-IoT_configuration_and_actuation.md) | 3 |
| 33 | [The agentic task contract](33-The_agentic_task_contract.md) | 3 |
| 34 | [Agentic tools and guardrails](34-Agentic_tools_and_guardrails.md) | 3 |
| 35 | [Agentic evaluation and checkpoints](35-Agentic_evaluation_and_checkpoints.md) | 3 |
| 36 | [One graph across the continuum](36-One_graph_across_the_continuum.md) | 3 |
| 37 | [Docker tasks](37-Docker_tasks.md) | 4 |
| 38 | [Apptainer tasks](38-Apptainer_tasks.md) | 4 |
| 39 | [Kubernetes and Nomad](39-Kubernetes_and_Nomad.md) | 4 |
| 40 | [Remote and cloud tasks](40-Remote_and_cloud_tasks.md) | 4 |
| 41 | [Slurm tasks](41-Slurm_tasks.md) | 4 |
| 42 | [BeeOND job-local storage](42-BeeOND_job_local_storage.md) | 4 |
| 43 | [Pre-staging scheduler inputs](43-Pre_staging_scheduler_inputs.md) | 4 |
| 44 | [Data movers](44-Data_movers.md) | 4 |
| 45 | [FAIR workflows](45-FAIR_workflows.md) | 4 |
| 46 | [Exporting to CWL](46-Exporting_to_CWL.md) | 4 |
| 47 | [Operating DAGonStar](47-Operating_DAGonStar.md) | 4 |
| 48 | [Capstone](48-Capstone.md) | 4 |
| A1 | [DAGonFS](A1-DAGonFS.md) | A |

Regenerate with `cd src && node notes.js`.
