"""Entity index over the knowledge base, name lookup, check 15 (stale index)."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Set, Tuple

from .checks import iter_files, read_page, register_check, register_fixer
from .issues import Issue, Scope
from .links import _kb_roots
from .markdown import field, title

INDEX_FILE = "entities.json"
INDEX_VERSION = 2
NO_STEM = {"concept", "inventory", "readme"}
GLOSSARY = "knowledge-base/shared/glossary/"
TERM_HEADINGS = {"terms", "core entities"}
TERMINOLOGY_HEADINGS = {"terminology"}

_SEP_RE = re.compile(r"[\s_.\-]+")
_TERM_RE = re.compile(r"^\s*[-*]\s+`([^`]+)`")
_ARROW_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*->")

# generic Ukrainian/Russian letter tables (detection only)
_CYR_TO_LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "ґ": "g", "д": "d", "е": "e", "є": "ye", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "і": "i", "ї": "yi", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh",
    "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu",
    "я": "ya", "'": "", "’": "", "ʼ": "",
}
_LAT_TO_CYR = [
    ("shch", "щ"), ("zh", "ж"), ("kh", "х"), ("ts", "ц"), ("ch", "ч"), ("sh", "ш"), ("yu", "ю"),
    ("ya", "я"), ("yo", "ё"), ("ye", "є"), ("yi", "ї"), ("a", "а"), ("b", "б"), ("v", "в"), ("w", "в"),
    ("g", "г"), ("h", "г"), ("d", "д"), ("e", "е"), ("z", "з"), ("i", "и"), ("y", "й"), ("j", "й"),
    ("k", "к"), ("c", "к"), ("q", "к"), ("l", "л"), ("m", "м"), ("n", "н"), ("o", "о"), ("p", "п"),
    ("r", "р"), ("s", "с"), ("t", "т"), ("u", "у"), ("f", "ф"), ("x", "кс"),
]


@dataclass
class Hit:
    score: float
    name: str
    path: str
    kind: str
    domain: str
    why: str


def normalize(s: str) -> str:
    return _SEP_RE.sub(" ", s.casefold()).strip()


def to_latin(s: str) -> str:
    out = []
    for ch in s:
        low = ch.lower()
        if low in _CYR_TO_LAT:
            rep = _CYR_TO_LAT[low]
            out.append(rep.capitalize() if ch != low and rep else rep)
        else:
            out.append(ch)
    return "".join(out)


def to_cyrillic(s: str) -> str:
    out = []
    i = 0
    low = s.lower()
    while i < len(s):
        for lat, cyr in _LAT_TO_CYR:
            if low.startswith(lat, i):
                out.append(cyr.upper() if s[i].isupper() else cyr)
                i += len(lat)
                break
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def _loose(s: str) -> str:
    """Latin key that absorbs common transliteration variants."""
    s = to_latin(normalize(s))
    s = s.replace("kh", "h").replace("w", "v").replace("x", "ks").replace("q", "k")
    s = re.sub(r"c(?!h)", "k", s)
    s = s.replace("j", "i").replace("y", "i")
    return s


def _trigrams(s: str) -> Set[str]:
    p = "  " + s + " "
    return {p[i:i + 3] for i in range(len(p) - 2)}


def trigram_similarity(a: str, b: str) -> float:
    ta, tb = _trigrams(a), _trigrams(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _placeholder(v: str) -> bool:
    return "<" in v or ">" in v or "..." in v


def _section_lines(text: str, wanted: Set[str]) -> List[str]:
    out, on = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            on = line[3:].strip().casefold() in wanted
            continue
        if on:
            out.append(line)
    return out


def _page_entry(ws, rel: str, mtime: int) -> dict:
    text = read_page(ws, rel) or ""
    stem = rel.rsplit("/", 1)[-1][:-3]
    names: List[str] = []
    if stem.casefold() not in NO_STEM:
        names.append(stem)
    t = title(text)
    if t and not _placeholder(t):
        names.append(t)
    aliases = field(text, "aliases")
    if aliases and not _placeholder(aliases):
        names += [a.strip() for a in aliases.split(",") if a.strip()]
    if rel.startswith(GLOSSARY):
        term = field(text, "term")
        if term and not _placeholder(term):
            names.append(term)
    terms: List[str] = []
    if rel.rsplit("/", 1)[-1] == "concept.md":
        for line in _section_lines(text, TERM_HEADINGS):
            m = _TERM_RE.match(line)
            if m and not _placeholder(m.group(1)):
                terms.append(m.group(1).strip())
        for line in _section_lines(text, TERMINOLOGY_HEADINGS):
            m = _ARROW_RE.match(line)
            if m:
                left = m.group(1).strip().strip("`\"'").strip()
                if left and not _placeholder(left):
                    terms.append(left)
    kind = field(text, "kind") or ""
    domain = field(text, "domain") or ws.module_for(rel) or ""
    source = (field(text, "source") or "").strip().strip("`").strip()
    return {"mtime": mtime, "title": t or "", "kind": kind if not _placeholder(kind) else "",
            "source": "" if _placeholder(source) else source,
            "domain": domain, "names": _dedupe(names), "terms": _dedupe(terms)}


def _dedupe(items: List[str]) -> List[str]:
    seen, out = set(), []
    for i in items:
        k = normalize(i)
        if k and k not in seen:
            seen.add(k)
            out.append(i)
    return out


def kb_pages(ws) -> Dict[str, int]:
    """Indexed pages with their mtime (ns)."""
    out = {}
    for root in _kb_roots(ws):
        for rel in iter_files(ws, root):
            if rel.rsplit("/", 1)[-1] == "INDEX.md":
                continue
            try:
                out[rel] = (ws.root / rel).stat().st_mtime_ns
            except OSError:
                continue
    return out


def _is_indexable(rel: str) -> bool:
    return rel.endswith(".md") and rel.rsplit("/", 1)[-1] != "INDEX.md"


def load_index(ws) -> Optional[dict]:
    p = ws.data_dir / INDEX_FILE
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return None
    if not isinstance(data, dict) or "pages" not in data or data.get("version") != INDEX_VERSION:
        return None  # older layout: check 15 reports it and fix --safe rebuilds it
    return data


def _maps(pages: Dict[str, dict]) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    names: Dict[str, List[str]] = {}
    terms: Dict[str, List[str]] = {}
    for rel in sorted(pages):
        for n in pages[rel]["names"]:
            lst = names.setdefault(normalize(n), [])
            if rel not in lst:
                lst.append(rel)
        for n in pages[rel]["terms"]:
            lst = terms.setdefault(normalize(n), [])
            if rel not in lst:
                lst.append(rel)
    return names, terms


def build_index(ws, changed: Optional[Set[str]] = None) -> dict:
    """Write .kb/entities.json. Full rebuild, or only the changed pages when given."""
    index = compute_index(ws, changed)
    ws.make_data_dir()
    (ws.data_dir / INDEX_FILE).write_bytes((json.dumps(index, ensure_ascii=False) + "\n").encode("utf-8"))
    return index


def compute_index(ws, changed: Optional[Set[str]] = None, old: Optional[dict] = None) -> dict:
    """The index in memory: full, or the stored one with the changed pages redone. Writes nothing."""
    if changed is not None and old is None:
        old = load_index(ws)
    if old is None:
        pages = {rel: _page_entry(ws, rel, m) for rel, m in kb_pages(ws).items()}
    else:
        pages = dict(old["pages"])
        roots = tuple(r.rstrip("/") + "/" for r in _kb_roots(ws))
        for rel in changed:
            if not (rel.startswith(roots) and _is_indexable(rel)):
                continue
            p = ws.root / rel
            if p.is_file():
                pages[rel] = _page_entry(ws, rel, p.stat().st_mtime_ns)
            else:
                pages.pop(rel, None)
    names, terms = _maps(pages)
    return {"version": INDEX_VERSION, "pages": pages, "names": names, "terms": terms}


def stale_pages(ws, index: Optional[dict]) -> Set[str]:
    current = kb_pages(ws)
    if index is None:
        return set(current)
    pages = index["pages"]
    out = {rel for rel, m in current.items() if rel not in pages or pages[rel]["mtime"] != m}
    out |= {rel for rel in pages if rel not in current}
    return out


def ensure_index(ws) -> dict:
    index = load_index(ws)
    if index is None:
        return build_index(ws)
    stale = stale_pages(ws, index)
    return build_index(ws, stale) if stale else index


def fresh_index(ws) -> dict:
    """Like ensure_index, but never writes: checks read through this (check never edits)."""
    index = load_index(ws)
    if index is None:
        return compute_index(ws)
    stale = stale_pages(ws, index)
    return compute_index(ws, stale, index) if stale else index


def collisions(index: dict) -> Dict[str, List[str]]:
    """Normalized page names (not concept terms) that point to more than one page."""
    return {k: sorted(v) for k, v in index["names"].items() if len(set(v)) > 1}


def query(ws, q: str, domain: Optional[str], kind: Optional[str], top: int, fulltext: bool) -> List[Hit]:
    index = ensure_index(ws)
    pages = index["pages"]
    nq = normalize(q)
    lq = _loose(q)
    best: Dict[str, Tuple[float, str, str]] = {}

    def offer(rel: str, score: float, name: str, why: str):
        if rel not in pages:
            return
        if rel not in best or score > best[rel][0]:
            best[rel] = (score, name, why)

    keyed = []
    for src, mapping in (("name", index["names"]), ("term", index.get("terms", {}))):
        for key, rels in mapping.items():
            keyed.append((src, key, rels))
    for src, key, rels in keyed:
        if key == nq:
            for rel in rels:
                offer(rel, 1.0, key, "exact %s" % src)
            continue
        if _loose(key) == lq:
            for rel in rels:
                offer(rel, 0.95, key, "transliterated %s" % src)
            continue
        sim = trigram_similarity(_loose(key), lq)
        if sim >= 0.3:
            for rel in rels:
                offer(rel, round(sim * 0.9, 3), key, "similar %s (trigram %.2f)" % (src, sim))
    if fulltext:
        needle = q.casefold()
        for rel in pages:
            if rel in best:
                continue
            text = read_page(ws, rel) or ""
            if needle in text.casefold():
                offer(rel, 0.5, q, "text match")
    hits = []
    for rel, (score, name, why) in best.items():
        e = pages[rel]
        if domain and e["domain"].casefold() != domain.casefold():
            continue
        if kind and e["kind"].casefold() != kind.casefold():
            continue
        hits.append(Hit(score, name, rel, e["kind"], e["domain"], why))
    hits.sort(key=lambda h: (-h.score, h.path))
    return hits[:top]


def hit_dict(h: Hit) -> dict:
    return asdict(h)


# --- check 15 ------------------------------------------------------------------

def check_index(ws, scope: Scope) -> List[Issue]:
    index = load_index(ws)
    if scope.changed is None:
        stale = stale_pages(ws, index)
        if not stale:
            return []
        what = "missing" if index is None else "stale for %d page%s" % (len(stale), "" if len(stale) == 1 else "s")
        return [Issue(15, ".kb/" + INDEX_FILE, "resolver index", "minor", "",
                      "resolver index is %s" % what, "rebuild with `kb fix --safe`",
                      {"kind": "rebuild_index", "safe": True, "pages": None})]
    roots = tuple(r.rstrip("/") + "/" for r in _kb_roots(ws))
    out = []
    for rel in sorted(scope.changed):
        if not (rel.startswith(roots) and _is_indexable(rel)):
            continue
        p = ws.root / rel
        entry = index["pages"].get(rel) if index else None
        if p.is_file():
            if entry is not None and entry["mtime"] == p.stat().st_mtime_ns:
                continue
        elif entry is None:
            continue
        out.append(Issue(15, rel, "resolver index", "minor", ws.module_for(rel) or "",
                         "resolver index is stale for %s" % rel, "rebuild with `kb fix --safe`",
                         {"kind": "rebuild_index", "safe": True, "pages": [rel]}))
    return out


def fix_rebuild_index(ws, fix: dict, journal) -> None:
    if journal.dry_run:
        print(".kb/%s: rebuild%s" % (INDEX_FILE, "" if not fix.get("pages") else " for " + ", ".join(fix["pages"])))
        return
    pages = fix.get("pages")
    build_index(ws, set(pages) if pages else None)


register_check(15, check_index)
register_fixer("rebuild_index", fix_rebuild_index, late=True)
