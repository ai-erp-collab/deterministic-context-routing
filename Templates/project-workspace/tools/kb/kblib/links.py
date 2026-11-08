"""Checks 2 (links open by path), 3 (legacy [[...]] links), 4 (index coverage) and their fixes."""
from __future__ import annotations

import fnmatch
import os
import posixpath
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import quote

from .checks import iter_files, read_page, register_check, register_fixer
from .issues import Issue, Scope
from .markdown import Link, _iter_lines, extract_links, split_target, title
from .workspace import KbError, _norm_dir

KB_ROOT = "knowledge-base"
SLOT_TARGETS = {"concept.md", "tables/", "contracts/", "usage/", "patterns/",
                "glossary/", "recipes/", "patterns/INDEX.md"}  # template slots that fill later
NEVER_MATCH = {"index.md"}  # an index basename says nothing about which index


class DirCache:
    """Directory listings for exact-case path checks, cached for one run."""

    def __init__(self, root):
        self.root = root
        self._cache: Dict[str, Optional[List[str]]] = {}

    def listing(self, rel_dir: str) -> Optional[List[str]]:
        if rel_dir not in self._cache:
            try:
                self._cache[rel_dir] = os.listdir(os.path.join(str(self.root), rel_dir) if rel_dir else str(self.root))
            except OSError:
                self._cache[rel_dir] = None
        return self._cache[rel_dir]

    def resolve(self, rel: str, ignore_case: bool) -> List[str]:
        """Exact (or case-insensitive) matches of a normalized root-relative path."""
        parts = [p for p in rel.split("/") if p]
        found = [""]
        for part in parts:
            nxt = []
            for base in found:
                names = self.listing(base) or []
                if ignore_case:
                    hits = [n for n in names if n.casefold() == part.casefold()]
                else:
                    hits = [n for n in names if n == part]
                nxt += [(base + "/" + n) if base else n for n in hits]
            found = nxt
            if not found:
                break
        return found


def _join(src_relpath: str, path: str) -> str:
    base = posixpath.dirname(src_relpath)
    return posixpath.normpath(posixpath.join(base, path)) if path else posixpath.normpath(base)


def resolve_path(ws, src_relpath: str, target: str, cache: Optional[DirCache] = None) -> Optional[str]:
    """Root-relative path the link opens, resolved from the linking file's folder; exact case."""
    path, _anchor = split_target(target)
    if not path:
        return None
    joined = _join(src_relpath, path)
    if joined == ".." or joined.startswith("../"):
        full = os.path.normpath(os.path.join(str(ws.root), joined))
        return joined if os.path.exists(full) else None
    if joined == ".":
        return ""
    cache = cache or DirCache(ws.root)
    hits = cache.resolve(joined, ignore_case=False)
    return hits[0] if hits else None


def _kb_roots(ws) -> List[str]:
    roots = [KB_ROOT]
    for m in ws.modules:
        w = _norm_dir(m.wiki)
        if w and not (w == KB_ROOT or w.startswith(KB_ROOT + "/")) and "<" not in w:
            roots.append(w)
    return roots


class NameIndex:
    """Files by casefolded basename (stem + extension), for candidate lookup."""

    def __init__(self, ws):
        self.by_name: Dict[str, List[str]] = {}
        for root in _kb_roots(ws):
            for rel in iter_files(ws, root, None):
                self.by_name.setdefault(posixpath.basename(rel).casefold(), []).append(rel)

    def candidates(self, name: str) -> List[str]:
        base = posixpath.basename(name.rstrip("/"))
        if not base or base.casefold() in NEVER_MATCH:
            return []
        stem, ext = posixpath.splitext(base)
        key = (base if ext else base + ".md").casefold()
        return sorted(self.by_name.get(key, []))


def candidates_by_basename(ws, name: str) -> List[str]:
    return NameIndex(ws).candidates(name)


def relative_link(src_relpath: str, dest_relpath: str, folder: bool = False) -> str:
    rel = posixpath.relpath(dest_relpath, posixpath.dirname(src_relpath) or ".")
    if folder and not rel.endswith("/"):
        rel += "/"
    return rel


def _rewrite_raw(link: Link, new_target: str) -> str:
    """Same link syntax as the original, with a new target."""
    if link.kind == "path":
        return "`%s`" % new_target
    raw = link.raw
    idx = raw.find(link.target, raw.find("]("))
    return raw[:idx] + new_target + raw[idx + len(link.target):]


def _new_target(link: Link, src: str, dest: str, folder: bool) -> str:
    _path, anchor = split_target(link.target)
    rel = relative_link(src, dest, folder)
    if link.kind == "md":
        rel = quote(rel, safe="/._-~()")
    return rel + ("#" + anchor if anchor else "")


def _kb_pages(ws, scope: Scope) -> List[str]:
    out = []
    for root in _kb_roots(ws):
        for rel in iter_files(ws, root):
            if scope.includes(rel):
                out.append(rel)
    return out


STOP_MARKER = "<!-- AGENT-SESSION-STOP -->"
IGNORE_MARK = "kb:ignore-link"


def _session_logs(ws) -> List[str]:
    out = ["session_state.md"] + [m.path.rstrip("/") + "/session_state.md" for m in ws.modules
                                  if m.path and "<" not in m.path]
    mods = ws.root / "modules"
    if mods.is_dir():
        out += [p.relative_to(ws.root).as_posix() for p in sorted(mods.glob("*/session_state.md"))]
    return out


def _link_pages(ws, scope: Scope) -> List[str]:
    """Pages whose links checks 2 and 3 read: the KB, the root and module AGENTS.md (the first files an
    agent reads), and the head of each session log (the part above the first stop marker)."""
    extra = ["AGENTS.md"] + [m.path.rstrip("/") + "/AGENTS.md" for m in ws.modules if m.path and "<" not in m.path]
    extra += _session_logs(ws)
    out, seen = _kb_pages(ws, scope), set()
    seen.update(out)
    for rel in extra:
        if rel not in seen and scope.includes(rel) and (ws.root / rel).is_file():
            seen.add(rel)
            out.append(rel)
    return out


def _is_log(rel: str) -> bool:
    return posixpath.basename(rel) == "session_state.md"


def _in_kb(ws, rel: str) -> bool:
    """A page inside a knowledge-base root. Files outside it (AGENTS.md, session logs) state rules in
    prose; a name search there is a guess, so their fixes are never safe unless the path itself resolves."""
    return rel.startswith(tuple(r.rstrip("/") + "/" for r in _kb_roots(ws)))


def _link_text(ws, rel: str) -> Optional[str]:
    """Page text to read links from; a session log is cut at its first stop marker (history below it
    may name files that were renamed since, and history is not rewritten)."""
    text = read_page(ws, rel)
    if text is None or not _is_log(rel):
        return text
    for _no, off, body, in_fence in _iter_lines(text):
        if not in_fence and body.strip() == STOP_MARKER:
            return text[:off]
    return text


def _live_links(ws, text: str):
    """Links not excluded by `.kb/config.json` link_ignore globs or an inline `kb:ignore-link` mark."""
    raw = ws.config.get("link_ignore") or []
    globs = [g for g in ([raw] if isinstance(raw, str) else raw) if isinstance(g, str) and g]
    marked = {no for no, line in enumerate(text.splitlines(), start=1) if IGNORE_MARK in line}
    for link in extract_links(text):
        if link.line in marked:
            continue
        path = split_target(link.target)[0]
        if any(fnmatch.fnmatchcase(path, g) or fnmatch.fnmatchcase(link.target, g) for g in globs):
            continue
        yield link


def _module(ws, rel: str) -> str:
    return ws.module_for(rel) or ""


def _folder_filter(cands: List[str], path: str) -> List[str]:
    """Keep candidates whose folders end with the folder names the link spells out."""
    parts = [p.casefold() for p in path.split("/")[:-1] if p not in ("", ".", "..")]
    if not parts:
        return cands
    return [c for c in cands if [p.casefold() for p in c.split("/")[:-1]][-len(parts):] == parts]


def _area(ws, rel: str) -> str:
    """The linking page's own area: its module wiki, the shared wiki, or the whole KB.
    A safe fix never points a link outside it."""
    best = ""
    for m in ws.modules:
        w = _norm_dir(m.wiki)
        if w and "<" not in w and rel.startswith(w + "/") and len(w) > len(best):
            best = w
    if best:
        return best + "/"
    if rel.startswith(KB_ROOT + "/shared/"):
        return KB_ROOT + "/shared/"
    return KB_ROOT + "/"


# --- check 2 -------------------------------------------------------------------

def check_links(ws, scope: Scope) -> List[Issue]:
    cache = DirCache(ws.root)
    names: Optional[NameIndex] = None
    out = []
    for rel in _link_pages(ws, scope):
        text = _link_text(ws, rel)
        if text is None:
            continue
        is_index = posixpath.basename(rel) == "INDEX.md"
        in_kb = _in_kb(ws, rel)
        for link in _live_links(ws, text):
            if link.kind == "wiki":
                continue
            if not in_kb and link.kind == "path" and "/" not in link.target.rstrip("/"):
                continue  # a bare file name in a rules file or log names a kind of file, not a route
            if resolve_path(ws, rel, link.target, cache) is not None:
                continue
            if is_index and link.kind == "path" and link.target in SLOT_TARGETS:
                continue
            path, _anchor = split_target(link.target)
            folder = path.endswith("/")
            joined = _join(rel, path)
            fix = None
            cands: List[str] = []
            if not joined.startswith(".."):
                ci = cache.resolve(joined, ignore_case=True)
                if len(ci) == 1:
                    cands = ci
                elif len(ci) > 1:
                    cands = sorted(ci)
            in_area = True
            searched = False
            if not cands and not folder:
                if names is None:
                    names = NameIndex(ws)
                cands = _folder_filter(names.candidates(path), path)
                area = _area(ws, rel)
                in_area = all(c.startswith(area) for c in cands)
                searched = True
            if len(cands) == 1:
                new = _rewrite_raw(link, _new_target(link, rel, cands[0], folder))
                safe = in_area and not _is_log(rel) and (not searched or _in_kb(ws, rel))
                fix = {"kind": "replace_link", "safe": safe, "file": rel, "start": link.start,
                       "end": link.end, "old": link.raw, "new": new}
                proposed = "change `%s` to `%s`" % (link.raw, new) + ("" if safe else " (target `%s`; confirm first: not automatic)" % cands[0])
            else:
                fix = {"kind": "replace_link", "safe": False, "file": rel, "start": link.start,
                       "end": link.end, "old": link.raw, "new": None}
                proposed = ("pick one target: " + ", ".join("`%s`" % c for c in cands)) if cands else \
                    "no file with that name; correct or remove the link"
            out.append(Issue(2, rel, "link %s line %d" % (link.target, link.line), "blocking", _module(ws, rel),
                             "%s line %d: link `%s` does not open" % (rel, link.line, link.target),
                             proposed, fix))
    return out


# --- check 3 -------------------------------------------------------------------

def _wiki_candidates(names: NameIndex, target: str) -> List[str]:
    path, _anchor = split_target(target)
    cands = names.candidates(path)
    folder_parts = [p.casefold() for p in path.split("/")[:-1] if p]
    if folder_parts:
        cands = [c for c in cands if [p.casefold() for p in c.split("/")[:-1]][-len(folder_parts):] == folder_parts]
    return cands


def check_wiki_links(ws, scope: Scope) -> List[Issue]:
    names: Optional[NameIndex] = None
    out = []
    for rel in _link_pages(ws, scope):
        text = _link_text(ws, rel)
        if text is None or "[[" not in text:
            continue
        for link in _live_links(ws, text):
            if link.kind != "wiki":
                continue
            if names is None:
                names = NameIndex(ws)
            cands = _wiki_candidates(names, link.target)
            label = link.alias or link.target
            area = _area(ws, rel)
            if len(cands) == 1:
                _p, anchor = split_target(link.target)
                target = quote(relative_link(rel, cands[0]), safe="/._-~()") + ("#" + anchor if anchor else "")
                new = "[%s](%s)" % (label, target)
                safe = cands[0].startswith(area) and _in_kb(ws, rel) and not _is_log(rel)
                fix = {"kind": "replace_link", "safe": safe, "file": rel, "start": link.start,
                       "end": link.end, "old": link.raw, "new": new}
                proposed = "change `%s` to `%s`" % (link.raw, new) + ("" if safe else " (target `%s`; confirm first: not automatic)" % cands[0])
            else:
                fix = {"kind": "replace_link", "safe": False, "file": rel, "start": link.start,
                       "end": link.end, "old": link.raw, "new": None}
                proposed = ("pick one target: " + ", ".join("`%s`" % c for c in cands)) if cands else \
                    "no page with that name; write a relative link by hand"
            out.append(Issue(3, rel, "wiki %s line %d" % (link.target, link.line), "minor", _module(ws, rel),
                             "%s line %d: legacy link `%s`" % (rel, link.line, link.raw), proposed, fix))
    return out


# --- check 4 -------------------------------------------------------------------

def _covering_index(ws, rel: str, strict: bool) -> Optional[str]:
    folder = posixpath.dirname(rel)
    if strict:
        if folder == KB_ROOT or "/" not in folder:
            return None
        folder = posixpath.dirname(folder)
    while folder and (folder == KB_ROOT or folder.startswith(KB_ROOT + "/")):
        if (ws.root / folder / "INDEX.md").is_file():
            return folder + "/INDEX.md"
        folder = posixpath.dirname(folder)
    return None


def check_indexes(ws, scope: Scope) -> List[Issue]:
    cache = DirCache(ws.root)
    targets_of: Dict[str, Set[str]] = {}
    out = []
    for rel in _kb_pages(ws, scope):
        if not rel.startswith(KB_ROOT + "/"):
            continue
        is_index = posixpath.basename(rel) == "INDEX.md"
        if is_index and posixpath.dirname(rel) == KB_ROOT:
            continue
        index = _covering_index(ws, rel, strict=is_index)
        if index is None:
            continue
        if index not in targets_of:
            text = read_page(ws, index) or ""
            resolved = set()
            for link in extract_links(text):
                r = resolve_path(ws, index, link.target, cache)
                if r is not None:
                    resolved.add(r)
            targets_of[index] = resolved
        resolved = targets_of[index]
        page_dir = posixpath.dirname(rel)
        index_dir = posixpath.dirname(index)
        covered = rel in resolved
        d = page_dir
        while not covered and d and d != index_dir and len(d) > len(index_dir):
            if d in resolved:
                covered = True
            d = posixpath.dirname(d)
        if covered:
            continue
        text = read_page(ws, rel) or ""
        name = title(text) or posixpath.splitext(posixpath.basename(rel))[0]
        if is_index:
            entry = relative_link(index, page_dir, folder=True)
        else:
            entry = relative_link(index, rel)
        line = "- `%s`: %s" % (entry, name)
        out.append(Issue(4, rel, "index", "minor", _module(ws, rel),
                         "`%s` is not listed in `%s`" % (rel, index),
                         "add `%s` to `%s`" % (line, index),
                         {"kind": "add_index_line", "safe": True, "file": index, "line": line}))
    return out


# --- fixers --------------------------------------------------------------------

def fix_replace_link(ws, fix: dict, journal) -> None:
    if not fix.get("new"):
        raise KbError("no single target for %s" % fix.get("old"))
    text = journal.read_text(fix["file"])
    start, end = int(fix["start"]), int(fix["end"])
    if text[start:end] != fix["old"]:
        raise KbError("%s changed since the check (expected `%s` at %d)" % (fix["file"], fix["old"], start))
    journal.write_text(fix["file"], text[:start] + fix["new"] + text[end:], "replace_link")


def fix_add_index_line(ws, fix: dict, journal) -> None:
    text = journal.read_text(fix["file"])
    if fix["line"] in text.splitlines():
        return
    if text and not text.endswith("\n"):
        text += "\n"
    journal.write_text(fix["file"], text + fix["line"] + "\n", "add_index_line")


register_check(2, check_links)
register_check(3, check_wiki_links)
register_check(4, check_indexes)
register_fixer("replace_link", fix_replace_link)
register_fixer("add_index_line", fix_add_index_line)
