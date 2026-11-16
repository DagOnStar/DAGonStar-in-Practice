# A1-dagonfs

## `block_layout.py`

Appendix A: the DAGonFS block layout, computed from (S, P) alone.

A file of S bytes is padded to N = ceil(S / B) blocks of B = 128 KiB; rank r
of P owns c_r = floor(N / P) + [r < N mod P] consecutive blocks starting at
d_r = sum of c_q for q < r (DAGonFS docs/DATA-PLANE.md, sections 1-2).

```bash
python examples/A1-dagonfs/block_layout.py
```

Recorded output: [`output/block_layout.txt`](output/block_layout.txt).

## `dagonfs_workflow.py`

Appendix A: a DAGonStar workflow whose scratch lives on a DAGonFS volume.

On a Linux node with MPI, FUSE 3 and a DAGonFS build, set
  DAGONFS_PYTHON=/path/to/DAGonFS/python  DAGONFS=/path/to/build/dagonfs
and the script mounts a client-server volume, runs the workflow on it, copies
the result to persistent storage (stage-out) and unmounts the volume.
Anywhere else it runs the same workflow on a temporary directory, so the
workflow itself is always tested.

```bash
python examples/A1-dagonfs/dagonfs_workflow.py
```

Recorded output: [`output/dagonfs_workflow.txt`](output/dagonfs_workflow.txt).
