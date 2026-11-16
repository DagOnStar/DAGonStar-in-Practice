"""Helpers shared by every example of the course.

Every example builds its workflow from a configuration dictionary that points
the scratch space at a fresh temporary directory, so no example needs a
dagon.ini, a credential or a network service, and no example leaves files
behind.  The data are the synthetic Gulf of Naples observations in
examples/data/gulf_of_naples.csv: three stations (NAP Naples, CAP Capri,
ISC Ischia), four hourly records each.
"""
import json
import shlex
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parents[1]
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

from dagon import Workflow  # noqa: E402

DATA = EXAMPLES / "data" / "gulf_of_naples.csv"
STATIONS = ("NAP", "CAP", "ISC")


def config(scratch, extra=None, remove_dir=False):
    """The configuration dictionary of a local workflow whose scratch is *scratch*."""
    value = {
        "batch": {"scratch_dir_base": str(scratch), "run_base": "", "threads": "2",
                  "remove_dir": str(remove_dir)},
        "dagon_service": {"use": "False"},
        "ftp_pub": {"ip": "localhost"},
        "slurm": {"partition": ""},
    }
    for section, options in (extra or {}).items():
        value.setdefault(section, {}).update(options)
    return value


def workflow(name, scratch, extra=None, remove_dir=False, **options):
    """A Workflow configured for *scratch*; *options* go to the Workflow constructor."""
    return Workflow(name, config=config(scratch, extra, remove_dir), **options)


@contextmanager
def scratch(lecture):
    """A temporary scratch directory, removed when the block ends."""
    with tempfile.TemporaryDirectory(prefix="dagon-course-%s-" % lecture) as path:
        yield Path(path)


def fetch_observations(target="outputs/observations.csv"):
    """Shell command that copies the course dataset into a task's working directory."""
    folder = str(Path(target).parent)
    return "mkdir -p %s && cp %s %s" % (folder, shlex.quote(str(DATA)), target)


def station_mean(station, source, target):
    """Shell command: mean temperature of one station with awk."""
    return ("mkdir -p outputs && awk -F, -v s=%s '$1==s{t+=$3;n++}END{printf \"%%s %%.2f\\n\", s, t/n}' %s > %s"
            % (station, source, target))


def text(task, relative):
    """Content of a file in a task's working directory."""
    return Path(task.working_dir, relative).read_text(encoding="utf-8")


def load(task, relative):
    """JSON content of a file in a task's working directory."""
    return json.loads(text(task, relative))


def where(task):
    """The task directory name without its timestamp: <timestamp>-<name> becomes <name>."""
    return Path(task.working_dir).name.split("-", 1)[1]


def check(condition, message):
    """Fail loudly: every example ends with checks, not only with prints."""
    if not condition:
        raise AssertionError(message)
