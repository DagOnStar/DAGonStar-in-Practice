"""Appendix A: the DAGonFS block layout, computed from (S, P) alone.

A file of S bytes is padded to N = ceil(S / B) blocks of B = 128 KiB; rank r
of P owns c_r = floor(N / P) + [r < N mod P] consecutive blocks starting at
d_r = sum of c_q for q < r (DAGonFS docs/DATA-PLANE.md, sections 1-2).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.course import check

B = 131072


def layout(size, ranks):
    blocks = -(-size // B)                      # ceil without floats
    counts = [blocks // ranks + (1 if r < blocks % ranks else 0) for r in range(ranks)]
    starts = [sum(counts[:r]) for r in range(ranks)]
    return blocks, counts, starts


for size, ranks in ((12 * 47, 4), (1_000_000, 4), (5 * B + 1, 4), (128 * 2**20, 4), (0, 4)):
    blocks, counts, starts = layout(size, ranks)
    print("S=%-10d P=%d  N=%-4d c=%s d=%s" % (size, ranks, blocks, counts, starts))
    check(sum(counts) == blocks, "every block has an owner")
    check(max(counts) - min(counts) <= 1, "balanced within one block")
    check(counts[0] == max(counts), "rank 0 holds at least as many blocks as any rank")
    check(blocks == 0 or counts[0] > 0, "if rank 0 holds nothing, nobody does")
