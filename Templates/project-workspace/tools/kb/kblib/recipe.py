"""Recipes (platform techniques with a donor symbol), check 12 (drift), promotion cooldown."""
from __future__ import annotations

import datetime
import re
from pathlib import Path, PurePosixPath
from typing import List, Optional, Tuple

from .checks import iter_files, read_page, register_check
from .issues import Issue, Scope
from .markdown import field
from .outline import family_for, norm_ext
from .symbols import Symbol, extract_symbol, symbol_hash
from .workspace import KbError

RECIPES = "knowledge-base/shared/recipes"
PATTERNS_INDEX = "knowledge-base/shared/patterns/INDEX.md"
INDEX_HEADER = "| Task | Pattern or recipe | Owner module |"
FENCE_LANG = {".cs": "csharp", ".py": "python", ".ts": "typescript"}
HISTORY = 20


def dedented_body(text: str, sym: Symbol) -> str:
    """Symbol body with the indentation of its first line removed from every line."""
    col = sym.start - (text.rfind("\n", 0, sym.start) + 1)
    lines = sym.body.split("\n")
    out = [lines[0]]
    for line in lines[1:]:
        k = 0
        while k < col and k < len(line) and line[k] in " \t":
            k += 1
        out.append(line[k:].rstrip("\r"))
    return "\n".join(out)


def donor_symbol(ws, donor_rel: str, symbol: str, params: Optional[str]) -> Tuple[str, Symbol]:
    path = ws.root / donor_rel
    if not path.is_file():
        raise KbError("donor file %s not found" % donor_rel)
    ext = norm_ext(PurePosixPath(donor_rel).suffix) if PurePosixPath(donor_rel).suffix else ""
    family = family_for(ext, ws.config) if ext else None
    if family is None:
        raise KbError("`%s` has no outline family; map it with `kb config family %s <family>`" % (donor_rel, ext))
    text = path.read_bytes().decode("utf-8-sig", errors="replace")
    sym = extract_symbol(text, family, symbol, params, ws.config, ext)
    sym.snippet = dedented_body(text, sym)
    return family, sym


def slugify(title: str) -> str:
    return re.sub(r"[^\w]+", "-", title.casefold()).strip("-_") or "recipe"


def _fence(ext: str) -> str:
    return FENCE_LANG.get(ext, ext.lstrip("."))


def render_recipe(title, domain, owner, donor_rel, symbol, params, digest, sym: Symbol, ext, today) -> str:
    lang = _fence(ext)
    body = (sym.snippet or sym.body).rstrip()
    return "\n".join([
        "# %s" % title,
        "",
        "kind: recipe",
        "title: %s" % title,
        "domain: %s" % domain,
        "owner_module: %s" % owner,
        "donor_file: %s" % donor_rel,
        "donor_symbol: %s" % symbol,
        "donor_params: %s" % (params or ""),
        "symbol_hash: %s" % digest,
        "status: candidate",
        "last_verified: %s" % today,
        "",
        "## Problem",
        "",
        "- (state the task this technique solves, in platform terms)",
        "",
        "## Signature",
        "",
        "```%s" % lang,
        sym.signature,
        "```",
        "",
        "## Snippet",
        "",
        "```%s" % lang,
        body,
        "```",
        "",
        "## Adaptation",
        "",
        "- (what to change when reusing it; replace module constants with parameters)",
        "",
        "## Evidence",
        "",
        "- donor: `%s`, symbol `%s`%s; owner module %s" % (donor_rel, symbol,
                                                           " (%s)" % params if params else "", owner),
        "",
    ])


def _add_index_row(journal, row: str) -> None:
    if journal.exists(PATTERNS_INDEX):
        text = journal.read_text(PATTERNS_INDEX)
    else:
        text = "# Ready Solutions\n\nShared recipes and patterns, with the module that owns each.\n"
    lines = text.splitlines()
    if INDEX_HEADER not in lines:
        if lines and lines[-1].strip():
            lines.append("")
        lines += [INDEX_HEADER, "| --- | --- | --- |"]
        insert_at = len(lines)
    else:
        k = lines.index(INDEX_HEADER) + 1
        while k < len(lines) and lines[k].lstrip().startswith("|"):
            k += 1
        insert_at = k
    lines.insert(insert_at, row)
    journal.write_text(PATTERNS_INDEX, "\n".join(lines) + "\n", "recipe_index")


def promote(ws, donor_rel: str, symbol: str, params: Optional[str], domain: str, title: str, owner: str,
            journal) -> str:
    family, sym = donor_symbol(ws, donor_rel, symbol, params)
    rel = "%s/%s/%s.md" % (RECIPES, slugify(domain), slugify(title))
    if (ws.root / rel).exists():
        raise FileExistsError(rel)
    ext = norm_ext(PurePosixPath(donor_rel).suffix)
    today = datetime.date.today().isoformat()
    digest = symbol_hash(sym.body, family)
    journal.write_text(rel, render_recipe(title, domain, owner, donor_rel, symbol, params, digest, sym, ext, today),
                       "recipe_promote")
    link = PurePosixPath("..", "recipes", slugify(domain), slugify(title) + ".md").as_posix()
    _add_index_row(journal, "| %s | `%s` | %s |" % (title.replace("|", "\\|"), link, owner))
    return rel


# --- check 12 -------------------------------------------------------------------------

def check_recipes(ws, scope: Scope) -> List[Issue]:
    out = []
    for rel in iter_files(ws, RECIPES):
        text = read_page(ws, rel)
        if text is None:
            continue
        donor = field(text, "donor_file")
        symbol = field(text, "donor_symbol")
        if not donor or not symbol:
            continue
        if not (scope.includes(rel) or scope.includes(donor)):
            continue
        params = field(text, "donor_params") or None
        recorded = field(text, "symbol_hash") or ""
        module = field(text, "owner_module") or ""
        status, detail = None, ""
        if not (ws.root / donor).is_file():
            status, detail = "DONOR_MISSING", "donor file `%s` is missing" % donor
        else:
            try:
                family, sym = donor_symbol(ws, donor, symbol, params)
            except KbError as exc:
                status, detail = "SYMBOL_NOT_FOUND", str(exc)
            else:
                if symbol_hash(sym.body, family) != recorded:
                    status, detail = "DRIFT", "donor `%s` symbol `%s` changed since the recipe was written" % (donor, symbol)
        if status:
            out.append(Issue(12, rel, "recipe " + status, "minor", module, "%s: %s" % (status, detail),
                             "review the donor change and update the recipe (snippet and `symbol_hash`), "
                             "or retire it"))
    return out


register_check(12, check_recipes)


# --- cooldown ----------------------------------------------------------------------------

def _hash_or_none(ws, donor_rel, symbol, params) -> Optional[str]:
    try:
        family, sym = donor_symbol(ws, donor_rel, symbol, params)
    except KbError:
        return None
    return symbol_hash(sym.body, family)


def candidate_add(ws, donor_rel: str, symbol: str, params: Optional[str], module: str) -> dict:
    family, sym = donor_symbol(ws, donor_rel, symbol, params)
    state = ws.read_state()
    cands = [c for c in state.get("candidates", [])
             if not (c["file"] == donor_rel and c["symbol"] == symbol and c.get("params") == params)]
    entry = {"file": donor_rel, "symbol": symbol, "params": params, "module": module,
             "hashes": [[datetime.date.today().isoformat(), symbol_hash(sym.body, family)]], "closes_unchanged": 0}
    cands.append(entry)
    state["candidates"] = cands
    ws.write_state(state)
    return entry


def candidate_tick(ws, module: str) -> List[dict]:
    state = ws.read_state()
    ticked = []
    for c in state.get("candidates", []):
        if c.get("module", "").casefold() != module.casefold():
            continue
        h = _hash_or_none(ws, c["file"], c["symbol"], c.get("params"))
        last = c["hashes"][-1][1] if c.get("hashes") else None
        if h is not None and h == last:
            c["closes_unchanged"] = int(c.get("closes_unchanged", 0)) + 1
        else:
            c["closes_unchanged"] = 0
        c.setdefault("hashes", []).append([datetime.date.today().isoformat(), h])
        c["hashes"] = c["hashes"][-HISTORY:]
        ticked.append(c)
    ws.write_state(state)
    return ticked


def ready_candidates(ws) -> List[dict]:
    threshold = int(ws.config.get("cooldown_sessions", 3))
    return [c for c in ws.read_state().get("candidates", []) if int(c.get("closes_unchanged", 0)) >= threshold]
