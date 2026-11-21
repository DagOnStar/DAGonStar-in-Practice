# DAGonStar in Practice

Orchestrating AI-HPC workflows for computational environmental science: a course of 48 one-hour
lectures, plus four appendix lectures: DAGonFS, ad-hoc volumes and streams, meta-tasks, and DAGonWeb. Each lecture has a PowerPoint deck of exactly
30 slides. Theory and hands-on work are not split into separate lessons: every lecture introduces a
concept and runs it at once. The material is aligned with
[DAGonStar](https://github.com/DagOnStar/dagonstar) 3.0.0,
[DAGonFS](https://github.com/DagOnStar/DAGonFS) and [DAGonWeb](https://github.com/DagOnStar/DAGonWeb).

Participants are expected to program in Python and to use a terminal. Basic knowledge of SSH and of
an HPC scheduler helps in Part IV, but every example also runs on a laptop.

| # | Lecture | Example |
|---|---------|---------|
| | **Part I - Foundations** | |
| 01 | Scientific workflows for AI-HPC | `01-hello` |
| 02 | From scripts to workflows | `02-script-vs-dag` |
| 03 | DAGonStar architecture | `03-architecture` |
| 04 | Installing and checking the environment | `04-environment` |
| 05 | Configuration | `05-configuration` |
| 06 | The first local task | `06-first-task` |
| 07 | Control dependencies | `07-dag` |
| 08 | Data dependencies with `workflow://` | `08-dataflow` |
| 09 | Validating graphs and cycles | `09-cycles` |
| 10 | Scratch, launchers and logs | `10-scratch` |
| 11 | Serialising and inspecting workflows | `11-inspect` |
| 12 | The station pipeline | `12-station-pipeline` |
| | **Part II - Execution, data and recovery** | |
| 13 | Staging modes | `13-staging` |
| 14 | Garbage collection | `14-garbage` |
| 15 | Checkpointing | `15-checkpoint` |
| 16 | Failures | `16-failures` |
| 17 | Asynchronous runs and events | `17-async` |
| 18 | Native tasks | `18-native` |
| 19 | Native bindings | `19-native-bindings` |
| 20 | Parameter sweeps | `20-sweep` |
| 21 | Ensembles | `21-ensemble` |
| 22 | Meta-workflows | `22-meta` |
| 23 | Dry runs and portable emulation | `23-dry-portable` |
| 24 | A resumable ensemble | `24-resumable-ensemble` |
| | **Part III - Task models for AI-HPC** | |
| 25 | Web tasks | `25-web-get` |
| 26 | Uploads, authentication and failures | `26-web-upload` |
| 27 | LLM tasks | `27-llm` |
| 28 | Responsible LLM tasks | `28-llm-audit` |
| 29 | FaaS tasks | `29-faas` |
| 30 | FaaS over HTTP | `30-faas-http` |
| 31 | IoT observation tasks | `31-iot-observe` |
| 32 | IoT configuration and actuation | `32-iot-actuate` |
| 33 | The agentic task contract | `33-agentic-contract` |
| 34 | Agentic tools and guardrails | `34-agentic-guardrails` |
| 35 | Agentic evaluation and checkpoints | `35-agentic-evaluation` |
| 36 | One graph across the continuum | `36-continuum` |
| | **Part IV - Infrastructure, data and FAIR** | |
| 37 | Docker tasks | `37-docker` |
| 38 | Apptainer tasks | `38-apptainer` |
| 39 | Kubernetes and Nomad | `39-orchestrators` |
| 40 | Remote and cloud tasks | `40-remote` |
| 41 | Slurm tasks | `41-slurm` |
| 42 | BeeOND job-local storage | `42-beeond` |
| 43 | Pre-staging scheduler inputs | `43-prestage` |
| 44 | Data movers | `44-movers` |
| 45 | FAIR workflows | `45-fair` |
| 46 | Exporting to CWL | `46-cwl` |
| 47 | Operating DAGonStar | `47-operations` |
| 48 | Capstone | `48-capstone` |
| | **Appendix** | |
| A1 | DAGonFS | `A1-dagonfs` |
| A2 | Ad-hoc volumes and streams | `A2-volumes` |
| A3 | Meta-tasks | `A3-meta` |
| A4 | DAGonWeb | `A4-dagonweb` |

## Folders

| Folder | Content |
|--------|---------|
| [`en/lectures/`](en/lectures/) | the 48 lecture decks and the appendix decks `A1`-`A4` (`.pptx`, 16:9, 30 slides each, editable text, speaker notes) |
| [`en/notes/`](en/notes/) | the notes of each lecture, slide by slide, in Markdown |
| [`en/textbook/`](en/textbook/) | the companion textbook in LaTeX: four parts that follow the lectures, appendices A-H (E DAGonFS, F ad-hoc volumes, G meta-tasks, H DAGonWeb); every course example and its recorded output are included from `examples/`; `main.pdf` is the latest build |
| [`examples/`](examples/) | one folder per lecture, each with a `README.md`, the scripts and their recorded output in `output/`; `common/` holds the shared helpers and `data/` the Gulf of Naples dataset |
| [`tools/`](tools/) | `run_examples.py`, which runs every example and compares it with its recorded output; `export_decks_powerpoint.sh`, which exports decks to PDF with PowerPoint (macOS) |
| [`src/`](src/) | the generator of the decks and the notes |
| [`AGENTS.md`](AGENTS.md) | the rules for changing the material |

A single running case, hourly observations from three stations of the Gulf of Naples (Naples `NAP`,
Capri `CAP`, Ischia `ISC`), runs through the whole course: a script, a DAG, a station pipeline,
sweeps and ensembles, web, LLM, FaaS and IoT tasks, an agentic quality check, Slurm, BeeOND and
DAGonFS scratch spaces, ad-hoc volumes, meta-tasks running other engines' workflows, a FAIR bundle,
a CWL export and a DAGonWeb workflow document.

## Running the examples

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r examples/requirements.txt
python tools/run_examples.py            # all examples, compared with the recorded outputs
python tools/run_examples.py 07 21      # only lectures 07 and 21
python examples/12-station-pipeline/station_pipeline.py
```

Every example runs in a temporary scratch directory, ends with its own assertions and needs no
external service: Docker, Slurm, Kubernetes, Nomad, SSH hosts, clouds and live LLM, FaaS and IoT
providers are replaced by mocks, local stand-ins or DAGonStar's portable emulation, and the output
says so. `DAGON_LIVE_DOCKER=1` also runs the Docker example against a real daemon. On a Linux node
with MPI, FUSE 3 and a DAGonFS build, `DAGONFS_PYTHON=/path/to/DAGonFS/python` and
`DAGONFS=/path/to/dagonfs` make `A1-dagonfs/dagonfs_workflow.py` run on a real DAGonFS volume (the recorded output was made
with `DAGONFS_PYTHON` set on a host without DAGonFS, so it shows the launch command it would use).
`A3-meta/meta_task.py` runs its CWL step only when `cwltool` is on `PATH`.

## Rebuilding

```bash
cd src
npm install
node count.js                  # every deck has exactly 30 slides
node build.js                  # decks -> en/lectures (`node build.js 7 12 A4` for some)
node notes.js                  # notes -> en/notes
```

On macOS, `tools/export_decks_powerpoint.sh A2 A4` exports decks to PDF with Microsoft PowerPoint,
to see how the slides really render.

```bash
cd en/textbook && latexmk -pdf main.tex
```

The content of each deck is in `src/lectures/NN.js` (the cover plus 29 entries); theme, layouts and
slide kinds are in `src/lib.js`. `<code/>` slides read their excerpts from the files in `examples/`,
and `<result/>` slides show the recorded outputs, so slides and code cannot drift apart.

## Licence

[CC0 1.0 Universal](LICENSE).
