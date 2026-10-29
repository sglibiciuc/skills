#!/usr/bin/env python3
"""Analyze staged Writer drafts. Never calls a model, rewrites, or scores text.

PostToolUse observes the staging receipt, binds that private draft to this
session, and analyzes changed revisions before the next model request.
Stop checks an active draft's receipt, not whether the text has zero findings.
It is recovery for an incomplete workflow, not an interception of UI messages.
"""
import json
from pathlib import Path
import re
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/writer/scripts"))
import draft


def context(event, text):
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


def strings(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "\n".join(strings(v) for v in value.values())
    if isinstance(value, list):
        return "\n".join(strings(v) for v in value)
    return ""


def process(data):
    if not isinstance(data, dict):
        return None
    event = data.get("hook_event_name")
    sid = data.get("session_id")
    cwd = data.get("cwd")
    if not isinstance(sid, str) or not sid or not isinstance(cwd, str):
        return None
    session_path = draft.root() / ("session-" + draft.digest(sid) + ".json")
    session = draft.load(session_path) if session_path.exists() else {"ids": []}
    if event == "SessionStart":
        return context(event, "Writer hooks are active. Session id: " + sid + ". "
                       "Pass --session " + sid + " when starting a draft.py source or put. "
                       "Staging returns analysis automatically; deliver only text returned by draft.py accept.")
    if event == "UserPromptSubmit":
        session.pop("active", None)
        session["current"] = []
        if session_path.exists():
            draft.save(session_path, session)
        return None
    if event == "SessionEnd":
        for ident in session["ids"]:
            try:
                path, meta = draft.state(ident, cwd)
                if meta.get("owner") == draft.digest(sid):
                    shutil.rmtree(path)
            except (OSError, draft.DraftError):
                pass
        if session_path.exists():
            session_path.unlink()
        return None
    if event == "PostToolUse":
        command = strings(data.get("tool_input", {}))
        staging = re.search(r"draft\.py[\"']?\s+(?:source|put)\b", command)
        response = strings(data.get("tool_response", ""))
        ids = re.findall(r"WRITER_DRAFT:([a-f0-9]{32})(?![a-f0-9])", response) if staging else []
        for ident in ids:
            path, meta = draft.state(ident, cwd)
            owner = draft.digest(sid)
            if meta.get("owner") != owner:
                continue
            session["active"] = ident
            if ident not in session["ids"]:
                session["ids"].append(ident)
            if ident not in session.setdefault("current", []):
                session["current"].append(ident)
        if ids:
            draft.save(session_path, session)
    ident = session.get("active")
    if not ident or event not in ("PostToolUse", "Stop"):
        return None
    path, meta = draft.state(ident, cwd)
    rev = draft.revision(path, meta)
    previous = draft.load(path / "analysis.json") if (path / "analysis.json").exists() else {}
    changed = previous.get("revision") != rev
    report = draft.analyze(ident, cwd)
    if event == "PostToolUse" and (changed or ids):
        return context(event, "Writer private analysis (not for the person):\n" +
                       json.dumps(report, ensure_ascii=False) +
                       "\nRead the findings. Revise with draft.py put --id, or keep each remaining "
                       "finding with a reason in draft.py accept --revision. Copy only accepted text into the final reply. "
                       "A source analysis is input for rewriting, not a finished draft.")
    if event == "Stop":
        try:
            for current in session.get("current", [ident]):
                draft.accepted(current, cwd)
        except (draft.DraftError, OSError, ValueError, KeyError):
            pending = draft.analyze(current, cwd)
            return {"decision": "block", "reason": "Writer private draft " + current +
                    " is not ready. Review its current analysis and accept this revision before delivering text.\n" +
                    json.dumps(pending, ensure_ascii=False)}
    return None


def main():
    data = {}
    try:
        data = json.load(sys.stdin)
        result = process(data)
    except (OSError, ValueError, KeyError, draft.DraftError) as error:
        event = data.get("hook_event_name", "") if isinstance(data, dict) else ""
        message = "Writer analysis unavailable: %s. Keep the draft private; repair the input or run draft.py " \
                  "analyze before accepting the current revision." % error
        result = ({"decision": "block", "reason": message} if event == "Stop" else
                  context(event, message) if event == "PostToolUse" else None)
    if result:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
