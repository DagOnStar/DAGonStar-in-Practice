# DAGonStar video series: build prompt

This file is a prompt. A person can follow it step by step, and Claude Code can execute it as it is
("Build video 03 as described in `media/videos_description.md`"). It describes fourteen short videos
about DAGonStar, how to capture their pictures, how to write and voice their narration, and how to
assemble and check them. The finished files go in `media/videos/`.

The rules of [`AGENTS.md`](../AGENTS.md) apply to the videos as they apply to slides and book:
the code is the reference, nothing is shown that does not run, and every number on screen can be
checked by hand.

---

## 1. Deliverables

| # | File in `media/videos/` | Main sources in this repository |
|---|-------------------------|---------------------------------|
| 00 | `00-dagonstar-introducing_dagonstar-motivation_contextualization_institutions_authors_contributors_repository_applications_publications.mp4` | `README.md`, `en/textbook/front/bibliography.tex`, `en/textbook/front/preface.tex`, deck `01`, GitHub repositories |
| 01 | `01-dagonstar-a_workflow_primer_with_dagonstar-introducing_the_eScience.mp4` | decks `01`, `02`; `ch01_introduction.tex`; `examples/01-hello`, `examples/02-script-vs-dag` |
| 02 | `02-dagonstar-introducing_dagonstar-the_workflow_schema.mp4` | deck `08`; `ch04_workflow_schema.tex`; `examples/08-dataflow` |
| 03 | `03-dagonstar-task_types_and_examples-part_1.mp4` | decks `06`, `18`, `37`, `38`, `39`, `40`, `41`; `examples/06-first-task`, `18-native`, `37-docker`, `38-apptainer`, `41-slurm` |
| 04 | `04-dagonstar-task_types_and_examples-part_2.mp4` | decks `25`, `27`, `29`, `31`, `33`, `36`; `examples/25-web-get`, `27-llm`, `29-faas`, `31-iot-observe`, `33-agentic-contract` |
| 05 | `05-dagonstar-advanced_features-the_ad_hoc_file_systems.mp4` | decks `A2`, `42`, `43`; `appF_volumes.tex`; `examples/A2-volumes`, `42-beeond` |
| 06 | `06-dagonstar-advanced_features-the_meta_task_type.mp4` | deck `A3` (and `22` for contrast); `appG_meta_tasks.tex`; `examples/A3-meta` |
| 07 | `07-dagonstar-dagonfs-the_ad_hoc_file_system_for_dagonstar.mp4` | deck `A1`; `appE_dagonfs.tex`; `examples/A1-dagonfs`; <https://github.com/DagOnStar/DAGonFS> |
| 08 | `08-dagonstar-dagonweb-the_user_friendly_interface_as_computational_science_and_data_gateway.mp4` | deck `A4`; `appH_dagonweb.tex`; `examples/A4-dagonweb`; <https://github.com/DagOnStar/DAGonWeb> |
| 09 | `09-dagonstar-dagonservice-tracking_dagonstar_workflows_in_production_environments.mp4` | <https://github.com/DagOnStar/DagOnService>; `dagon/api/` in the pinned DAGonStar source; `[dagon_service]` in `ch05_configuration.tex` and `ch02_architecture.tex`; decks `17`, `47` |
| 10 | `10-dagonstar-administrating_dagonstar.mp4` | decks `10`, `14`, `15`, `16`, `47`; `examples/10-scratch`, `14-garbage`, `15-checkpoint`, `16-failures`, `47-operations` |
| 11 | `11-dagonstar-installation.mp4` | deck `04`; `ch03_getting_started.tex`; `examples/04-environment`; `examples/requirements.txt` |
| 12 | `12-dagonstar-configuration.mp4` | deck `05`; `ch05_configuration.tex`, `appC_configuration_reference.tex`; `examples/05-configuration` |
| 13 | `13-dagonstar-wrapping_up_an_outlook_to_eScience.mp4` | decks `45`, `46`, `48`; `ch17_synthesis.tex`; `examples/45-fair`, `46-cwl`, `48-capstone` |

Use these file names exactly. If a name changes, rename every link to it as well.

## 2. Technical specification (all videos)

| Property | Value |
|----------|-------|
| Duration | 3:00, accepted range 2:50-3:10 |
| Container / video | MP4, H.264 (`libx264`, `yuv420p`, CRF 20, preset `slow`), 1920x1080, 30 fps, `+faststart` |
| Audio | AAC 192 kb/s, 48 kHz, stereo; integrated loudness -16 LUFS, true peak -1.5 dBTP |
| Language | English only, voice and on-screen text |
| Voices | two text-to-speech voices, one male and one female, alternating by section (section 5) |
| Subtitles | a matching `.srt` next to each `.mp4` (same base name), built from the narration |
| Pictures | real screenshots only (section 4): no AI-generated images, no mock-ups of UIs or terminals |
| Structure | 5 s title card, body sections, 10 s closing card |
| Licence | CC0 1.0, like the rest of the course; say so on the closing card |

Narration speed is about 145 words per minute, so each script has **400-440 words** in total.

## 3. Working layout

```
media/
├── videos_description.md        # this file
├── videos/                      # final .mp4 and .srt files (deliverables)
└── build/                       # working files, ignored by git (.gitignore)
    └── NN/
        ├── script.md            # narration, section by section, with voice and shots
        ├── shots/               # captured PNGs, 1920x1080, named NN-SS-description.png
        ├── terminal/            # .cast or .txt captures of example runs
        ├── audio/               # one .wav per section, then narration.wav
        ├── segments.txt         # ffmpeg concat list
        └── NN.srt
```

`.gitignore` excludes `*.mp4` and `media/build/`, so videos never enter the repository. Publish the
finished `.mp4` files as assets of a GitHub release (or on a video platform) and link them from there;
the `.srt` files and this description are the parts kept in git.

## 4. Capturing real screenshots

Every picture comes from something that actually runs or exists. Allowed sources:

1. **Slides.** Build the decks (`cd src && node build.js`), export them with PowerPoint
   (`tools/export_decks_powerpoint.sh 08 A4`), then rasterise the PDF at full HD:
   ```bash
   pdftoppm -r 144 -scale-to-x 1920 -scale-to-y 1080 -png <deck>.pdf media/build/NN/shots/NN-slide
   ```
2. **Running examples.** Run the example in a real terminal and capture it. Use a clean prompt, a
   dark theme, a font of at least 20 pt, and a window sized to 1920x1080:
   ```bash
   source .venv/bin/activate
   python examples/08-dataflow/workflow_references.py
   screencapture -x -o -l "$(osascript -e 'tell app "Terminal" to id of window 1')" media/build/02/shots/02-03-run.png
   ```
   For a moving terminal, record with `asciinema rec media/build/NN/terminal/run.cast` and render
   with `agg`, or record the window with
   `ffmpeg -f avfoundation -capture_cursor 1 -framerate 30 -i "<screen index>:none" ...`.
   The output on screen must match `examples/NN-*/output/*.txt`; if it does not, stop and run
   `python tools/run_examples.py NN` first.
3. **Source code.** Open the example file in an editor (VS Code, light or dark, font 20 pt, minimap
   off) and capture the lines the narration talks about. Show the file name in the tab.
4. **Web pages.** Capture GitHub pages (repositories, contributors, README, `docs/`) and DAGonWeb
   pages with a browser at 1920x1080, signed out, cookie banners declined, for example:
   ```bash
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
     --window-size=1920,1080 --hide-scrollbars --screenshot=media/build/00/shots/00-04-repo.png \
     https://github.com/DagOnStar/dagonstar
   ```
   Claude Code may use its built-in browser pane instead. Never capture a page that shows a
   personal account, a token, an e-mail address or private data.
5. **The textbook.** Rasterise pages of `en/textbook/main.pdf` with `pdftoppm` as for slides.

Each shot stays on screen for 4-12 s. Use slow pans or zooms (`zoompan`, at most 1.15x) on still
shots so the picture is never frozen for long, and a 0.4 s cross-fade between shots.

## 5. Narration and voices

### 5.1 Writing the script

Write `media/build/NN/script.md` before capturing anything. For each section give the time range,
the voice, the narration text and the list of shots. Template:

```markdown
## Section 2 - 00:25-00:55 - voice: female
Shots: 02-02-slide-12.png (slide 12 of deck 08), 02-03-run.png (terminal, workflow_references.py)

A task in DAGonStar does not need to know where its inputs live. ...
```

Rules for the text:

- Short sentences, active voice, one idea per section (as in `AGENTS.md`).
- Spell identifiers the way a listener can follow: "workflow colon slash slash", "dagon dot ini".
  Put the exact identifier on screen at the same moment.
- Every claim about DAGonStar, DAGonFS or DAGonWeb is checked against its source at the commit
  pinned in `examples/requirements.txt` (DAGonStar 3.0.0) or against the repository of DAGonFS and
  DAGonWeb. Write the file and line you checked as a comment in `script.md`. Do not describe an
  option, a default or a behaviour you have not read.
- Every number spoken or shown comes from the recorded outputs or from the Gulf of Naples dataset
  (`NAP`, `CAP`, `ISC`, 2 November 2026).
- Opening line of every video: "DAGonStar in Practice, video NN: <title>."
  Closing line: "The code, slides and book are free under CC0 at github dot com slash DagOnStar."

### 5.2 Voices

Use a male voice and a female voice. They alternate by section: the male voice opens and closes,
the female voice takes the even sections. Keep the same pair for the whole series.

**Local (default, macOS `say`).** Voices installed on this machine include male `Daniel` (en_GB),
`Reed (English (US))`, `Eddy (English (US))`, and female `Samantha` (en_US), `Shelley (English (US))`,
`Flo (English (US))`. Prefer the *Enhanced* or *Premium* versions if they are installed (System
Settings > Accessibility > Spoken Content > System Voice > Manage Voices). Suggested pair:
male `Daniel`, female `Samantha`.

```bash
say -v Daniel   -r 165 -o media/build/NN/audio/s01.aiff -f media/build/NN/audio/s01.txt
say -v Samantha -r 165 -o media/build/NN/audio/s02.aiff -f media/build/NN/audio/s02.txt
ffmpeg -y -i media/build/NN/audio/s01.aiff -ar 48000 -ac 2 media/build/NN/audio/s01.wav
```

**Local, open source (Linux or macOS).** Piper (`piper --model en_US-ryan-high` male,
`en_US-amy-medium` or `en_GB-jenny_dioco-medium` female) gives more natural voices offline.

**AI service (optional).** OpenAI TTS (`gpt-4o-mini-tts`, voices such as `onyx` male and `nova`
female), ElevenLabs, Azure Neural TTS or Google Cloud TTS may be used for a better sound. Read the
API key from an environment variable, send only the narration text (course material, CC0), and
record the provider, model and voice names in `script.md` and on the closing card
("Voices: <provider> <voice>, synthetic").

Whatever the engine, the closing card says that the voices are synthetic.

### 5.3 Timing

Measure each section with `ffprobe -show_entries format=duration -of csv=p=0 sNN.wav`. Adjust the
text (not the speech rate beyond `-r 150..180`) until the sum of sections plus title and closing
cards is 2:50-3:10. Shots of a section last as long as its audio plus 0.3 s of silence.

## 6. Assembly

1. Title card (5 s): course name, video number and title, a still from the video, no voice or a
   one-line male intro.
2. Body: for each section, render its shots to a clip that lasts exactly as long as its audio:
   ```bash
   ffmpeg -y -loop 1 -t <dur> -i shot.png -vf "scale=1920:1080,zoompan=z='min(zoom+0.0006,1.15)':d=<frames>:s=1920x1080,fps=30,format=yuv420p" -c:v libx264 -crf 20 clip.mp4
   ```
   Concatenate clips with `xfade` (0.4 s) and concatenate the section audio into `narration.wav`.
3. Closing card (10 s): "DAGonStar in Practice", the repository URLs
   (<https://github.com/DagOnStar/dagonstar>, <https://github.com/DagOnStar/DAGonFS>,
   <https://github.com/DagOnStar/DAGonWeb>), "CC0 1.0", "Voices: synthetic (<engine>)".
4. Mux and normalise:
   ```bash
   ffmpeg -y -i video.mp4 -i narration.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 \
     -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart media/videos/<name>.mp4
   ```
5. Subtitles: build `NN.srt` from the section texts and their measured start times, split into
   lines of at most 42 characters and cues of at most 6 s. Copy it next to the `.mp4`.

Claude Code may write these steps as a script in `media/build/make_video.py` that reads
`script.md`; it is a working file, so keep it out of the deliverables unless asked.

## 7. Content of each video

Times are guides; keep the section order. "M" is the male voice, "F" the female voice.

### 00 - Introducing DAGonStar: motivation, context, institutions, authors, contributors, repository, applications, publications

1. M 0:05-0:30 - Why workflows: environmental simulations chain data download, models, AI and
   post-processing across laptops, clusters and clouds. Shots: deck `01` cover and motivation slides.
2. F 0:30-0:55 - What DAGonStar is: a Python engine that runs a directed acyclic graph of tasks "on
   anything" (WORKS 2018 paper title). Shot: README of `DagOnStar/dagonstar` on GitHub.
3. M 0:55-1:20 - Institutions: High-Performance Scientific Computing Laboratory, Department of
   Science and Technology, University of Naples "Parthenope". Partners as named in the bibliography
   (authors' affiliations of the listed papers). Shot: textbook bibliography page.
4. F 1:20-1:50 - Authors and contributors: the authors of the engine publications in
   `bibliography.tex`; contributors as shown by the GitHub contributors page of each repository at
   recording time. Shot: contributors pages of dagonstar, DAGonFS, DAGonWeb. Read names from the
   page; do not list people who do not appear there or in the bibliography.
5. M 1:50-2:20 - Applications: Shoreline Alert Model (PDP 2023), Lagrangian marine pollutant
   transport (PDP 2023, Metrology for the Sea 2022), mussel farming projects MytilX and MytilEx,
   EuroHPC ADMIRE. Shots: bibliography and funding pages.
6. F 2:20-2:50 - Publications and the course: the five engine papers (FGCS 2021, EMS 2021, WF-IoT
   2019, SITIS 2019, WORKS 2018), then the course itself: 48 lectures, 4 appendix decks, textbook,
   54 runnable examples. Shots: textbook cover, `README.md` table.

### 01 - A workflow primer with DAGonStar: introducing eScience

1. M - eScience: computation and data as the third and fourth way of doing science; reproducibility
   needs an explicit description of the steps. Shot: deck `01`.
2. F - From a shell script to a graph: show `examples/02-script-vs-dag/pipeline.sh`, then `as_dag.py`.
3. M - Directed acyclic graphs, topological order, parallel branches. Shot: graph slide of deck `02`.
4. F - Run `examples/01-hello/hello_workflow.py` live; show the output and the task directories.
5. M - Task-oriented and data-oriented workflows (`ch01_introduction.tex`); the running case: hourly
   data of NAP, CAP, ISC on 2 November 2026. Shot: dataset file in `examples/data/`.

### 02 - Introducing DAGonStar: the workflow:// schema

1. M - The problem: a task must read the output of another task without knowing its scratch path.
2. F - The shape `workflow://<workflow>/<task>/<path>` and its components, exactly as in
   `ch04_workflow_schema.tex`, checked against the source.
3. M - Dependency inference: the engine finds the producer, adds the edge, rewrites the command.
   Show the relevant lines of `dagon/` source.
4. F - Run `examples/08-dataflow/workflow_references.py`; show the rewritten command and the result.
5. M - Whitespace boundary rule, cross-workflow references, common errors.

### 03 - Task types and examples, part 1 (local and infrastructure tasks)

1. M - What a task is in DAGonStar; the task-type selector. Shot: deck `06`.
2. F - Batch task: `examples/06-first-task/first_task.py`, run live.
3. M - Native (Python) tasks: `examples/18-native/native_task.py`.
4. F - Containers: Docker and Apptainer tasks (`37-docker`, `38-apptainer`); say that the course runs
   them with local stand-ins unless `DAGON_LIVE_DOCKER=1`.
5. M - Orchestrators and HPC: Kubernetes, Nomad, remote/cloud, Slurm (`41-slurm/slurm_tasks.py`,
   emulated). Shot: the output line that states the emulation.

### 04 - Task types and examples, part 2 (AI-HPC task models)

1. M - Beyond scripts: tasks that call services. Shot: deck `25` cover.
2. F - Web tasks: `examples/25-web-get/web_get.py` against a local stand-in server.
3. M - LLM tasks: `examples/27-llm/llm_task.py` with the mock provider; responsible use (deck `28`).
4. F - FaaS and IoT tasks: `29-faas/faas_mock.py`, `31-iot-observe/iot_observe.py`.
5. M - Agentic tasks and the continuum: `33-agentic-contract/agentic_contract.py`; one graph across
   edge, cloud and HPC (deck `36`).

### 05 - Advanced features: ad-hoc file systems

1. M - Why ad-hoc storage: many small files and shared scratch slow down parallel file systems.
2. F - Ad-hoc volumes and streams in DAGonStar 3.0.0: deck `A2`, `examples/A2-volumes/volume_task.py`
   and `local_directory.py`, run live.
3. M - BeeOND job-local storage: deck `42`, `examples/42-beeond/beeond.py`.
4. F - Pre-staging scheduler inputs: deck `43`.
5. M - Choosing a scratch space; pointer to DAGonFS (video 07).

### 06 - Advanced features: the meta-task type

1. M - A workflow of workflows: meta-workflows (deck `22`) versus meta-tasks (deck `A3`).
2. F - The meta-task contract: a task that runs another engine's workflow, as in the source.
3. M - Run `examples/A3-meta/meta_task.py`; show the `engines/` folder. Say that the CWL step runs
   only when `cwltool` is on `PATH`.
4. F - Outputs, failures and checkpoints of a meta-task.
5. M - When to use a meta-task.

### 07 - DAGonFS: the ad-hoc file system for DAGonStar

1. M - What DAGonFS is, from the README of <https://github.com/DagOnStar/DAGonFS>: requirements
   (MPI, FUSE 3) and goal.
2. F - Block layout: `examples/A1-dagonfs/block_layout.py`; numbers checkable by hand.
3. M - DAGonFS in a workflow: `dagonfs_workflow.py`; explain `DAGONFS_PYTHON` and `DAGONFS`, and that
   the recorded output shows the launch command on a host without DAGonFS.
4. F - Architecture slides of deck `A1`; textbook appendix E.
5. M - Limits and status as written in the DAGonFS documentation.

### 08 - DAGonWeb: the user-friendly interface as computational science and data gateway

DAGonWeb is a Flask/Bootstrap progressive web application: a visual canvas that saves a DAGonStar
task-map JSON document and runs it on the server with `launch()` / `wait()`. Run it locally with
Docker, as its README says (`cp .env.example .env`, `docker compose up --build`, then
<http://localhost:8000>). Set your own admin credentials in `.env` first; never show the `.env`
file, the demo credentials or a signed-in user's data on screen. Enable portable emulation, so
container, scheduler, cloud and LLM tasks run locally. If Docker is not available, the guest
playground's **Dry run** needs no account and executes nothing; capture that instead and say so.

1. M - Science gateways: why a web interface for workflows; who DAGonWeb is for.
2. F - The canvas and the template gallery: open a template, show the palette of task types and the
   inspector. Shots: real pages of the local instance.
3. M - The workflow document: `examples/A4-dagonweb/dagonweb_document.py`, run live, next to the
   same document exported from the browser.
4. F - A live run: the graph updates, the progress bar, the stage of each task, the artifacts of the
   run's scratch directory; then **Resume** after a failed task (checkpoint resume).
5. M - Volume and Meta tasks, stream links (`workflow:///emit/numbers?stream=shared`), exports
   (headless application ZIP, Python program, CWL v1.2), and HPC login-node deployment as in
   `docs/hpc.md`.

### 09 - DAGonService: tracking DAGonStar workflows in production environments

Sources: <https://github.com/DagOnStar/DagOnService> ("REST API to the management of DagOn
workflows") and `dagon/api/` in the pinned DAGonStar commit (`API` client, Flask-based
`WorkflowServer`). DagOnService is a Flask service in `app/main.py` backed by MongoDB
(`mongo:4.0`). `docker-compose up --build` publishes it on port 57000, the default
`[dagon_service] route = http://localhost:57000` of DAGonStar, and
<http://localhost:57000/check> tells whether it is up. Its routes include `POST /create`,
`PUT /changestatus/<workflow_id>/<task>/<status_code>`, `GET /getworkflow/<workflow_name>`,
`GET /<workflow_id>`, `GET /<workflow_id>/<task>`, `POST /add_task/<workflow_id>`,
`PUT /update/<workflow_id>/<task>/<parameter>`, `PUT /<workflow_id>/<task>/dependency/<dependency>`,
`/subscribe/<subscriber_id>/<to_id>/<task>`, `/list`, `/check` and `/delete/<workflow_id>`.
The README mentions a `dashboard` folder, but the repository has none: do not show or describe a
dashboard. The repository was last updated in October 2023; before recording, run it with the
pinned DAGonStar and check that a workflow with `use = True` registers and updates its tasks. If it
does not, record only what works and say so in the narration.

1. M - Why tracking matters in production: many workflows, many users, status after the terminal
   closes.
2. F - Architecture: DAGonStar's `dagon.api.API` client talks to DagOnService over REST; the
   service stores workflows and task states in MongoDB. Shots: `docker-compose.yml`, `app/main.py`.
3. M - Turning it on: `docker-compose up --build`, `curl http://localhost:57000/check`, then
   `[dagon_service] use = True` in `dagon.ini`. Shot: terminal.
4. F - Tracking a run: run a small Gulf of Naples workflow with the service on, then
   `curl http://localhost:57000/list` and `GET /<workflow_id>` while tasks change state.
   Shot: terminal with the JSON answers.
5. M - Cross-workflow lookups through the service (`workflow://` references to other workflows,
   `[ftp_pub]`), and operating it (deck `47`); keep it off (`use = False`, the default) for local
   work and tests.

### 10 - Administrating DAGonStar

1. M - The administrator's view: scratch areas, logs, disk use, failures.
2. F - Scratch, launchers and logs: `examples/10-scratch/inspect_scratch.py`.
3. M - Garbage collection: `examples/14-garbage/garbage_collection.py`.
4. F - Checkpointing and resuming after a failure: `15-checkpoint/checkpoint_resume.py`,
   `16-failures/fail_and_resume.py`.
5. M - Operations checklist: `examples/47-operations/operations.py` and deck `47`.

### 11 - Installation

1. M - Requirements (`ch03_getting_started.tex`): Python version, optional extras.
2. F - Create a virtual environment and install the pinned commit, live:
   `python3 -m venv .venv && source .venv/bin/activate && pip install -r examples/requirements.txt`.
3. M - Extras `docker`, `kubernetes`, and optional `cwltool`, as in `requirements.txt`.
4. F - Check the environment: `examples/04-environment/check_environment.py`.
5. M - Run all examples: `python tools/run_examples.py`; common early pitfalls.

### 12 - Configuration

1. M - Where DAGonStar reads its configuration and in which order (checked in the source).
2. F - `dagon.ini` section by section, from `examples/05-configuration/dagon.ini`:
   `[dagon_service]`, `[ftp_pub]`, `[batch]` and its scratch directory, `[slurm]`, and the logging
   sections (`[loggers]`, `[handlers]`, `[formatters]`); other sections, such as `[dagon_ip]`, only
   as described in `appC_configuration_reference.tex` and the source.
3. M - Run `examples/05-configuration/configuration.py`.
4. F - Secrets: never in the repository; environment variables or local ignored files.
5. M - A pre-flight checklist (from `ch05_configuration.tex`).

### 13 - Wrapping up: an outlook to eScience

1. M - What the series built: one graph from a laptop to HPC, cloud, edge and AI services.
2. F - FAIR workflows: `examples/45-fair/fair.py`, the FAIR bundle.
3. M - Interoperability: CWL export, `examples/46-cwl/cwl_export.py`.
4. F - The capstone: `examples/48-capstone/capstone.py` on the Gulf of Naples data.
5. M - Outlook from `ch17_synthesis.tex`: what generalises beyond DAGonStar; where to go next
   (course repository, textbook, contributing).

## 8. Checks before delivering a video

- [ ] Duration 2:50-3:10 (`ffprobe`), 1920x1080, 30 fps, AAC 48 kHz, -16 LUFS +/- 1.
- [ ] Both voices are present and alternate as in `script.md`; the closing card says they are synthetic.
- [ ] Every shot is a real capture listed in `script.md`; no shot shows personal data or tokens.
- [ ] Every terminal output matches `examples/NN-*/output/*.txt`
      (`python tools/run_examples.py --strict` passes).
- [ ] Every claim has a source reference in `script.md`; every number can be checked by hand.
- [ ] The `.srt` file is in sync (spot-check start, middle and end).
- [ ] The file name is exactly as in section 1.
- [ ] Watched once end to end, with sound, by a person.

## 9. Prompt for Claude Code

> Read `AGENTS.md` and `media/videos_description.md`. Build video `<NN>`: write
> `media/build/<NN>/script.md` following sections 5 and 7, checking every claim against the pinned
> DAGonStar source and the DAGonFS or DAGonWeb repositories; capture the shots following section 4;
> synthesise the narration with a male and a female voice (local `say` voices `Daniel` and
> `Samantha` unless I name an AI service); assemble the video and its subtitles following section 6;
> run the checks of section 8 and report each one. Do not invent screenshots, numbers or features.
> Ask me before uploading anything, sending text to a paid TTS service, or committing the `.mp4`.
