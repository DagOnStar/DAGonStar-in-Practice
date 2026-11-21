# Workflows in Practice with DAGonStar — Textbook (LaTeX source)

This folder contains the LaTeX source of *Workflows in Practice with DAGonStar:
Orchestrating AI–HPC Workflows for Computational Science*, the companion textbook
of the 48-lecture course. Its use case is environmental computational science,
on the Gulf of Naples dataset. It is aligned with DAGonStar 3.0.0
(https://github.com/DagOnStar/dagonstar), DAGonFS
(https://github.com/DagOnStar/DAGonFS) and DAGonWeb
(https://github.com/DagOnStar/DAGonWeb).

Course examples and their recorded outputs are included with
`\lstinputlisting{../../examples/...}`, so the book must be built inside the
repository checkout (or, on Overleaf, from an upload of the whole repository with
`en/textbook/main.tex` as the main document).

## How to build

### Locally (TeX Live / MacTeX / MiKTeX)

```bash
latexmk -pdf main.tex
```

or, manually:

```bash
pdflatex main.tex
pdflatex main.tex
pdflatex main.tex
```

`latexmk` reads `.latexmkrc`, which names the output
`Workflows_in_Practice_with_DAGonStar.pdf`. With plain `pdflatex`, pass
`-jobname=Workflows_in_Practice_with_DAGonStar` to get the same name.

The version of the book (`MAJOR.MINOR.PATCH`), its date and its history are in
`front/version.tex`; see the repository README for how a version is released.

(Three passes ensure the table of contents, list of figures, list of
listings, and all `\Cref`/`\ref` cross-references are fully resolved.)

## Project structure

```
main.tex                  Document class, preamble, packages, chapter includes
front/version.tex         Version number, date and version history
front/colophon.tex        Verso of the title page: version, use case, licence, history
front/abstract.tex        Front-matter abstract
front/preface.tex         Front-matter preface
front/bibliography.tex    Back-matter bibliography & source provenance
chapters/ch*.tex           22 chapters in four parts that follow the lectures
chapters/app*.tex          appendices A-H (E: DAGonFS, F: ad-hoc volumes,
                          G: meta-tasks, H: DAGonWeb)
```

## Dependencies

The document uses only packages available in a standard, full TeX Live /
Overleaf installation: `tikz`, `listings`, `tcolorbox`, `hyperref`,
`cleveref`, `booktabs`, `enumitem`, `microtype`, `fancyhdr`, `titlesec`,
`epigraph`, `appendix`. No external image files are required — all figures
are generated inline with TikZ.

## Content provenance

Every code listing, configuration fragment, and "Lesson box" reproduced in
this book is drawn directly from the DAGonStar `docs/` directory and
`docs/tutorial/` lesson sequence. See `front/bibliography.tex` for full
source attribution.
