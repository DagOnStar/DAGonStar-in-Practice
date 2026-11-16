# AGENTS.md

Instructions for anyone, human or AI agent, who changes the teaching material in this repository.
Follow them so that slides, notes, textbook and code stay correct and say the same thing.

## 1. What the repository contains

| Path | Content | Edited by hand? |
|------|---------|-----------------|
| `src/lectures/NN.js`, `src/lectures/A1.js` | source of lecture NN: cover data and 29 slide descriptions | yes |
| `src/lib.js` | deck builder: theme, layouts, slide kinds, layout warnings | yes, with care |
| `src/build.js`, `src/notes.js`, `src/count.js` | build the decks, write the notes, count the slides | yes, with care |
| `en/lectures/` | the 48 decks and `A1` (`.pptx`) | **no**: generated |
| `en/notes/` | the lecture notes (Markdown) | **no**: generated |
| `examples/NN-topic/*.py` | runnable examples, one folder per lecture | yes |
| `examples/NN-topic/output/*.txt`, `examples/NN-topic/README.md` | recorded outputs and READMEs | **no**: `python tools/run_examples.py --record` |
| `examples/common/`, `examples/data/` | shared helpers and the Gulf of Naples dataset | yes, then re-record every example |
| `examples/requirements.txt` | the pinned DAGonStar commit the course is tested against | yes, then re-run every example |
| `en/textbook/` | the LaTeX textbook | yes |
| `tools/run_examples.py` | runs and checks every example | yes |
| `LICENSE`, `README.md`, `AGENTS.md` | licence, overview, these rules | yes |

Never edit generated files: change their source and rebuild.

## 2. Structure of the course

- 48 lectures in four parts of twelve (01-12 Foundations, 13-24 Execution, data and recovery,
  25-36 Task models for AI-HPC, 37-48 Infrastructure, data and FAIR), plus `A1` on DAGonFS.
- Every deck has **exactly 30 slides**: the cover plus 29 entries. `node count.js` checks it.
- Theory and hands-on work are **not** separated. Every lecture introduces a concept and runs it,
  with its own example folder.
- English only.

## 3. Correctness rules

- **The code is the reference.** Every claim about DAGonStar must be checked against its source
  (`dagon/`) at the commit pinned in `examples/requirements.txt`, and every claim about DAGonFS
  against <https://github.com/DagOnStar/DAGonFS>. Do not describe an option, a default or an
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

## 4. Before committing

```bash
python tools/run_examples.py                 # 50 examples, 0 failed, 0 different
cd src && node count.js && node build.js && node notes.js
cd en/textbook && latexmk -pdf main.tex     # no undefined references
```

`node build.js` exits with status 1 on any layout warning (code too long for its box, text that
overflows); fix the warning, do not ignore it.

## 5. Style

- Short sentences, active voice, one idea per slide.
- Code, commands, file names and identifiers in English, exactly as in the examples.
- The running case is the Gulf of Naples dataset (`NAP`, `CAP`, `ISC`, 2 November 2026). Keep new
  examples on it.
- Material is released under CC0 1.0.
