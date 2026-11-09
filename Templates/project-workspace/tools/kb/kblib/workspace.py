"""Workspace root detection, modules.md parsing, configuration."""
from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

CURRENT_VERSION = 1

DEFAULT_CONFIG = {
    "workspace_version": 1,
    "cooldown_sessions": 3,
    "outline_threshold_kb": 50,
    "resolve_min_score": 0.75,
    "families": {},
    "keyword_blocks": {},
    "accepted_duplicates": [],
    "link_ignore": [],
    "tiers": {},
    "migrations_applied": [],
}


class KbError(Exception):
    """Usage or environment error: message is shown, exit code 2."""


# Machine-local files the tool writes; everything else under .kb/ (config, profiles,
# track.ignore, issues.json, manifest.json, state.json) is shared project state.
DATA_GITIGNORE = (
    "# Written by kb. Machine-local data: backups, undo journal, upgrade log, rebuilt index.\n"
    "# Commit the rest of .kb/ (config, profiles, issue ids, shipped-file manifest).\n"
    "backups/\n"
    "journal/\n"
    "upgrade-log.jsonl\n"
    "entities.json\n"
)

CHECKS_GITIGNORE = (
    "# Written by kb. Dated check reports stay local; OPEN.md is the shared current state.\n"
    "*-check.md\n"
    "*-check-*.md\n"
)


def ensure_dir(folder: Path, gitignore: str) -> Path:
    """Create folder; write its .gitignore once (a project-edited one is never replaced)."""
    folder.mkdir(parents=True, exist_ok=True)
    ignore = folder / ".gitignore"
    if not ignore.exists():
        ignore.write_bytes(gitignore.encode("utf-8"))
    return folder


class NoWorkspace(KbError):
    """No workspace (AGENTS.md + modules.md) at the given or detected root."""


@dataclass
class Module:
    name: str
    path: str = ""
    wiki: str = ""
    sources: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)


_MODULE_RE = re.compile(r"^-\s+(\S.*?)\s*$")
_FIELD_RE = re.compile(r"^\s+-\s+([A-Za-z][A-Za-z ]*?)\s*:\s*(.*?)\s*$")
_SHARED_RE = re.compile(r"^(?:-\s+)?shared evidence\s*:\s*(.*?)\s*$", re.IGNORECASE)


def _split_values(raw: str) -> List[str]:
    out = []
    for part in raw.split(","):
        v = part.strip().strip("`").strip()
        if v:
            out.append(v)
    return out


def parse_modules(text: str) -> Tuple[List[Module], List[str]]:
    """Parse modules.md. Returns (modules, workspace-level shared evidence roots)."""
    modules: List[Module] = []
    shared: List[str] = []
    current: Optional[Module] = None
    for line in text.splitlines():
        m = _SHARED_RE.match(line)
        if m:
            shared.extend(_split_values(m.group(1)))
            current = None
            continue
        m = _MODULE_RE.match(line)
        if m:
            current = Module(name=m.group(1))
            modules.append(current)
            continue
        m = _FIELD_RE.match(line)
        if m and current is not None:
            key = m.group(1).strip().lower()
            values = _split_values(m.group(2))
            if key == "path":
                current.path = values[0] if values else ""
            elif key == "wiki":
                current.wiki = values[0] if values else ""
            elif key == "sources":
                current.sources = values
            elif key == "evidence":
                current.evidence = values
            elif key == "aliases":
                current.aliases = values
            continue
        if line.strip() and not line.startswith((" ", "\t")):
            # any other top-level line ends the current module block
            current = None
    return modules, shared


def find_root(start: Path) -> Path:
    """Walk up from start to the first folder holding both AGENTS.md and modules.md."""
    p = Path(start).resolve()
    for cand in [p] + list(p.parents):
        if (cand / "AGENTS.md").is_file() and (cand / "modules.md").is_file():
            return cand
    raise NoWorkspace("no workspace found (a folder with AGENTS.md and modules.md) at or above %s; pass --root" % p)


def _deep_merge(base: dict, over: dict) -> dict:
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
    return base


def load_config(data_dir: Path) -> dict:
    """Defaults deep-merged under the values of data_dir/config.json."""
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    path = Path(data_dir) / "config.json"
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except ValueError as exc:
            raise KbError("%s is not valid JSON: %s" % (path, exc))
        if not isinstance(data, dict):
            raise KbError("%s must hold a JSON object" % path)
        _deep_merge(cfg, data)
    return cfg


def _norm_dir(p: str) -> str:
    p = p.replace("\\", "/").strip()
    while p.startswith("./"):
        p = p[2:]
    return p.rstrip("/")


class Workspace:
    def __init__(self, root: Path, modules: List[Module], shared_evidence: List[str], config: dict):
        self.root = root
        self.kb_dir = root / "knowledge-base"
        self.data_dir = root / ".kb"
        self.modules = modules
        self.shared_evidence = shared_evidence
        self.config = config

    @classmethod
    def load(cls, root: Optional[Path] = None) -> "Workspace":
        if root is None:
            root = find_root(Path.cwd())
        else:
            root = Path(root).resolve()
            if not (root / "modules.md").is_file():
                raise NoWorkspace("%s has no modules.md" % root)
        text = (root / "modules.md").read_bytes().decode("utf-8", errors="replace")
        modules, shared = parse_modules(text)
        config = load_config(root / ".kb")
        return cls(root, modules, shared, config)

    def rel(self, p: Path) -> str:
        return Path(p).resolve().relative_to(self.root).as_posix()

    def module_for(self, relpath: str) -> Optional[str]:
        rp = _norm_dir(relpath)
        best = None
        best_len = -1
        for m in self.modules:
            for d in [m.path, m.wiki] + m.sources + m.evidence:
                nd = _norm_dir(d)
                if not nd:
                    continue
                if (rp == nd or rp.startswith(nd + "/")) and len(nd) > best_len:
                    best, best_len = m.name, len(nd)
        return best

    def read_state(self) -> dict:
        """.kb/state.json (cooldown candidates, session-changed files); empty dict when absent."""
        p = self.data_dir / "state.json"
        if p.is_file():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except ValueError:
                pass
        return {}

    def make_data_dir(self) -> Path:
        """.kb/, created with its .gitignore."""
        return ensure_dir(self.data_dir, DATA_GITIGNORE)

    def write_state(self, state: dict) -> None:
        self.make_data_dir()
        (self.data_dir / "state.json").write_bytes((json.dumps(state, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))

    def save_config(self) -> None:
        self.make_data_dir()
        (self.data_dir / "config.json").write_bytes(
            (json.dumps(self.config, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        )
