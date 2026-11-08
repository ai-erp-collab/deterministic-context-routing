"""Page checks: 7 (required sections per page kind), 8 (duplicate names)."""
from __future__ import annotations

from typing import Dict, List, Tuple

from .checks import read_page, register_check
from .issues import Issue, Scope
from .links import _kb_pages
from .markdown import field, headings
from .resolve import collisions, fresh_index

REQUIRED_SECTIONS = {
    "table": ["Keys", "Fields", "Relations"],
    "class": ["Purpose", "Signature"],
    "function": ["Purpose", "Signature"],
}


def check_sections(ws, scope: Scope) -> List[Issue]:
    out = []
    for rel in _kb_pages(ws, scope):
        text = read_page(ws, rel)
        if text is None:
            continue
        kind = (field(text, "kind") or "").strip().casefold()
        required = REQUIRED_SECTIONS.get(kind)
        if not required:
            continue
        have = {h.casefold() for h in headings(text)}
        missing = [s for s in required if s.casefold() not in have]
        if missing:
            out.append(Issue(7, rel, "sections", "minor", ws.module_for(rel) or "",
                             "%s (kind: %s) lacks section%s %s" % (rel, kind, "" if len(missing) == 1 else "s",
                                                                   ", ".join("`## %s`" % m for m in missing)),
                             "add the missing section%s" % ("" if len(missing) == 1 else "s")))
    return out


def check_duplicates(ws, scope: Scope) -> List[Issue]:
    index = fresh_index(ws)  # in memory: a stale or missing file must not hide duplicates
    accepted = {tuple(sorted(p)) for p in ws.config.get("accepted_duplicates", [])}
    groups: Dict[Tuple[str, ...], List[str]] = {}
    for name, paths in collisions(index).items():
        key = tuple(sorted(set(paths)))
        groups.setdefault(key, []).append(name)
    out = []
    for paths, names in sorted(groups.items()):
        if paths in accepted:
            continue
        in_scope = [p for p in paths if scope.includes(p)]
        if not in_scope:
            continue
        anchor = in_scope[0]
        others = [p for p in paths if p != anchor]
        out.append(Issue(8, anchor, "duplicate " + ", ".join(others), "minor", ws.module_for(anchor) or "",
                         "pages share the name%s %s: %s" % ("" if len(names) == 1 else "s",
                                                           ", ".join("`%s`" % n for n in sorted(names)),
                                                           ", ".join(paths)),
                         "merge, or accept with `kb config accept-duplicate %s`" % " ".join(paths)))
    return out


register_check(7, check_sections)
register_check(8, check_duplicates)
