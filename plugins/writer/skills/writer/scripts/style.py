#!/usr/bin/env python3
"""The person's writing profile: find and show it, filter rule candidates, add or decline one rule, or write it whole.

Global profile:  ${WRITER_HOME:-~/.writer}/style.md  (outside the plugin, survives updates)
Project layer:   .writer/style.md in the current folder or the nearest parent
Declined rules:  declined.md beside each style.md (both layers are read)

Subcommands:
  show       print the profile (global, then project layer), the files used, where a write goes, and
             summary {rules, updated, declined}: rule lines ("- ") in the used files, the date the newest
             used file changed, declined rules in both layers
  review     filter rule candidates from --candidates FILE (or -), a JSON list of {"rule","when","origin"}:
             drops those already in the profile or declined, keeps at most 3; prints
             {"propose", "dropped": [{"rule","reason": in_profile|declined|limit}], "declined": [declined rule
             texts, both layers], "writes_to"}; writes nothing
  remember   append one rule: --rule, --when (where the rule applies), --origin (where it came from);
             the line reads "- [when] rule (origin, YYYY-MM-DD)"
  decline    append one declined rule to declined.md: --rule, --when; the line reads "- [when] rule (YYYY-MM-DD)"
  write      replace the profile with --from FILE (or -)

remember, decline and write change files: run them only after the person said yes (decline: after their no).
Each keeps the previous file as <name>.bak. They write the global layer; when its folder is not writable they
write the project layer in the current folder instead and say so. --project uses the project layer directly
(the nearest .writer/ in the current folder or a parent, else .writer/ in the current folder).
Exit 0 on success; 2 on bad input or when nothing could be written.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import sys
import tempfile
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _text  # noqa: E402

NAME = "style.md"
DECLINED = "declined.md"
LIMIT = 3
RULE_RE = re.compile(r"^- (?:\[[^\]]*\]\s*)?(.*?)(?:\s*\((?:[^()]|\([^()]*\))*\d{4}-\d{2}-\d{2}\))?\s*$")


def writer_home():
    return os.path.abspath(os.path.expanduser(os.environ.get("WRITER_HOME") or "~/.writer"))


def global_path(name=NAME):
    return os.path.join(writer_home(), name)


def project_path(start=None, name=NAME):
    """The nearest .writer/<name> in start or a parent that is not the global one; None if there is none."""
    d = os.path.abspath(start or os.getcwd())
    skip = {global_path(name), os.path.join(os.path.expanduser("~"), ".writer", name)}
    while True:
        p = os.path.join(d, ".writer", name)
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


def rule_lines(paths):
    lines = []
    for path in paths:
        lines += [x.rstrip() for x in read(path).splitlines() if x.startswith("- ")]
    return lines


def norm(rule):
    return re.sub(r"\s+", " ", rule).strip().rstrip(".").strip().casefold()


def rules_of(paths):
    return [RULE_RE.match(x).group(1) for x in rule_lines(paths)]


def rule_texts(paths):
    return {norm(x) for x in rules_of(paths)}


def declined_paths(start=None):
    return [p for p in (global_path(DECLINED), project_path(start, DECLINED)) if p and os.path.isfile(p)]


def summary(used, start=None):
    updated = max((os.path.getmtime(p) for p in used), default=None)
    return OrderedDict([
        ("rules", len(rule_lines(used))),
        ("updated", datetime.date.fromtimestamp(updated).isoformat() if updated is not None else None),
        ("declined", len(rule_lines(declined_paths(start)))),
    ])


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
        ("summary", summary(used, start)),
    ])


def review(candidates, start=None, project=False):
    """Split candidates into those to propose (at most LIMIT) and those dropped with a reason. Writes nothing."""
    if not isinstance(candidates, list):
        raise _text.BadInput("candidates must be a JSON list of {\"rule\", \"when\", \"origin\"}")
    e = effective(start, project)
    declined_rules = rules_of(declined_paths(start))
    known, declined = rule_texts(e["used"]), {norm(x) for x in declined_rules}
    propose, dropped = [], []
    for c in candidates:
        if not isinstance(c, dict) or not all(isinstance(c.get(k), str) and c[k].strip() and "\n" not in c[k]
                                              for k in ("rule", "when", "origin")):
            raise _text.BadInput("each candidate needs rule, when and origin, one line each")
        key = norm(c["rule"])
        reason = ("in_profile" if key in known else "declined" if key in declined else
                  "limit" if len(propose) >= LIMIT else None)
        if reason:
            dropped.append(OrderedDict([("rule", c["rule"]), ("reason", reason)]))
        else:
            propose.append(OrderedDict((k, c[k]) for k in ("rule", "when", "origin")))
    return OrderedDict([("propose", propose), ("dropped", dropped), ("declined", declined_rules),
                        ("writes_to", e["writes_to"])])


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


def _write(make, project=False, start=None, name=NAME):
    """make(old_text) -> new_text, applied to the global <name>; on OSError (or with project) to <name> beside
    the project layer's style.md. Raises OSError when neither can be written."""
    fallback_from, error = None, None
    if not project:
        g = global_path(name)
        try:
            bak = _atomic_write(g, make(read(g) if os.path.isfile(g) else ""))
            return OrderedDict([("path", g), ("layer", "global"), ("backup", bak),
                                ("fallback_from", None), ("error", None)])
        except OSError as e:
            fallback_from, error = g, "%s: %s" % (type(e).__name__, e)
    p = os.path.join(os.path.dirname(project_target(start)), name)
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


def decline(rule, when, project=False, start=None, date=None):
    parts = [(rule or "").strip(), (when or "").strip()]
    if not all(parts) or any("\n" in x for x in parts):
        raise _text.BadInput("--rule and --when are each required, one line each")
    line = "- [%s] %s (%s)" % (parts[1], parts[0], date or datetime.date.today().isoformat())

    def add(old):
        old = old.rstrip("\n")
        return (old + "\n" if old else "") + line + "\n"
    r = _write(add, project, start, DECLINED)
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
    ap = argparse.ArgumentParser(description="Show the writing profile, filter rule candidates, add or decline "
                                 "one rule, or write it whole.")
    sub = ap.add_subparsers(dest="cmd")
    p_show = sub.add_parser("show", help="print the profile, the files used, where a write goes and a summary")
    p_rev = sub.add_parser("review", help="filter rule candidates against the profile and declined rules; "
                           "writes nothing")
    p_rev.add_argument("--candidates", default="-", help="JSON list of {rule, when, origin}: file, or - (default)")
    p_rem = sub.add_parser("remember", help="append one rule with where it applies and where it came from "
                           "(only after the person said yes)")
    p_rem.add_argument("--rule", required=True, help="the rule, one line")
    p_rem.add_argument("--when", required=True, help="where the rule applies, e.g. 'emails to clients'")
    p_rem.add_argument("--origin", required=True, help="where it came from, e.g. 'reply to Marta'")
    p_dec = sub.add_parser("decline", help="record a rule the person declined (only after their no)")
    p_dec.add_argument("--rule", required=True, help="the declined rule, one line")
    p_dec.add_argument("--when", required=True, help="where it would have applied")
    p_write = sub.add_parser("write", help="replace the profile (only after the person said yes)")
    p_write.add_argument("--from", dest="src", required=True, help="profile text file, or -")
    for p in (p_show, p_rev, p_rem, p_dec, p_write):
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
            s = r["summary"]
            print("profile: %d rules, updated %s" % (s["rules"], s["updated"]) if r["used"] else "no profile yet")
            print("used: " + (", ".join(r["used"]) or "none"))
            print("writes to: " + r["writes_to"])
            if r["used"]:
                print(r["profile"])
        return 0
    try:
        if a.cmd == "review":
            raw = _text.read_input(a.candidates)
            try:
                candidates = json.loads(raw) if raw.strip() else []
            except ValueError as e:
                raise _text.BadInput("candidates are not valid JSON: %s" % e)
            r = review(candidates, project=a.project)
            if a.format == "json":
                _text.dump(r)
            else:
                for i, c in enumerate(r["propose"], 1):
                    print("%d. [%s] %s (%s)" % (i, c["when"], c["rule"], c["origin"]))
                if not r["propose"]:
                    print("no new rules")
                print("writes to: " + r["writes_to"])
        elif a.cmd == "remember":
            report(remember(a.rule, a.when, a.origin, project=a.project), a.format, "remembered in")
        elif a.cmd == "decline":
            report(decline(a.rule, a.when, project=a.project), a.format, "declined in")
        else:
            report(write_profile(_text.read_input(a.src), project=a.project), a.format, "written")
    except _text.BadInput as e:
        _text.fail(str(e))
    except OSError as e:
        _text.fail("could not write the profile: %s: %s" % (type(e).__name__, e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
