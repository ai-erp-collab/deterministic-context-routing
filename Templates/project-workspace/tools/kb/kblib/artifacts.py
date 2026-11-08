"""Evidence registry, ignore rules, ingest, INDEX.md, checks 9, 10, 11, 13."""
from __future__ import annotations

import datetime
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .checks import is_placeholder, iter_files, read_page, register_check, register_fixer
from .issues import Issue, Scope
from .workspace import KbError

ARTIFACTS = "source-artifacts"
REGISTRY = ARTIFACTS + "/registry.json"
INDEX = ARTIFACTS + "/INDEX.md"
KINDS = ("tables", "docs", "specs", "code")
STATUSES = ("raw", "processed", "reference", "ignored")
TABLE_EXT = {".xlsx", ".xls", ".xml", ".csv", ".tsv", ".txt"}
CODE_EXT = {".cs", ".java", ".kt", ".kts", ".go", ".js", ".jsx", ".mjs", ".ts", ".tsx", ".c", ".h", ".cpp",
            ".hpp", ".cc", ".php", ".swift", ".rs", ".scala", ".dart", ".py", ".sql", ".vb", ".pas", ".bsl"}
MOJIBAKE_RE = re.compile("[\u00c0-\u00ff][\u0080-\u00bf]")
RAW_RE = re.compile(r"^source-artifacts/[^/]+/raw/")


@dataclass
class Row:
    copy: str
    origin: Optional[str]
    module: str
    kind: str
    sha256: str
    status: str = "raw"
    pages: List[str] = field(default_factory=list)
    first_seen: str = ""
    notes: str = ""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(str(path), "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Registry:
    def __init__(self, ws, rows: Dict[str, Row]):
        self.ws = ws
        self.rows = rows

    @classmethod
    def load(cls, ws, journal=None) -> "Registry":
        text = None
        if journal is not None and journal.exists(REGISTRY):
            text = journal.read_text(REGISTRY)
        elif (ws.root / REGISTRY).is_file():
            text = (ws.root / REGISTRY).read_bytes().decode("utf-8-sig")
        rows: Dict[str, Row] = {}
        if text:
            try:
                data = json.loads(text)
            except ValueError as exc:
                raise KbError("%s is not valid JSON: %s" % (REGISTRY, exc))
            for item in data.get("rows", []):
                known = {k: item[k] for k in Row.__dataclass_fields__ if k in item}
                row = Row(**known)
                rows[row.copy] = row
        return cls(ws, rows)

    def to_text(self) -> str:
        data = {"version": 1, "rows": [asdict(self.rows[k]) for k in sorted(self.rows)]}
        return json.dumps(data, indent=1, ensure_ascii=False) + "\n"

    def save(self, journal, rule: str) -> None:
        journal.write_text(REGISTRY, self.to_text(), rule)
        journal.write_text(INDEX, render_index(self.ws, self), rule)


def _cell(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def render_index(ws, reg: Registry) -> str:
    lines = INDEX_HEAD[:]
    for k in sorted(reg.rows):
        r = reg.rows[k]
        pages = ", ".join("`%s`" % p for p in r.pages) if r.pages else "-"
        lines.append("| `%s` | %s | %s | %s | %s |" % (r.copy, r.status, _cell(r.module or "-"), pages,
                                                      _cell(r.notes) if r.notes else "-"))
    lines.append("")
    return "\n".join(lines)


INDEX_HEAD = [
    "# Source Artifacts",
    "",
    "Evidence copied into the workspace. `kb ingest` copies each file to `<kind>/raw/<module>/` and records its",
    "origin and hash in `registry.json`; this file is generated from that registry by `tools/kb/kb.py`.",
    "",
    "- Do not rewrite raw files unless the project has an explicit normalization rule.",
    "- A file is processed once a curated page names it in its `source:` line; `kb fix --safe` then sets the",
    "  status. Files never move between folders, so links to them stay valid.",
    "",
    "| Artifact | Status | Module | Curated pages | Notes |",
    "| --- | --- | --- | --- | --- |",
]


# --- ignore rules ------------------------------------------------------------

def _glob_to_regex(pat: str) -> str:
    out = []
    i = 0
    while i < len(pat):
        if pat.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pat.startswith("/**", i) and i + 3 == len(pat):
            out.append("/.*")
            i += 3
        elif pat.startswith("**", i):
            out.append(".*")
            i += 2
        elif pat[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pat[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pat[i]))
            i += 1
    return "".join(out)


class IgnoreRules:
    def __init__(self, rules: List[tuple]):
        self.rules = rules  # (regex, negate, dir_only)

    @classmethod
    def load(cls, ws) -> "IgnoreRules":
        p = ws.data_dir / "track.ignore"
        rules = []
        if p.is_file():
            for raw in p.read_bytes().decode("utf-8-sig", errors="replace").splitlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                neg = line.startswith("!")
                if neg:
                    line = line[1:]
                dir_only = line.endswith("/")
                line = line.strip("/") if dir_only else line
                anchored = "/" in line
                line = line.lstrip("/")
                body = _glob_to_regex(line)
                rx = re.compile(("^" if anchored else "^(?:.*/)?") + body + "$")
                rules.append((rx, neg, dir_only))
        return cls(rules)

    def match(self, relpath: str) -> bool:
        parts = relpath.split("/")
        dirs = ["/".join(parts[:i]) for i in range(1, len(parts))]
        state = False
        for rx, neg, dir_only in self.rules:
            cands = dirs if dir_only else dirs + [relpath]
            if any(rx.match(c) for c in cands):
                state = not neg
        return state


def _roots(ws) -> List[str]:
    roots = []
    for m in ws.modules:
        roots += m.evidence
    roots += ws.shared_evidence
    roots.append(ARTIFACTS)
    out = []
    for r in roots:
        r = r.replace("\\", "/").strip("/")
        if r and not is_placeholder(r) and r not in out:
            out.append(r)
    return out


def tracked_files(ws) -> List[str]:
    rules = IgnoreRules.load(ws)
    out = set()
    for root in _roots(ws):
        for rel in iter_files(ws, root, None):
            if rel in (REGISTRY, INDEX):
                continue
            if not rules.match(rel):
                out.add(rel)
    return sorted(out)


def guess_kind(name: str) -> str:
    ext = Path(name).suffix.lower()
    if ext in TABLE_EXT:
        return "tables"
    if ext in CODE_EXT:
        return "code"
    return "docs"


def _row_for(ws, rel: str) -> Row:
    parts = rel.split("/")
    if parts[0] == ARTIFACTS and len(parts) >= 5 and parts[2] in ("raw", "processed"):
        module, kind, origin = parts[3], parts[1], None
    else:
        module, kind, origin = ws.module_for(rel) or "", guess_kind(rel), rel
    return Row(rel, origin, module, kind, sha256_file(ws.root / rel), "raw", [],
               datetime.date.today().isoformat(), "")


def _module_name(ws, module: str) -> str:
    for m in ws.modules:
        if m.name.casefold() == module.casefold():
            return m.name
    raise KbError("unknown module `%s`; modules.md lists: %s" % (module, ", ".join(m.name for m in ws.modules) or "none"))


def _source_path(ws, p: str) -> Path:
    cand = Path(p)
    if cand.is_absolute():
        return cand
    if cand.exists():
        return cand.resolve()
    return (ws.root / p).resolve()


def ingest(ws, paths: List[str], module: str, kind: Optional[str], journal) -> List[Row]:
    module = _module_name(ws, module)
    if kind is not None and kind not in KINDS:
        raise KbError("--kind must be one of %s" % ", ".join(KINDS))
    reg = Registry.load(ws, journal)
    rows = []
    sources = []
    for p in paths:  # a folder stands for every file under it
        src = _source_path(ws, p)
        if src.is_dir():
            sources += sorted(f for f in src.rglob("*") if f.is_file())
        elif src.is_file():
            sources.append(src)
        else:
            raise KbError("%s is not a file or folder" % p)
    for src in sources:
        k = kind or guess_kind(src.name)
        digest = sha256_file(src)
        try:
            origin = src.relative_to(ws.root).as_posix()
        except ValueError:
            origin = src.as_posix()
        for row in reg.rows.values():  # rows tracking this file in place get its new hash
            if row.copy == origin and row.origin == origin:
                row.sha256 = digest
        previous = [r for r in reg.rows.values() if r.origin == origin and r.copy != origin]
        if previous:
            # a new version of an ingested file replaces its registered copy (journaled; undo restores it)
            row = previous[0]
            if not (ws.root / row.copy).is_file() or sha256_file(ws.root / row.copy) != digest:
                journal.copy_file(src, row.copy, "ingest_refresh", overwrite=True)
            row.sha256 = digest
            rows.append(row)
            continue
        folder = "%s/%s/raw/%s" % (ARTIFACTS, k, module)
        stem, ext = src.stem, src.suffix
        n = 1
        while True:
            name = src.name if n == 1 else "%s-%d%s" % (stem, n, ext)
            rel = folder + "/" + name
            dest = ws.root / rel
            if not dest.exists() and not journal.exists(rel):
                journal.copy_file(src, rel, "ingest")
                break
            if dest.is_file() and sha256_file(dest) == digest:
                break  # identical copy already present
            n += 1
        row = reg.rows.get(rel) or Row(rel, origin, module, k, digest, "raw", [], datetime.date.today().isoformat(), "")
        row.origin = origin
        reg.rows[rel] = row
        rows.append(row)
    reg.save(journal, "ingest")
    return rows


# --- check 9: completeness -------------------------------------------------------

def check_untracked(ws, scope: Scope) -> List[Issue]:
    reg = Registry.load(ws)
    origins = {r.origin for r in reg.rows.values() if r.origin}
    out = []
    for rel in tracked_files(ws):
        if rel in reg.rows or rel in origins or not scope.includes(rel):
            continue
        out.append(Issue(9, rel, "registry row", "blocking", ws.module_for(rel) or "",
                         "evidence file `%s` has no registry row" % rel,
                         "add it to the registry as `raw` (`kb fix --safe`), or exclude it in `.kb/track.ignore`",
                         {"kind": "add_registry_row", "safe": True, "path": rel}))
    return out


def fix_add_registry_rows(ws, fixes: List[dict], journal) -> int:
    """All missing rows of a run in one registry load and one save."""
    reg = Registry.load(ws, journal)
    added = 0
    for fix in fixes:
        rel = fix["path"]
        if rel in reg.rows or not (ws.root / rel).is_file():
            continue
        reg.rows[rel] = _row_for(ws, rel)
        added += 1
    if added:
        reg.save(journal, "add_registry_row")
    return added


# --- check 10: freshness ---------------------------------------------------------

def _origin_path(ws, origin: str) -> Path:
    p = Path(origin)
    return p if p.is_absolute() else ws.root / origin


def check_freshness(ws, scope: Scope) -> List[Issue]:
    reg = Registry.load(ws)
    out = []
    for key in sorted(reg.rows):
        r = reg.rows[key]
        if not (scope.includes(r.copy) or (r.origin and scope.includes(r.origin))):
            continue
        copy = ws.root / r.copy
        if not copy.is_file():
            out.append(Issue(10, r.copy, "copy missing", "minor", r.module,
                             "registered copy `%s` is missing" % r.copy,
                             "restore the copy, or re-ingest from its origin"))
            continue
        if r.origin:
            op = _origin_path(ws, r.origin)
            if op.is_file() and sha256_file(op) != r.sha256:
                out.append(Issue(10, r.copy, "origin changed", "minor", r.module,
                                 "a new version arrived: origin `%s` differs from registered `%s`" % (r.origin, r.copy),
                                 "re-ingest the origin and refresh the curated pages"))
    return out


# --- check 11: processed rule ----------------------------------------------------

def check_processed(ws, scope: Scope) -> List[Issue]:
    reg = Registry.load(ws)
    out = []
    for key in sorted(reg.rows):
        r = reg.rows[key]
        if r.status != "processed" or not scope.includes(r.copy):
            continue
        if any((ws.root / p).is_file() for p in r.pages):
            continue
        out.append(Issue(11, r.copy, "processed without page", "minor", r.module,
                         "`%s` is marked processed but none of its curated pages exists" % r.copy,
                         "write or link the curated page, or set the status back to raw"))
    return out


# --- check 13: encoding ----------------------------------------------------------

def _encoding_targets(ws, scope: Scope) -> List[str]:
    def in_roots(rel: str) -> bool:
        return rel.startswith(("knowledge-base/", "modules/")) or "/" not in rel

    if scope.changed is not None:
        rels = [r for r in sorted(scope.changed) if r.lower().endswith(".md") and in_roots(r)
                and (ws.root / r).is_file()]
    else:
        rels = list(iter_files(ws, "knowledge-base")) + list(iter_files(ws, "modules"))
        rels += sorted(p.name for p in ws.root.glob("*.md") if p.is_file())
    return [r for r in rels if not RAW_RE.match(r)]


def _as_byte(ch: str) -> Optional[int]:
    """The single byte a legacy code page (latin-1 or cp1252) would have shown as ch."""
    if ord(ch) < 256:
        return ord(ch)
    try:
        b = ch.encode("cp1252")
    except UnicodeEncodeError:
        return None
    return b[0] if len(b) == 1 else None


def mojibake_at(text: str) -> Optional[int]:
    """Offset of UTF-8 text that was decoded as a single-byte code page, or None.
    Flags only runs that turn back into valid non-ASCII UTF-8; plain accented text passes."""
    for m in MOJIBAKE_RE.finditer(text):
        lead = ord(m.group(0)[0])
        size = 2 if lead < 0xE0 else 3 if lead < 0xF0 else 4
        chunk = text[m.start():m.start() + size]
        raw = [_as_byte(c) for c in chunk]
        if len(chunk) < size or None in raw:
            continue
        try:
            bytes(raw).decode("utf-8")
        except UnicodeDecodeError:
            continue
        return m.start()
    return None


def check_encoding(ws, scope: Scope) -> List[Issue]:
    out = []
    for rel in _encoding_targets(ws, scope):
        data = (ws.root / rel).read_bytes()
        reason = None
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            reason = "is not valid UTF-8 (byte %d)" % exc.start
        else:
            if "\ufffd" in text:
                reason = "contains U+FFFD replacement characters"
            else:
                pos = mojibake_at(text)
                if pos is not None:
                    line = text.count("\n", 0, pos) + 1
                    reason = "looks double-encoded (mojibake) at line %d" % line
        if reason:
            out.append(Issue(13, rel, "encoding", "blocking", ws.module_for(rel) or "",
                             "`%s` %s" % (rel, reason),
                             "restore the text from its source with the right encoding"))
    return out


# --- check 17: processing backlog -------------------------------------------------

def pages_by_source(ws) -> Dict[str, List[str]]:
    """Registered copy path -> KB pages whose `source:` names it exactly (no name matching)."""
    from .resolve import load_index
    out: Dict[str, List[str]] = {}
    index = load_index(ws)
    if index is not None:
        items = [(rel, e.get("source", "")) for rel, e in index["pages"].items()]
    else:
        from .links import _kb_pages
        from .markdown import field as _field
        items = []
        for rel in _kb_pages(ws, Scope(None)):
            text = read_page(ws, rel) or ""
            items.append((rel, (_field(text, "source") or "").strip().strip("`").strip()))
    for rel, src in items:
        if src:
            out.setdefault(src, []).append(rel)
    return out


def check_backlog(ws, scope: Scope) -> List[Issue]:
    reg = Registry.load(ws)
    raw = [r for k, r in sorted(reg.rows.items()) if r.status == "raw" and scope.includes(r.copy)]
    if not raw:
        return []
    sources = pages_by_source(ws)
    out = []
    for r in raw:
        pages = sorted(p for p in sources.get(r.copy, []) if (ws.root / p).is_file())
        if pages:
            out.append(Issue(17, r.copy, "processing", "minor", r.module,
                             "`%s` is still `raw` although %s name%s it in `source:`"
                             % (r.copy, ", ".join("`%s`" % p for p in pages), "s" if len(pages) == 1 else ""),
                             "mark it processed (`kb fix --safe`)",
                             {"kind": "mark_processed", "safe": True, "copy": r.copy, "pages": pages}))
            continue
        if r.kind == "tables":
            how = "parse it: `kb table %s --module %s` (exit 3 = new layout: `kb table learn`)" % (r.copy, r.module or "<M>")
        else:
            how = "curate a page from it and put `source: %s` in that page" % r.copy
        out.append(Issue(17, r.copy, "processing", "minor", r.module,
                         "`%s` is waiting to be processed: no page names it in `source:`" % r.copy, how))
    return out


def fix_mark_processed(ws, fixes: List[dict], journal) -> int:
    reg = Registry.load(ws, journal)
    changed = 0
    for fix in fixes:
        row = reg.rows.get(fix["copy"])
        if row is None or row.status != "raw":
            continue
        row.status = "processed"
        row.pages = sorted(set(row.pages) | set(fix["pages"]))
        changed += 1
    if changed:
        reg.save(journal, "mark_processed")
    return changed


def mark_processed(ws, copy: str, pages: List[str], journal) -> bool:
    """Used by `kb table`: the export it just turned into pages is processed."""
    return fix_mark_processed(ws, [{"copy": copy, "pages": pages}], journal) > 0


register_check(9, check_untracked)
register_check(17, check_backlog)
register_fixer("mark_processed", fix_mark_processed, batch=True)
register_check(10, check_freshness)
register_check(11, check_processed)
register_check(13, check_encoding)
register_fixer("add_registry_row", fix_add_registry_rows, batch=True)
