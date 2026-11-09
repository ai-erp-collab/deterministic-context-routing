"""Migration 002: workspace skills move to the cross-agent `.agents/skills/` folder.

The project-owned `skills/cross-module-owner-api/` is moved there; the shipped `kb` copies in
`skills/kb/` and `.codex/skills/kb/` are removed when unedited (the files step already wrote
`.agents/skills/kb/`). Edited files and files whose target already exists are kept and reported."""
from __future__ import annotations

import hashlib
import json
import re
from typing import List

from . import Question

ID = "002"
TARGET = ".agents/skills"
OWNER_API = "skills/cross-module-owner-api"
LEGACY_KB = ("skills/kb", ".codex/skills/kb")
EMPTY_ROOTS = ("skills", ".codex/skills")
RULE_FILES = ("AGENTS.md", "CLAUDE.md", "README.md", "ASSEMBLY.md")
LINK = re.compile(r"(?<![\w./])(\./)?(?:\.codex/)?skills/(kb|cross-module-owner-api)/")


def _files(ws, base: str) -> List[str]:
    root = ws.root / base
    if not root.is_dir():
        return []
    return sorted(p.relative_to(ws.root).as_posix() for p in root.rglob("*") if p.is_file())


def _sha(ws, rel: str) -> str:
    return hashlib.sha256((ws.root / rel).read_bytes()).hexdigest()


def needs(ws) -> bool:
    if ID in ws.config.get("migrations_applied", []):
        return False  # files it kept are reported by check 16, not re-planned on every upgrade
    return any(_files(ws, base) for base in (OWNER_API,) + LEGACY_KB)


def questions(ws) -> List[Question]:
    return []


def _manifest(ws) -> dict:
    path = ws.data_dir / "manifest.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_bytes().decode("utf-8-sig"))
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def apply(ws, answers: dict, journal) -> List[str]:
    moved, removed, kept = 0, [], []
    # 1. project-owned owner-api skill: move file by file, never over an existing target
    for rel in _files(ws, OWNER_API):
        dest = TARGET + "/" + rel[len("skills/"):]
        if not (ws.root / dest).is_file():
            journal.copy_file(ws.root / rel, dest, "m002_move")
            journal.delete_file(rel, "m002_move")
            moved += 1
        elif _sha(ws, dest) == _sha(ws, rel):
            journal.delete_file(rel, "m002_duplicate")
            removed.append(rel)
        else:
            kept.append(rel)
    # 2. shipped kb copies: remove the unedited ones
    manifest = _manifest(ws)
    for base in LEGACY_KB:
        for rel in _files(ws, base):
            shipped = TARGET + "/kb/" + rel[len(base) + 1:]
            if rel.endswith(".new"):  # an old pending merge; .agents/skills/kb/ holds the shipped version
                journal.delete_file(rel, "m002_remove_legacy")
                removed.append(rel)
                continue
            sha = _sha(ws, rel)
            if sha == manifest.get(rel) or ((ws.root / shipped).is_file() and sha == _sha(ws, shipped)):
                journal.delete_file(rel, "m002_remove_legacy")
                removed.append(rel)
            else:
                kept.append(rel)
    if removed and manifest and not journal.dry_run:
        for rel in removed:
            manifest.pop(rel, None)
        (ws.data_dir / "manifest.json").write_bytes(
            (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode("utf-8"))
    # 3. empty folders left behind (never .codex/ itself); best effort: a folder held open
    # by Explorer or antivirus stays behind instead of stopping the upgrade
    if not journal.dry_run:
        for base in EMPTY_ROOTS:
            root = ws.root / base
            if not root.is_dir():
                continue
            dirs = sorted((p for p in root.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True)
            for d in dirs + [root]:
                try:
                    if not any(d.iterdir()):
                        d.rmdir()
                except OSError:
                    pass
    # 4. rule-file links
    for name in RULE_FILES:
        if not journal.exists(name):
            continue
        text = journal.read_text(name)
        new = LINK.sub(lambda m: (m.group(1) or "") + TARGET + "/" + m.group(2) + "/", text)
        if new != text:
            journal.write_text(name, new, "m002_links")
    out = ["moved %d file(s) to %s/" % (moved, TARGET),
           "removed %d unedited legacy skill file(s)" % len(removed)]
    for rel in kept:
        if rel.startswith(OWNER_API + "/"):
            why, skill = "a different copy already exists in %s/" % TARGET, "cross-module-owner-api"
        else:
            why, skill = "edited by the project", "kb"
        out.append("kept %s: %s; merge into %s/%s/ and delete it" % (rel, why, TARGET, skill))
    return out
