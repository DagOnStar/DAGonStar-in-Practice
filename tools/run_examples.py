"""Run every course example and check it.

    python tools/run_examples.py            # run all, compare with the recorded outputs
    python tools/run_examples.py 07 21      # only the examples of lectures 07 and 21
    python tools/run_examples.py --record   # run all and rewrite output/*.txt and README.md
    python tools/run_examples.py --strict   # also exit with status 1 on a different output (CI)

An example passes when it exits with status 0 (every example ends with its own
assertions).  Its standard output is compared with examples/NN-*/output/<script>.txt,
the text the slides show: a difference is reported, so that slides and code
cannot silently drift apart.
"""
import ast
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def scripts(only):
    for folder in sorted(EXAMPLES.iterdir()):
        if not folder.is_dir() or folder.name in ("common", "data") or folder.name.startswith("."):
            continue
        if only and not any(folder.name.startswith(o) for o in only):
            continue
        for script in sorted(folder.glob("*.py")):
            yield folder, script


def write_readme(folder):
    lines = ["# %s" % folder.name, ""]
    for script in sorted(folder.glob("*.py")):
        doc = ast.get_docstring(ast.parse(script.read_text())) or ""
        lines += ["## `%s`" % script.name, "", doc, "",
                  "```bash", "python examples/%s/%s" % (folder.name, script.name), "```", "",
                  "Recorded output: [`output/%s.txt`](output/%s.txt)." % (script.stem, script.stem), ""]
    others = [p.name for p in sorted(folder.iterdir()) if p.is_file() and p.suffix not in (".py", ".md")]
    if others:
        lines += ["Other files: " + ", ".join("`%s`" % o for o in others) + ".", ""]
    (folder / "README.md").write_text("\n".join(lines))


def main(argv):
    record = "--record" in argv
    strict = "--strict" in argv
    only = [a for a in argv if not a.startswith("--")]
    failed, changed, count = [], [], 0
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for folder, script in scripts(only):
        count += 1
        started = time.monotonic()
        done = subprocess.run([sys.executable, str(script)], cwd=str(ROOT), env=env,
                              capture_output=True, text=True, timeout=600)
        took = time.monotonic() - started
        name = "%s/%s" % (folder.name, script.name)
        expected = folder / "output" / (script.stem + ".txt")
        if done.returncode:
            failed.append(name)
            print("FAIL %-50s %5.1fs\n%s" % (name, took, done.stderr[-2000:]))
            continue
        if record:
            expected.parent.mkdir(exist_ok=True)
            expected.write_text(done.stdout)
            write_readme(folder)
            status = "rec "
        elif not expected.is_file() or expected.read_text() != done.stdout:
            changed.append(name)
            status = "diff"
        else:
            status = "ok  "
        print("%s %-50s %5.1fs" % (status, name, took))
    print("\n%d examples, %d failed, %d with an output different from the recorded one"
          % (count, len(failed), len(changed)))
    for name in changed:
        print("  changed output:", name)
    return 1 if failed or (strict and changed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
