# AGENTS.md

Instructions for anyone, human or AI agent, who changes the teaching material in this repository.
Follow them so that slides, notes, textbook and code stay correct and say the same thing.

## 1. What the repository contains

| Path | Content | Edited by hand? |
|------|---------|-----------------|
| `src/lectures/NN.js`, `src/lectures/A1.js`-`A4.js` | source of lecture NN: cover data and 29 slide descriptions | yes |
| `src/lib.js` | deck builder: theme, layouts, slide kinds, layout warnings | yes, with care |
| `src/build.js`, `src/notes.js`, `src/count.js` | build the decks, write the notes, count the slides | yes, with care |
| `en/lectures/` | the 48 decks and `A1`-`A4` (`.pptx`) | **no**: generated |
| `en/notes/` | the lecture notes (Markdown) | **no**: generated |
| `examples/NN-topic/*.py` | runnable examples, one folder per lecture | yes |
| `examples/NN-topic/output/*.txt`, `examples/NN-topic/README.md` | recorded outputs and READMEs | **no**: `python tools/run_examples.py --record` |
| `examples/common/`, `examples/data/` | shared helpers and the Gulf of Naples dataset | yes, then re-record every example |
| `examples/requirements.txt` | the pinned DAGonStar commit the course is tested against | yes, then re-run every example |
| `en/textbook/main.tex`, `chapters/`, `front/` | the LaTeX textbook: preamble and cover, chapters, front and back matter | yes |
| `en/textbook/front/version.tex` | version, date and version history of the book | yes, before every release |
| `en/textbook/figures/` | the cover image (DAGonWeb workflow editor, Apache 2.0) | yes, with care |
| `en/textbook/Workflows_in_Practice_with_DAGonStar.pdf` | the built textbook | **no**: `latexmk -pdf main.tex`, then commit it |
| `tools/run_examples.py` | runs and checks every example | yes |
| `.github/workflows/` | CI checks and the release workflow | yes |
| `LICENSE`, `README.md`, `AGENTS.md` | licence, overview, these rules | yes |

Never edit generated files: change their source and rebuild.

## 2. Structure of the course

- The course and the book are titled **Workflows in Practice with DAGonStar**, subtitled
  *Orchestrating AI–HPC Workflows for Computational Science*. The use case is environmental
  computational science. The name lives in `COURSE` (and `SUBTITLE`, `USE_CASE`) of `src/lib.js`
  and in the title block of `en/textbook/main.tex`; change both together and rebuild every deck.

- 48 lectures in four parts of twelve (01-12 Foundations, 13-24 Execution, data and recovery,
  25-36 Task models for AI-HPC, 37-48 Infrastructure, data and FAIR), plus the appendix decks `A1` DAGonFS, `A2` ad-hoc volumes and streams, `A3` meta-tasks and
  `A4` DAGonWeb.
- Every deck has **exactly 30 slides**: the cover plus 29 entries. `node count.js` checks it.
- Theory and hands-on work are **not** separated. Every lecture introduces a concept and runs it,
  with its own example folder.
- English only.

## 3. The textbook

- `latexmk -pdf main.tex` writes `Workflows_in_Practice_with_DAGonStar.pdf`: the name is set in
  `en/textbook/.latexmkrc`. Do not rename `main.tex`.
- **Versioning.** The book follows `MAJOR.MINOR.PATCH` (new edition, new material, correction), kept in
  `front/version.tex`. A change that will be released bumps `\bookversion` and `\bookdate` and adds a
  row to `\bookhistory`. The release tag must be `v` plus that version: the release workflow refuses
  any other. The date is written out, never `\today`, so the title page is reproducible.
- **Cover.** The title page holds the title, subtitle, use case, the cover image, the author, the
  contributors and the version. It must fit on **one page**: if the colophon (`front/colophon.tex`,
  version, licence, cover credit, history) is not on page ii, the cover has grown too tall.
- **Contributors** are listed on the cover with `\contributor{given names}{family name}`, in
  alphabetical order of **family name**, then given names. Family names can have several words:
  Barrón Lugo, De Vita, Di Luccio, Domizzi Sánchez-Gallegos (Dante and Genaro), Torres Charles.
  Each has a department, university and country.
- **Third-party images** keep their licence. The cover image is cropped from DAGonWeb's
  `docs/images/volume-editor.png` (Apache 2.0); the colophon credits it and excludes it from the CC0
  dedication. Credit any new third-party image the same way.

## 4. Correctness rules

- **The code is the reference.** Every claim about DAGonStar must be checked against its source
  (`dagon/`) at the commit pinned in `examples/requirements.txt`, and every claim about DAGonFS
  against <https://github.com/DagOnStar/DAGonFS>, and every claim about DAGonWeb against
  <https://github.com/DagOnStar/DAGonWeb>. Do not describe an option, a default or an
  error message you have not read in the source.
- **Examples are self-checking.** Each script runs in a temporary scratch directory (helpers in
  `examples/common/course.py`), ends with `check(...)` assertions, and needs no external service:
  use mocks, local stand-ins or portable emulation, and say so in the output.
- **Slides and the book never contain code that does not run.** `<code/>` slides and the textbook's
  `\lstinputlisting` read the files in `examples/`; result slides and the book show the recorded
  `output/*.txt`. A change to an example is followed by `python tools/run_examples.py --record`, a
  rebuild of the affected decks and a textbook build.
- Numbers shown to students (means, spreads, scores, block counts) must be checkable by hand from
  the dataset or the formula on the same slide.

## 5. Before committing

```bash
python tools/run_examples.py --strict        # 54 examples, 0 failed, 0 different
cd src && node count.js && node build.js && node notes.js
cd en/textbook && latexmk -pdf main.tex     # no undefined references; writes Workflows_in_Practice_with_DAGonStar.pdf
```

Run the examples against the **pinned** DAGonStar (`pip install -r examples/requirements.txt` in a
clean virtual environment), not against a development checkout of DAGonStar: a newer client can
break the mocks (lecture 47 mocks `requests.head` and `requests.post` of `dagon.api`). Appendix A1
needs `DAGONFS_PYTHON` pointing at the `python/` folder of a DAGonFS checkout at the commit used in
`.github/workflows/ci.yml`; without it, its output differs from the recorded one.

`node build.js` exits with status 1 on any layout warning (code too long for its box, text that
overflows, a graph label that PowerPoint would break mid-word); fix the warning, do not ignore it.
Builds are reproducible: rebuilding an unchanged source gives the same `.pptx` bytes, so commit
every deck that git shows as changed. On macOS, `tools/export_decks_powerpoint.sh A2 A4` exports
decks to PDF with PowerPoint itself; look at new or changed slides there before committing.

The same checks run in GitHub Actions (`.github/workflows/ci.yml`) on every push and pull request;
a pushed `v*` tag publishes a release (`.github/workflows/release.yml`). Keep both green.

## 6. Style

- Short sentences, active voice, one idea per slide.
- Code, commands, file names and identifiers in English, exactly as in the examples.
- The running case is the Gulf of Naples dataset (`NAP`, `CAP`, `ISC`, 2 November 2026). Keep new
  examples on it.
- Material is released under CC0 1.0, except third-party images, which keep their own licence.
