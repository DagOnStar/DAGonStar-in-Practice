"""Lecture 04: check the installation without any configuration file."""
import importlib.util
import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dagon
from dagon.platform_support import bash_executable
from dagon.task import TaskType
from common.course import check

try:
    installed = version("dagonstar")
except PackageNotFoundError:
    installed = "not installed (checkout on sys.path)"

print("Python", platform.python_version(), "on", platform.system())
print("dagonstar", installed, "from", Path(dagon.__file__).parent.name)
print("bash:", bash_executable())
print("task types:", len(TaskType))
OPTIONAL = ("docker", "kubernetes", "libcloud", "globus_sdk", "cwltool")
for name in OPTIONAL:
    found = importlib.util.find_spec(name) is not None
    print("  optional %-11s %s" % (name, "present" if found else "absent"))
check(sys.version_info >= (3, 8), "DAGonStar needs Python 3.8 or later")
check(Path(bash_executable()).exists(), "a bash shell runs the launchers")
