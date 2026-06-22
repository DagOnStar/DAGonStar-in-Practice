# DAGonStar in Practice — Textbook (LaTeX source)

This folder contains the full LaTeX source for the academic textbook
*DAGonStar in Practice: Orchestrating AI–HPC Workflows for Computational
Environmental Science*, derived from the DAGonStar project documentation
(`docs/` directory, `development-native-web` branch of
https://github.com/DagOnStar/dagonstar).

## How to build

### On Overleaf
1. Upload this entire folder (or the zip it came from) as a new Overleaf project.
2. Set the main document to `main.tex` (Overleaf usually detects this automatically).
3. Compile with **pdfLaTeX** (the default engine). Two passes are normally
   triggered automatically by Overleaf to resolve cross-references, the
   table of contents, and the list of figures.

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

(Three passes ensure the table of contents, list of figures, list of
listings, and all `\Cref`/`\ref` cross-references are fully resolved.)

## Project structure

```
main.tex                  Document class, preamble, packages, chapter includes
front/abstract.tex        Front-matter abstract
front/preface.tex         Front-matter preface
front/bibliography.tex    Back-matter bibliography & source provenance
chapters/ch01_*.tex ...   17 narrative chapters (Parts I–III)
chapters/appA_*.tex ...   4 reference appendices
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
