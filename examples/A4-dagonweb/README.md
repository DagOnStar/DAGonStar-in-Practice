# A4-dagonweb

## `dagonweb_document.py`

Appendix A4: a DAGonWeb workflow document, loaded and run by DAGonStar.

DAGonWeb saves what you draw as a DAGonStar task-map document; editor state
lives only in additive "dagonweb" keys.  This script writes such a document
for the station pipeline by hand, with the conventions DAGonWeb uses (named
inputs prepended as shell assignments, one explicit dependency in
explicit_prevs), and runs it the way DAGonWeb's executor does: load the
document, apply the runtime options, run with a checkpoint.  The first run
fails on a typo in report; the "fixed" document is resumed, as DAGonWeb's
Resume button does.  No web server is started: DAGonWeb itself is not needed
to run its documents.

```bash
python examples/A4-dagonweb/dagonweb_document.py
```

Recorded output: [`output/dagonweb_document.txt`](output/dagonweb_document.txt).
