"""Issue model, dated reports, OPEN.md, issues.json, known_issues.md pointer."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set

from .journal import read_text_file, write_text_preserving
from .workspace import CHECKS_GITIGNORE, ensure_dir


@dataclass
class Issue:
    check: int
    file: str
    subject: str
    severity: str  # 'blocking' | 'minor'
    module: str
    symptom: str
    proposed_fix: str
    fix: Optional[dict] = None

    @property
    def key(self) -> str:
        return "%s | %s | %s" % (self.check, self.file, self.subject)


class Scope:
    def __init__(self, changed: Optional[Set[str]] = None):
        self.changed = None if changed is None else set(changed)

    def includes(self, relpath: str) -> bool:
        return self.changed is None or relpath in self.changed


def summary_line(command: str, issues: List[Issue]) -> str:
    n = len(issues)
    b = sum(1 for i in issues if i.severity == "blocking")
    return "kb %s: %d issue%s (%d blocking)" % (command, n, "" if n == 1 else "s", b)


def issue_line(i: Issue) -> str:
    return "[%s] %s: %s" % (i.severity, i.file, i.symptom)


def _cell(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def load_state(ws) -> dict:
    p = ws.data_dir / "issues.json"
    if p.is_file():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("next_id", 1)
                data.setdefault("open", [])
                return data
        except ValueError:
            pass
    next_id = 1
    open_md = ws.root / "docs" / "checks" / "OPEN.md"
    if open_md.is_file():
        m = re.search(r"^next-id:\s*(\d+)", open_md.read_text(encoding="utf-8", errors="replace"), re.M)
        if m:
            next_id = int(m.group(1))
    return {"next_id": next_id, "open": []}


def save_state(ws, state: dict) -> None:
    ws.make_data_dir()
    write_lf(ws.data_dir / "issues.json", json.dumps(state, indent=1, ensure_ascii=False) + "\n")


def write_lf(path: Path, text: str) -> None:
    """Write a generated file as UTF-8 with LF newlines on every OS."""
    path.write_bytes(text.encode("utf-8"))


def _report_path(checks_dir: Path, today: str) -> Path:
    p = checks_dir / ("%s-check.md" % today)
    n = 2
    while p.exists():
        p = checks_dir / ("%s-check-%d.md" % (today, n))
        n += 1
    return p


def write_reports(ws, issues: List[Issue], today: str) -> Path:
    state = load_state(ws)
    prev = {row["key"]: row for row in state["open"]}
    checks_dir = ws.root / "docs" / "checks"
    ensure_dir(checks_dir, CHECKS_GITIGNORE)
    report = _report_path(checks_dir, today)
    rows = []
    seen = set()
    for i in issues:
        if i.key in seen:
            continue
        seen.add(i.key)
        old = prev.get(i.key)
        if old:
            iid, rep = old["id"], old.get("report", report.name)
        else:
            iid, rep = state["next_id"], report.name
            state["next_id"] += 1
        rows.append({"id": iid, "key": i.key, "check": i.check, "file": i.file, "subject": i.subject,
                     "severity": i.severity, "module": i.module, "symptom": i.symptom,
                     "proposed_fix": i.proposed_fix, "fix": i.fix, "report": rep})
    rows.sort(key=lambda r: r["id"])
    resolved = [r for k, r in prev.items() if k not in seen]
    resolved.sort(key=lambda r: r["id"])

    lines = ["# Workspace check %s" % today, "", "## Open", ""]
    if rows:
        lines += ["| id | severity | module | symptom | proposed fix |", "|---|---|---|---|---|"]
        lines += ["| %d | %s | %s | %s | %s |" % (r["id"], r["severity"], _cell(r["module"] or "-"),
                                                  _cell(r["symptom"]), _cell(r["proposed_fix"])) for r in rows]
    else:
        lines.append("none")
    lines += ["", "## Resolved since last run", ""]
    if resolved:
        lines += ["| id | symptom |", "|---|---|"]
        lines += ["| %d | %s |" % (r["id"], _cell(r["symptom"])) for r in resolved]
    else:
        lines.append("none")
    write_lf(report, "\n".join(lines) + "\n")

    open_lines = ["# Open workspace issues", "", "next-id: %d" % state["next_id"], ""]
    if rows:
        open_lines += ["| id | severity | module | symptom | proposed fix | report |", "|---|---|---|---|---|---|"]
        open_lines += ["| %d | %s | %s | %s | %s | %s |" % (r["id"], r["severity"], _cell(r["module"] or "-"),
                                                            _cell(r["symptom"]), _cell(r["proposed_fix"]),
                                                            r["report"]) for r in rows]
    else:
        open_lines.append("No open issues.")
    write_lf(checks_dir / "OPEN.md", "\n".join(open_lines) + "\n")

    state["open"] = rows
    save_state(ws, state)
    update_pointer(ws, rows)
    return report


def pointer_text(rows: List[dict]) -> Optional[str]:
    if not rows:
        return None
    n = len(rows)
    blocking = [r for r in rows if r["severity"] == "blocking"]
    mods = sorted({r["module"] for r in blocking if r["module"]})
    detail = "%d blocking" % len(blocking)
    if len(mods) == 1:
        detail += ": module `%s`" % mods[0]
    elif mods:
        detail += ": modules " + ", ".join("`%s`" % m for m in mods)
    return ("- Workspace health: %d open issue%s (%s).\n"
            "  Before work in a listed module, warn the user. To review or fix:\n"
            "  read docs/checks/OPEN.md.\n") % (n, "" if n == 1 else "s", detail)


_HEALTH = "## Workspace Health"


def update_pointer(ws, rows: List[dict]) -> None:
    path = ws.root / "known_issues.md"
    bullet = pointer_text(rows)
    if path.is_file():
        text, _bom, crlf = read_text_file(path)
    elif bullet is None:
        return
    else:
        text, crlf = "# Known Issues\n", False
    nl = "\r\n" if crlf else "\n"
    lines = text.splitlines(True)
    start = None
    for idx, ln in enumerate(lines):
        if ln.rstrip("\r\n") == _HEALTH:
            start = idx
            break
    if start is not None:
        end = start + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        before, after = lines[:start], lines[end:]
    else:
        before, after = lines, []
    if bullet is None:
        if start is None:
            return
        # drop the section and the blank line that separated it
        while before and not before[-1].strip() and not after:
            before.pop()
        new = "".join(before) + "".join(after)
        if not after and before:
            new = new.rstrip("\r\n") + nl
    else:
        section = _HEALTH + nl + nl + bullet.replace("\n", nl)
        head = "".join(before)
        if head and not head.endswith(("\n",)):
            head += nl
        if start is None and head.strip():
            if not head.endswith(nl + nl) and not head.endswith("\n\n"):
                head += nl
        if after:
            section += nl
        new = head + section + "".join(after)
    write_text_preserving(path, new)
