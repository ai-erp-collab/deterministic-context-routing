"""Environment probe (parser tiers), extension scan, check 14 (extension without outline family)."""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
from pathlib import PurePosixPath
from typing import Dict, List, Tuple

from .artifacts import tracked_files
from .checks import register_check
from .issues import Issue, Scope
from .outline import FAMILIES, family_for, norm_ext

# data and document formats: tracked as evidence, never outlined
NO_OUTLINE_EXT = {
    ".xlsx", ".xls", ".xlsm", ".xlsb", ".ods", ".csv", ".tsv", ".txt", ".docx", ".doc", ".odt", ".rtf", ".pdf",
    ".pptx", ".ppt", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".zip", ".7z", ".rar", ".gz",
    ".tar", ".dll", ".exe", ".bin", ".log", ".json5",
}


def probe_tiers() -> Dict[str, bool]:
    """Probe only; never installs anything."""
    dotnet = False
    exe = shutil.which("dotnet")
    if exe:
        try:
            proc = subprocess.run([exe, "--list-sdks"], capture_output=True, text=True, timeout=15)
            dotnet = proc.returncode == 0 and bool(proc.stdout.strip())
        except (OSError, subprocess.SubprocessError):
            dotnet = False
    try:
        tree_sitter = importlib.util.find_spec("tree_sitter") is not None
    except (ImportError, ValueError):
        tree_sitter = False
    return {"dotnet": dotnet, "tree_sitter": tree_sitter}


def scan_extensions(ws) -> Tuple[Dict[str, str], Dict[str, str]]:
    """(known ext -> family, unknown ext -> first file) over tracked evidence files."""
    known: Dict[str, str] = {}
    unknown: Dict[str, str] = {}
    for rel in tracked_files(ws):
        suffix = PurePosixPath(rel).suffix
        if not suffix:
            continue
        ext = norm_ext(suffix)
        if ext in NO_OUTLINE_EXT or ext in known or ext in unknown:
            continue
        fam = family_for(ext, ws.config)
        if fam:
            known[ext] = fam
        else:
            unknown[ext] = rel
    return known, unknown


def run_doctor(ws) -> Tuple[Dict[str, bool], Dict[str, str], Dict[str, str]]:
    tiers = probe_tiers()
    known, unknown = scan_extensions(ws)
    ws.config["tiers"] = tiers
    fams = ws.config.setdefault("families", {})
    mapped = {}
    for ext, fam in sorted(known.items()):
        if ext not in fams:
            fams[ext] = fam
            mapped[ext] = fam
    ws.save_config()
    return tiers, mapped, unknown


def check_families(ws, scope: Scope) -> List[Issue]:
    _known, unknown = scan_extensions(ws)
    if scope.changed is not None:
        # report against the changed file itself, one issue per extension
        firsts = {}
        for rel in sorted(scope.changed):
            ext = norm_ext(PurePosixPath(rel).suffix) if PurePosixPath(rel).suffix else ""
            if ext in unknown and ext not in firsts:
                firsts[ext] = rel
        unknown = firsts
    out = []
    for ext, rel in sorted(unknown.items()):
        out.append(Issue(14, rel, "family " + ext, "minor", ws.module_for(rel) or "",
                         "`%s` files have no outline family (first: `%s`)" % (ext, rel),
                         "assign one: `kb config family %s <family>` (families: %s)" % (ext, ", ".join(FAMILIES))))
    return out


register_check(14, check_families)
