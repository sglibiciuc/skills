"""Shared test helpers: import scripts as modules, run them as CLIs."""
import os
import subprocess
import sys

TESTS = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(TESTS)
FIX = os.path.join(TESTS, "fixtures")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)


def fixture(name):
    return os.path.join(FIX, name)


def read_fixture(name):
    with open(fixture(name), encoding="utf-8") as fh:
        return fh.read()


def run(script, *args, stdin=None, env=None, cwd=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + list(args),
                          input=stdin.encode("utf-8") if stdin is not None else None,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=e, cwd=cwd)
