"""Check and fixer registries; checks 1, 5, 6."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional, Set

from .issues import Issue, Scope
from .journal import read_text_file
from .markdown import field
from .workspace import KbError

__all__ = ["Issue", "Scope", "CHECKS", "FIXERS", "register_check", "register_fixer", "run_checks",
           "apply_fixes", "is_placeholder", "iter_files", "read_page"]

CHECKS: Dict[int, Callable] = {}
FIXERS: Dict[str, Callable] = {}

STOP_MARKER = "<!-- AGENT-SESSION-STOP -->"


def register_check(number: int, func: Callable) -> Callable:
    CHECKS[number] = func
    return func


LATE_FIXERS: Set[str] = set()
BATCH_FIXERS: Set[str] = set()


def register_fixer(kind: str, func: Callable, late: bool = False, batch: bool = False) -> Callable:
    """late=True: the fixer regenerates data from files and runs after all edits.
    batch=True: the fixer takes the list of all fixes of its kind in one call."""
    FIXERS[kind] = func
    if late:
        LATE_FIXERS.add(kind)
    if batch:
        BATCH_FIXERS.add(kind)
    return func


def run_checks(ws, scope: Scope, only: Optional[Set[int]] = None) -> List[Issue]:
    found: List[Issue] = []
    for number in sorted(CHECKS):
        if only is not None and number not in only:
            continue
        for issue in CHECKS[number](ws, scope):
            if scope.includes(issue.file):
                found.append(issue)
    found.sort(key=lambda i: (i.check, i.file, i.subject))
    return found


def apply_fixes(ws, issues: List[Issue], journal, safe_only: bool, skipped: Optional[Dict[str, str]] = None) -> int:
    """Apply fixes; edits to one file go from the end backwards so offsets stay valid.
    skipped, when given, collects issue key -> reason for fixes that could not be applied."""
    todo = [i for i in issues if i.fix and (i.fix.get("safe") or not safe_only)]
    todo.sort(key=lambda i: (i.fix.get("kind") in LATE_FIXERS, i.fix.get("file", i.file),
                             -int(i.fix.get("start", 0))))
    applied = 0
    batches: Dict[str, List[dict]] = {}
    for i in todo:
        kind = i.fix.get("kind")
        if kind in BATCH_FIXERS:
            batches.setdefault(kind, []).append(i.fix)
            continue
        fixer = FIXERS.get(kind)
        if fixer is None:
            continue
        try:
            fixer(ws, i.fix, journal)
            applied += 1
        except KbError as exc:
            print("skipped %s: %s" % (i.key, exc))
            if skipped is not None:
                skipped[i.key] = str(exc)
    for kind, fixes in batches.items():
        try:
            applied += int(FIXERS[kind](ws, fixes, journal) or 0)
        except KbError as exc:
            print("skipped %d %s fixes: %s" % (len(fixes), kind, exc))
    return applied


def is_placeholder(value: str) -> bool:
    return "<" in value or ">" in value or "..." in value or "*" in value


def iter_files(ws, base_rel: str, suffix: Optional[str] = ".md") -> Iterator[str]:
    base = ws.root / base_rel
    if not base.is_dir():
        return
    for p in sorted(base.rglob("*")):
        if p.is_file() and (suffix is None or p.name.lower().endswith(suffix)):
            yield p.relative_to(ws.root).as_posix()


def read_page(ws, relpath: str) -> Optional[str]:
    try:
        return read_text_file(ws.root / relpath)[0]
    except (KbError, OSError):
        return None


# --- check 1: registry paths ---------------------------------------------------

def check_registry(ws, scope: Scope) -> List[Issue]:
    if not scope.includes("modules.md"):
        return []
    out = []

    def probe(module: str, label: str, value: str):
        if not value or is_placeholder(value):
            return
        if not (ws.root / value.rstrip("/")).exists():
            out.append(Issue(1, "modules.md", "%s %s %s" % (module, label, value), "blocking", module,
                             "modules.md %s `%s` does not exist" % (label, value),
                             "create `%s` or correct the %s entry in modules.md" % (value, label)))

    for m in ws.modules:
        probe(m.name, "path", m.path)
        probe(m.name, "wiki", m.wiki)
        for s in m.sources:
            probe(m.name, "sources", s)
        for e in m.evidence:
            probe(m.name, "evidence", e)
    for e in ws.shared_evidence:
        probe("", "shared evidence", e)
    return out


# --- check 5: session stop marker ---------------------------------------------

def check_session_logs(ws, scope: Scope) -> List[Issue]:
    out = []
    rels = {m.path.rstrip("/") + "/session_state.md" for m in ws.modules if m.path and "<" not in m.path}
    mods = ws.root / "modules"
    if mods.is_dir():
        rels |= {p.relative_to(ws.root).as_posix() for p in mods.glob("*/session_state.md")}
    for rel in sorted(rels):
        p = ws.root / rel
        if not p.is_file() or not scope.includes(rel):
            continue
        text = read_page(ws, rel)
        if text is None or not text.strip():
            continue
        lines = text.splitlines()
        heads = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
        if heads:
            end = heads[1] if len(heads) > 1 else len(lines)
            segment = lines[heads[0]:end]
        else:
            segment = lines
        if not any(ln.strip() == STOP_MARKER for ln in segment):
            module = ws.module_for(rel) or p.parent.name
            out.append(Issue(5, rel, "stop marker", "minor", module,
                             "%s has no `%s` after its first entry" % (rel, STOP_MARKER),
                             "add `%s` on its own line after the first entry" % STOP_MARKER))
    return out


# --- check 6: confidence -------------------------------------------------------

def check_confidence(ws, scope: Scope) -> List[Issue]:
    out = []
    for rel in iter_files(ws, "knowledge-base/modules"):
        parts = rel.split("/")
        if len(parts) < 4 or parts[-1] in ("INDEX.md", "inventory.md") or not scope.includes(rel):
            continue
        text = read_page(ws, rel)
        if text is None or field(text, "confidence") is not None:
            continue
        module = ws.module_for(rel) or parts[2]
        out.append(Issue(6, rel, "confidence", "minor", module,
                         "%s has no `confidence:` line" % rel,
                         "add `confidence: <label>` under the title"))
    return out


register_check(1, check_registry)
register_check(5, check_session_logs)
register_check(6, check_confidence)
