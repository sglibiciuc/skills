#!/usr/bin/env python3
"""The person's writing profile: find and show it, add one remembered rule, or write it whole.

Global profile:  ${WRITER_HOME:-~/.writer}/style.md  (outside the plugin, survives updates)
Project layer:   .writer/style.md in the current folder or the nearest parent

Subcommands:
  show       print the profile (global, then project layer), the files used, and where a write goes
  remember   append one rule: --rule, --when (where the rule applies), --origin (where it came from);
             the line reads "- [when] rule (origin, YYYY-MM-DD)"
  write      replace the profile with --from FILE (or -)

remember and write change the profile: run them only after the person said yes. Each keeps the previous
file as style.md.bak. They write the global profile; when its folder is not writable they write the project
layer in the current folder instead and say so. --project writes the project layer directly (the nearest
.writer/ in the current folder or a parent, else .writer/ in the current folder).
Exit 0 on success; 2 on bad input or when nothing could be written.
"""

import argparse
import datetime
import os
import shutil
import sys
import tempfile
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _text  # noqa: E402

NAME = "style.md"


def writer_home():
    return os.path.abspath(os.path.expanduser(os.environ.get("WRITER_HOME") or "~/.writer"))


def global_path():
    return os.path.join(writer_home(), NAME)


def project_path(start=None):
    """The nearest .writer/style.md in start or a parent that is not the global profile; None if there is none."""
    d = os.path.abspath(start or os.getcwd())
    skip = {global_path(), os.path.join(os.path.expanduser("~"), ".writer", NAME)}
    while True:
        p = os.path.join(d, ".writer", NAME)
        if os.path.isfile(p) and os.path.abspath(p) not in skip:
            return p
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def project_target(start=None):
    return project_path(start) or os.path.join(os.path.abspath(start or os.getcwd()), ".writer", NAME)


def read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def effective(start=None, project=False):
    g = global_path()
    p = project_path(start)
    used, parts = [], []
    if os.path.isfile(g):
        used.append(g)
        parts.append(read(g).rstrip())
    if p:
        used.append(p)
        parts.append("## Project layer (%s)\n\nAdds to or overrides the global profile for this project.\n\n%s"
                     % (p, read(p).rstrip()))
    return OrderedDict([
        ("global", OrderedDict([("path", g), ("exists", os.path.isfile(g))])),
        ("project", p),
        ("used", used),
        ("writes_to", project_target(start) if project else g),
        ("profile", "\n\n".join(parts) + ("\n" if parts else "")),
    ])


def _atomic_write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bak = None
    fd, tmp = tempfile.mkstemp(prefix=".writer.", suffix=".tmp", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        if os.path.isfile(path):
            bak = path + ".bak"
            shutil.copy2(path, bak)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return bak


def _write(make, project=False, start=None):
    """make(old_text) -> new_text, applied to the global profile; on OSError (or with project) to the project
    layer. Raises OSError when neither can be written."""
    fallback_from, error = None, None
    if not project:
        g = global_path()
        try:
            bak = _atomic_write(g, make(read(g) if os.path.isfile(g) else ""))
            return OrderedDict([("path", g), ("layer", "global"), ("backup", bak),
                                ("fallback_from", None), ("error", None)])
        except OSError as e:
            fallback_from, error = g, "%s: %s" % (type(e).__name__, e)
    p = project_target(start)
    bak = _atomic_write(p, make(read(p) if os.path.isfile(p) else ""))
    return OrderedDict([("path", p), ("layer", "project"), ("backup", bak),
                        ("fallback_from", fallback_from), ("error", error)])


def write_profile(content, project=False, start=None):
    if not content.strip():
        raise _text.BadInput("refusing to write an empty profile")
    return _write(lambda old: content, project, start)


def rule_line(rule, when, origin, date=None):
    parts = [(rule or "").strip(), (when or "").strip(), (origin or "").strip()]
    if not all(parts) or any("\n" in x for x in parts):
        raise _text.BadInput("--rule, --when and --origin are each required, one line each")
    return "- [%s] %s (%s, %s)" % (parts[1], parts[0], parts[2], date or datetime.date.today().isoformat())


def remember(rule, when, origin, project=False, start=None, date=None):
    line = rule_line(rule, when, origin, date)

    def add(old):
        old = old.rstrip("\n")
        return (old + "\n" if old else "") + line + "\n"
    r = _write(add, project, start)
    r["line"] = line
    return r


def report(r, fmt, verb):
    if fmt == "json":
        _text.dump(r)
        return
    print("%s: %s (%s layer)" % (verb, r["path"], r["layer"]))
    if r.get("line"):
        print(r["line"])
    if r["fallback_from"]:
        print("could not write the global profile %s (%s); saved as the project layer instead"
              % (r["fallback_from"], r["error"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Show the writing profile, add one remembered rule, or write it whole.")
    sub = ap.add_subparsers(dest="cmd")
    p_show = sub.add_parser("show", help="print the profile, the files used and where a write goes")
    p_rem = sub.add_parser("remember", help="append one rule with where it applies and where it came from "
                           "(only after the person said yes)")
    p_rem.add_argument("--rule", required=True, help="the rule, one line")
    p_rem.add_argument("--when", required=True, help="where the rule applies, e.g. 'emails to clients'")
    p_rem.add_argument("--origin", required=True, help="where it came from, e.g. 'reply to Marta'")
    p_write = sub.add_parser("write", help="replace the profile (only after the person said yes)")
    p_write.add_argument("--from", dest="src", required=True, help="profile text file, or -")
    for p in (p_show, p_rem, p_write):
        p.add_argument("--project", action="store_true",
                       help="use the project layer .writer/style.md (nearest existing, else in the current folder)")
        p.add_argument("--format", choices=("json", "text"), default="json")
    a = ap.parse_args(argv)
    if not a.cmd:
        ap.print_help()
        return 2
    if a.cmd == "show":
        r = effective(project=a.project)
        if a.format == "json":
            _text.dump(r)
        else:
            print("used: " + (", ".join(r["used"]) or "none"))
            print("writes to: " + r["writes_to"])
            print(r["profile"] if r["used"] else "no profile yet")
        return 0
    try:
        if a.cmd == "remember":
            report(remember(a.rule, a.when, a.origin, project=a.project), a.format, "remembered in")
        else:
            report(write_profile(_text.read_input(a.src), project=a.project), a.format, "written")
    except _text.BadInput as e:
        _text.fail(str(e))
    except OSError as e:
        _text.fail("could not write the profile: %s: %s" % (type(e).__name__, e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
