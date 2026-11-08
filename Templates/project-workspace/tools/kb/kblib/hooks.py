"""Hook entry points for agent harnesses: post-write, stop, session-start.

Each reads the harness's JSON payload from stdin (missing or invalid = empty)
and prints nothing when there is nothing to report.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, List

from . import checks, resolve
from .issues import issue_line, load_state, summary_line
from .journal import Journal
from .markdown import field
from .workspace import CURRENT_VERSION

SKILL_HINT = "Use the kb skill to resolve them."


def read_payload(stream) -> dict:
    try:
        if stream is None or (hasattr(stream, "isatty") and stream.isatty()):
            return {}
        buffer = getattr(stream, "buffer", None)
        # Harness payloads are UTF-8 JSON; the text layer would decode them in the console code page.
        raw = buffer.read().decode("utf-8-sig") if buffer is not None else stream.read().lstrip("﻿")
    except (OSError, ValueError):
        return {}
    if not raw or not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


PATCH_HEADER = re.compile(r"^\*\*\* (?:(?:Add|Update|Delete) File|Move to): (.+?)\s*$", re.M)


def _patch_paths(text: str, out: List[str]) -> None:
    """Paths named by apply_patch headers (Codex sends the patch text as a string)."""
    if "*** " in text:
        out.extend(m.group(1) for m in PATCH_HEADER.finditer(text))


def _collect(obj, out: List[str]) -> None:
    if isinstance(obj, dict):
        for key in ("file_path", "path"):
            v = obj.get(key)
            if isinstance(v, str) and v:
                out.append(v)
        for key, v in obj.items():
            if isinstance(v, (dict, list)):
                _collect(v, out)
            elif isinstance(v, str) and key not in ("file_path", "path"):
                _patch_paths(v, out)
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, str):
                _patch_paths(v, out)
            else:
                _collect(v, out)


def payload_paths(payload: dict) -> List[str]:
    out: List[str] = []
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, (dict, list)):
        _collect(tool_input, out)
    seen, uniq = set(), []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def _relative(ws, p: str):
    path = Path(p)
    if not path.is_absolute():
        path = ws.root / path
    try:
        return path.resolve().relative_to(ws.root).as_posix()
    except (ValueError, OSError):
        return None


def watched_roots(ws) -> List[str]:
    roots = ["knowledge-base/", "source-artifacts/"]
    for m in ws.modules:
        roots += [e.rstrip("/") + "/" for e in m.evidence if "<" not in e]
    roots += [e.rstrip("/") + "/" for e in ws.shared_evidence if "<" not in e]
    return roots


def relevant(ws, rel: str) -> bool:
    return rel == "modules.md" or rel.startswith(tuple(watched_roots(ws)))


def _remember(ws, rels: Iterable[str]) -> None:
    state = ws.read_state()
    changed = list(state.get("session_changed", []))
    for r in rels:
        if r not in changed:
            changed.append(r)
    state["session_changed"] = changed
    ws.write_state(state)


def _page_sources(ws, rels: List[str]) -> List[str]:
    """`source:` values of the written KB pages: check 17 can then mark those copies processed."""
    out = []
    for rel in rels:
        if rel.startswith("knowledge-base/") and rel.lower().endswith(".md"):
            value = field(checks.read_page(ws, rel) or "", "source")
            value = (value or "").strip().strip("`").strip()
            if value and value not in out:
                out.append(value)
    return out


def post_write(ws, payload: dict) -> List[str]:
    rels = []
    for p in payload_paths(payload):
        rel = _relative(ws, p)
        if rel and relevant(ws, rel):
            rels.append(rel)
    if not rels:
        return []
    _remember(ws, rels)
    rels += [s for s in _page_sources(ws, rels) if s not in rels]
    scope = checks.Scope(set(rels))
    journal = Journal(ws)
    journal.start_run("hook post-write")
    first = checks.run_checks(ws, scope)
    checks.apply_fixes(ws, first, journal, safe_only=True)
    touched = {e[0] for e in journal.edits}
    resolve.build_index(ws, set(rels) | touched)
    if journal.edits:
        issues = checks.run_checks(ws, checks.Scope(set(rels) | touched))
    else:  # nothing edited: the first run stands, except the index issues build_index just settled
        issues = [i for i in first if i.check != 15]
    ids = open_ids(ws)
    lines = [summary_line("check", issues)] + [_with_id(i, ids) for i in issues] + [SKILL_HINT] if issues else []
    if journal.edits:
        n = len(journal.edits)
        lines.append("kb fix: %d edit%s applied, run_id: %s (undo with kb undo %s)"
                     % (n, "" if n == 1 else "s", journal.run_id, journal.run_id))
        lines += ["%s: %s -> %s" % e for e in journal.edits]
    return lines


def stop(ws, payload: dict) -> List[str]:
    state = ws.read_state()
    changed = list(state.get("session_changed", []))
    if not changed:
        return []
    issues = checks.run_checks(ws, checks.Scope(set(changed)))
    known = set()
    if (ws.data_dir / "issues.json").is_file():
        known = {stable_key(r["key"]) for r in load_state(ws)["open"]}
    introduced = [i for i in issues if i.severity == "blocking" and stable_key(i.key) not in known]
    if introduced and payload.get("stop_hook_active") is not True:
        reason = " ".join([summary_line("check", introduced)] + [issue_line(i) for i in introduced] + [SKILL_HINT])
        return [json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False)]
    state["session_changed"] = []
    ws.write_state(state)
    return []  # minor or old issues: left to the next kb check and the session-start line


def open_ids(ws) -> dict:
    """stable key -> id of issues already in the queue (ids are given only by a full kb check)."""
    if not (ws.data_dir / "issues.json").is_file():
        return {}
    return {stable_key(r["key"]): r["id"] for r in load_state(ws)["open"] if "id" in r}


def _with_id(issue, ids: dict) -> str:
    iid = ids.get(stable_key(issue.key))
    return issue_line(issue) + (" (#%d)" % iid if iid is not None else "")


def stable_key(key: str) -> str:
    """Issue key without line numbers, so an issue that only moved is not 'new'."""
    return re.sub(r" line \d+", "", key)


def workspace_version(ws) -> int:
    if not (ws.data_dir / "config.json").is_file():
        return 0
    try:
        return int(ws.config.get("workspace_version", 0))
    except (TypeError, ValueError):
        return 0


def session_start(ws, payload: dict) -> List[str]:
    lines = []
    rows = load_state(ws)["open"] if (ws.data_dir / "issues.json").is_file() else []
    if rows:
        b = sum(1 for r in rows if r.get("severity") == "blocking")
        lines.append("KB: %d open issue%s (%d blocking). See docs/checks/OPEN.md."
                     % (len(rows), "" if len(rows) == 1 else "s", b))
    version = workspace_version(ws)
    if version < CURRENT_VERSION:
        lines.append("KB: workspace version %d < %d. Run kb upgrade --dry-run." % (version, CURRENT_VERSION))
    return lines


def render(event: str, lines: List[str]) -> str:
    """Exact stdout for a hook event; "" when there is nothing to say.

    post-write: one JSON object with hookSpecificOutput.additionalContext.
    stop: the block decision JSON (already a single line) or nothing.
    session-start: plain lines.
    """
    if not lines:
        return ""
    if event == "post-write":
        return json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                  "additionalContext": "\n".join(lines)}}, ensure_ascii=False)
    return "\n".join(lines)


EVENTS = {"post-write": post_write, "stop": stop, "session-start": session_start}
