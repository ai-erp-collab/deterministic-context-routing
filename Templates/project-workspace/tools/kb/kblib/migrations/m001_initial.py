"""Migration 001: a pre-integrity workspace (version 0) gets evidence roots, the machine
registry, .kb/ defaults, the extension map, and its legacy [[...]] links converted where safe."""
from __future__ import annotations

import copy
import datetime
import re
from pathlib import Path
from typing import Dict, List, Optional

from .. import checks, doctor, resolve
from ..artifacts import INDEX, REGISTRY, STATUSES, Registry, Row, guess_kind, sha256_file
from ..journal import Journal
from ..workspace import DEFAULT_CONFIG, Workspace, parse_modules
from . import Question

ID = "001"
EXPORT_EXT = {".xlsx", ".xml", ".csv", ".tsv", ".txt"}
UNIMPORTED = "source-artifacts/unimported-rows.md"
BASELINE_ASSET = Path(__file__).resolve().parents[2] / "assets" / "baseline-0.1.json"
LEGACY_READMES = ("source-artifacts/tables/raw/README.md", "source-artifacts/tables/processed/README.md")
LEGACY_MOVE_LINE = "- Example: define how raw artifacts move from raw to processed here."
TRACK_IGNORE_HEADER = (
    "# Evidence tracking exclusions (gitignore-style), relative to the workspace root.\n"
    "# Every file under an `evidence:` root or source-artifacts/ needs a registry row unless listed here.\n"
    "# Lines: pattern | dir/ | !negation | * ** ? globs. The last matching line wins.\n"
)


def legacy_baseline() -> Dict[str, List[str]]:
    """Path -> sha256 values of that file in every 0.1.x template (bytes the project never edited)."""
    try:
        import json
        return json.loads(BASELINE_ASSET.read_bytes().decode("utf-8"))["files"]
    except (OSError, ValueError, KeyError):
        return {}


def unedited_legacy(ws, rel: str) -> bool:
    return sha256_file(ws.root / rel) in legacy_baseline().get(rel, [])


def needs(ws) -> bool:
    return ID not in ws.config.get("migrations_applied", [])


def _modules_without_evidence(ws) -> List[str]:
    return [m.name for m in ws.modules if not m.evidence]


def _candidates(ws, module) -> List[str]:
    out: List[str] = []
    keys = {module.name.casefold()}
    if module.path:
        keys.add(Path(module.path.rstrip("/")).name.casefold())
    sa = ws.root / "source-artifacts"
    if sa.is_dir():
        for kind_dir in sorted(p for p in sa.iterdir() if p.is_dir()):
            raw = kind_dir / "raw"
            if raw.is_dir():
                for d in sorted(p for p in raw.iterdir() if p.is_dir()):
                    if d.name.casefold() in keys:
                        out.append(d.relative_to(ws.root).as_posix() + "/")
    mod_root = ws.root / module.path.rstrip("/") if module.path and "<" not in module.path else None
    if mod_root is not None and mod_root.is_dir():
        for p in sorted(mod_root.rglob("*")):
            if p.is_file() and p.suffix.lower() in EXPORT_EXT:
                folder = p.parent.relative_to(ws.root).as_posix() + "/"
                if folder not in out:
                    out.append(folder)
            if len(out) >= 8:
                break
    return out


def questions(ws) -> List[Question]:
    out = []
    for m in ws.modules:
        if m.evidence:
            continue
        out.append(Question(
            "evidence:%s" % m.name,
            "where does outside material (table exports, library sources, documents) for module %s land?" % m.name,
            _candidates(ws, m),
            "--set-evidence %s=path;path  (or %s= for none)" % (m.name, m.name)))
    return out


# --- modules.md ----------------------------------------------------------------------

def _add_evidence_lines(text: str, evidence: Dict[str, List[str]], shared: Optional[List[str]]) -> str:
    lines = text.split("\n")
    names = {k.casefold(): v for k, v in evidence.items()}
    out: List[str] = []
    k = 0
    while k < len(lines):
        line = lines[k]
        out.append(line)
        m = re.match(r"^-\s+(\S.*?)\s*\r?$", line)
        if m and m.group(1).casefold() in names and not m.group(1).lower().startswith("shared evidence"):
            block = []
            j = k + 1
            while j < len(lines) and re.match(r"^\s+-\s", lines[j]):
                block.append(lines[j])
                j += 1
            out.extend(block)
            paths = names[m.group(1).casefold()]
            if paths and not any(re.match(r"^\s+-\s+evidence\s*:", b) for b in block):
                indent = re.match(r"^(\s+)", block[0]).group(1) if block else "  "
                cr = "\r" if line.endswith("\r") else ""
                out.append("%s- evidence: %s%s" % (indent, ", ".join("`%s`" % p for p in paths), cr))
            k = j
            continue
        k += 1
    result = "\n".join(out)
    if shared and not re.search(r"^(?:-\s+)?shared evidence\s*:", result, re.M | re.I):
        result = result.rstrip("\n") + "\nshared evidence: %s\n" % ", ".join("`%s`" % p for p in shared)
    return result


# --- ledger import -------------------------------------------------------------------

def _cells(line: str) -> List[str]:
    body = line.strip()
    if not (body.startswith("|") and body.endswith("|")):
        return []
    parts = re.split(r"(?<!\\)\|", body[1:-1])
    return [p.strip().replace("\\|", "|") for p in parts]


def _unquote(s: str) -> str:
    return s.strip().strip("`").strip()


def import_ledger(ws, text: str) -> (Dict[str, Row], List[str]):
    rows: Dict[str, Row] = {}
    bad: List[str] = []
    header: Optional[List[str]] = None
    today = datetime.date.today().isoformat()
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = _cells(line)
        if header is None:
            if cells and any(c.casefold() == "artifact" for c in cells):
                header = [c.casefold() for c in cells]
            continue
        if cells and all(re.match(r"^:?-+:?$", c) for c in cells if c):
            continue
        if not cells or len(cells) != len(header):
            bad.append(line.strip())
            continue
        rec = dict(zip(header, cells))
        artifact = _unquote(rec.get("artifact", ""))
        if not artifact or "<" in artifact:
            continue
        status = _unquote(rec.get("status", "raw")).casefold() or "raw"
        if status not in STATUSES:
            bad.append(line.strip())
            continue
        copy_rel = artifact
        if not (ws.root / copy_rel).exists() and (ws.root / "source-artifacts" / artifact).exists():
            copy_rel = "source-artifacts/" + artifact
        pages_cell = rec.get("curated pages", "")
        pages = [_unquote(p) for p in pages_cell.split(",") if _unquote(p) and _unquote(p) not in ("-", "none")]
        notes = rec.get("notes", "").strip()
        notes = "" if notes in ("-",) else notes
        om = re.search(r"origin:\s*`?([^`;|\s]+)`?", notes)
        parts = copy_rel.split("/")
        if parts[0] == "source-artifacts" and len(parts) >= 5 and parts[2] in ("raw", "processed"):
            module, kind = parts[3], parts[1]
        else:
            module, kind = ws.module_for(copy_rel) or "", guess_kind(copy_rel)
        path = ws.root / copy_rel
        digest = sha256_file(path) if path.is_file() else ""
        rows[copy_rel] = Row(copy_rel, om.group(1) if om else None, _unquote(rec.get("module", "")) or module, kind,
                             digest, status, pages, today, notes)
    return rows, bad


# --- apply ------------------------------------------------------------------------------

def apply(ws, answers: dict, journal) -> List[str]:
    out: List[str] = []
    # 1. evidence roots in modules.md
    evidence = answers.get("evidence") or {}
    shared = answers.get("shared_evidence")
    if evidence or shared:
        text = journal.read_text("modules.md")
        new = _add_evidence_lines(text, evidence, shared)
        if new != text:
            journal.write_text("modules.md", new, "m001_evidence")
            out.append("modules.md: evidence roots added")
        ws.modules, ws.shared_evidence = parse_modules(new)
    # 2. ledger -> registry.json, then INDEX.md regenerated
    if not (ws.root / REGISTRY).is_file():
        reg = Registry(ws, {})
        if (ws.root / INDEX).is_file():
            rows, bad = import_ledger(ws, journal.read_text(INDEX))
            reg.rows.update(rows)
            out.append("registry: %d ledger row%s imported" % (len(rows), "" if len(rows) == 1 else "s"))
            if bad:
                body = ["# Unimported ledger rows", "",
                        "These rows of the old `source-artifacts/INDEX.md` could not be read. Register each with",
                        "`kb ingest` or by hand in `registry.json`, then delete this file.", ""]
                body += ["- `%s`" % b.replace("`", "'") for b in bad]
                journal.write_text(UNIMPORTED, "\n".join(body) + "\n", "m001_unimported")
                out.append("registry: %d row%s could not be read; listed in %s"
                           % (len(bad), "" if len(bad) == 1 else "s", UNIMPORTED))
        reg.save(journal, "m001_registry")
    # 3. .kb defaults
    ws.data_dir.mkdir(parents=True, exist_ok=True)
    if not (ws.data_dir / "config.json").is_file():
        ws.config = copy.deepcopy(DEFAULT_CONFIG)
        ws.config["workspace_version"] = 0
        ws.save_config()
    if not (ws.data_dir / "track.ignore").is_file():
        (ws.data_dir / "track.ignore").write_bytes(TRACK_IGNORE_HEADER.encode("utf-8"))
    (ws.data_dir / "profiles").mkdir(exist_ok=True)
    # 3b. 0.1.x table READMEs: files never move now, so their raw/processed wording is stale.
    # Unedited copies (kept in the pre-upgrade snapshot) are deleted; edited ones leave evidence
    # tracking and stay queued (check 16) until their project rules move into AGENTS.md.
    ignore_path = ws.data_dir / "track.ignore"
    for rel in LEGACY_READMES:
        if not (ws.root / rel).is_file():
            continue
        if unedited_legacy(ws, rel):
            journal.delete_file(rel, "m001_legacy_readme")
            out.append("%s: unedited 0.1.x README removed (kept in the pre-upgrade snapshot)" % rel)
            continue
        lines = ignore_path.read_bytes().decode("utf-8").splitlines()
        if rel not in lines:
            ignore_path.write_bytes(("\n".join(lines + [rel]) + "\n").encode("utf-8"))
        out.append("%s: edited by the project; excluded from evidence tracking, queued for review" % rel)
    if (ws.root / "AGENTS.md").is_file():
        text = journal.read_text("AGENTS.md")
        kept = [ln for ln in text.split("\n") if ln.rstrip("\r") != LEGACY_MOVE_LINE]
        if len(kept) != len(text.split("\n")):
            journal.write_text("AGENTS.md", "\n".join(kept), "m001_legacy_move_line")
            out.append("AGENTS.md: template example about moving raw to processed removed")
    # 4. environment probe and extension map
    tiers, mapped, unknown = doctor.run_doctor(ws)
    out.append("doctor: %d extension%s mapped, %d unknown" % (len(mapped), "" if len(mapped) == 1 else "s", len(unknown)))
    # 5. legacy links: dry run shown, then safe conversions (checks 3 and 15 only)
    found = checks.run_checks(ws, checks.Scope(None), {3, 15})
    for i in found:
        if i.check == 3:
            out.append("link %s: %s" % ("convert" if i.fix and i.fix.get("safe") else "left as issue", i.symptom))
    applied = checks.apply_fixes(ws, found, journal, safe_only=True)
    out.append("safe fixes applied: %d" % applied)
    return out
