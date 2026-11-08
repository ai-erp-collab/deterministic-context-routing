"""Outlines (skeletons) of source files per language family. Tier B: standard library only."""
from __future__ import annotations

import ast
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .lexer import mask, mask_comments
from .tables import decode_text
from .workspace import DEFAULT_CONFIG, KbError

DEFAULT_FAMILIES = {
    "c-like": [".cs", ".java", ".kt", ".kts", ".go", ".js", ".jsx", ".mjs", ".ts", ".tsx", ".c", ".h", ".cpp",
               ".hpp", ".cc", ".php", ".swift", ".rs", ".scala", ".dart"],
    "python": [".py"],
    "sql": [".sql"],
    "json": [".json"],
    "xml": [".xml", ".xaml", ".config", ".csproj", ".resx"],
    "markup": [".html", ".htm", ".css", ".md"],
    "keyword-block": [],
}
FAMILIES = tuple(DEFAULT_FAMILIES)
_DEFAULT_BY_EXT = {ext: fam for fam, exts in DEFAULT_FAMILIES.items() for ext in exts}
CONTAINER_WORDS = {"namespace", "class", "struct", "interface", "enum", "record", "trait", "impl", "object",
                   "module"}
SKIP_DIRECTIVES = re.compile(r"^[ \t]*#[ \t]*(?:region|endregion|if|ifdef|ifndef|else|elif|endif|pragma|define|undef"
                             r"|include|import|nullable|line|error|warning)\b.*$", re.M)
IND = "    "


@dataclass
class OutlineResult:
    text: str
    tier: str
    family: str
    size_before: int
    size_after: int


def norm_ext(ext: str) -> str:
    ext = ext.strip().lower()
    return ext if ext.startswith(".") else "." + ext


def family_for(ext: str, config: dict) -> Optional[str]:
    ext = norm_ext(ext)
    fam = (config.get("families") or {}).get(ext)
    if fam:
        return fam
    if ext in (config.get("keyword_blocks") or {}):
        return "keyword-block"
    return _DEFAULT_BY_EXT.get(ext)


def _collapse(s: str) -> str:
    s = " ".join(s.split())
    s = re.sub(r"\(\s+", "(", s)
    return re.sub(r"\s+\)", ")", s)


# --- c-like ---------------------------------------------------------------------

def _match_brace(m: str, i: int, end: int) -> int:
    depth = 0
    for k in range(i, end):
        ch = m[k]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return k
    return end - 1


def _render(m: str, c: str, a: int, b: int) -> str:
    """Original text (comments removed) with top-level brace groups shown as '{ ... }'."""
    parts = []
    k = a
    while k < b:
        if m[k] == "{":
            j = _match_brace(m, k, b)
            parts.append("{ ... }")
            k = j + 1
            continue
        parts.append(c[k])
        k += 1
    return _collapse("".join(parts))


_EXPR_END = ("=", "(", ",", "[", ":", "?", "=>", "&&", "||", "!")
_EXPR_WORDS = {"return", "import", "export", "new", "await", "yield", "in", "of", "from"}


def _expression_brace(head_m: str, paren: int) -> bool:
    if paren > 0:
        return True
    h = head_m.rstrip()
    if h.endswith(_EXPR_END):
        return True
    words = re.findall(r"[A-Za-z_]\w*$", h)
    return bool(words) and words[0] in _EXPR_WORDS


def _is_container(head_m: str) -> bool:
    h = head_m.strip()
    before = h.split("(", 1)[0]
    words = set(re.findall(r"[A-Za-z_]\w*", before))
    hits = words & CONTAINER_WORDS
    if hits == {"object"} and h.endswith(")"):
        return False
    return bool(hits)


def _stmt_end_after_arrow(m: str, i: int, end: int) -> int:
    """Index of the last character of an expression body starting at i."""
    k = i
    while k < end and m[k] in " \t\r\n":
        k += 1
    if k < end and m[k] == "{":
        j = _match_brace(m, k, end)
        k2 = j + 1
        while k2 < end and m[k2] in " \t\r\n":
            k2 += 1
        return k2 if k2 < end and m[k2] == ";" else j
    depth = 0
    for p in range(k, end):
        ch = m[p]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == ";" and depth <= 0:
            return p
    return end - 1


def _c_block(m: str, c: str, start: int, end: int, depth: int, out: List[str]) -> None:
    i = start
    stmt = start
    paren = 0

    def emit(s: str) -> None:
        if s and s != ";":
            out.append(IND * depth + s)

    while i < end:
        ch = m[i]
        if ch in "([":
            paren += 1
        elif ch in ")]":
            paren = max(0, paren - 1)
        elif ch == ";" and paren == 0:
            emit(_render(m, c, stmt, i + 1))
            i += 1
            stmt = i
            continue
        elif ch == "=" and paren == 0 and i + 1 < end and m[i + 1] == ">":
            head = _render(m, c, stmt, i)
            j = _stmt_end_after_arrow(m, i + 2, end)
            emit(head + " => ...;")
            i = j + 1
            stmt = i
            paren = 0
            continue
        elif ch == "{":
            head_m = m[stmt:i]
            j = _match_brace(m, i, end)
            if not head_m.strip():
                i = j + 1
                stmt = i
                continue
            if _expression_brace(head_m, paren):
                i = j + 1
                continue
            head = _render(m, c, stmt, i)
            if _is_container(head_m):
                emit(head + " {")
                _c_block(m, c, i + 1, j, depth + 1, out)
                emit("}")
            else:
                emit(head + " { ... }")
            i = j + 1
            stmt = i
            paren = 0
            continue
        elif ch == "}":
            i += 1
            stmt = i
            continue
        i += 1
    if depth > 0:
        emit(_render(m, c, stmt, end))


def _outline_c(text: str, config: dict, ext: Optional[str]) -> str:
    m = mask(text, "c-like")
    c = mask_comments(text, "c-like")
    # preprocessor directives are not part of the outline
    for d in SKIP_DIRECTIVES.finditer(m):
        blank = re.sub(r"[^\r\n]", " ", d.group(0))
        m = m[:d.start()] + blank + m[d.end():]
        c = c[:d.start()] + blank + c[d.end():]
    out: List[str] = []
    _c_block(m, c, 0, len(m), 0, out)
    return "\n".join(out)


# --- python ---------------------------------------------------------------------

def _outline_python(text: str, config: dict, ext: Optional[str]) -> str:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return "(python syntax error at line %s: %s)" % (exc.lineno, exc.msg)
    c = mask_comments(text, "python")
    lines = text.splitlines(True)
    starts = [0]
    for ln in lines:
        starts.append(starts[-1] + len(ln))

    def off(lineno: int, col: int) -> int:
        line = lines[lineno - 1] if lineno - 1 < len(lines) else ""
        return starts[lineno - 1] + len(line.encode("utf-8")[:col].decode("utf-8", errors="ignore"))

    def seg(node) -> str:
        return _collapse(c[off(node.lineno, node.col_offset):off(node.end_lineno, node.end_col_offset)])

    def header(node) -> str:
        a = off(node.lineno, node.col_offset)
        b = off(node.body[0].lineno, node.body[0].col_offset)
        h = c[a:b].rstrip()
        cut = h.rfind(":")
        return _collapse(h[:cut + 1] if cut >= 0 else h)

    out: List[str] = []

    def visit(body, depth: int, module_level: bool) -> None:
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for dec in node.decorator_list:
                    out.append(IND * depth + "@" + seg(dec))
                out.append(IND * depth + header(node))
                doc = ast.get_docstring(node)
                if doc:
                    out.append(IND * (depth + 1) + '"""%s"""' % doc.strip().splitlines()[0].strip())
                if isinstance(node, ast.ClassDef):
                    visit(node.body, depth + 1, False)
            elif module_level and isinstance(node, ast.Assign):
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                if names and len(names) == len(node.targets) and all(re.match(r"^[A-Z][A-Z0-9_]*$", n) for n in names):
                    out.append(" = ".join(names) + " = ...")
            elif module_level and isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if re.match(r"^[A-Z][A-Z0-9_]*$", node.target.id):
                    out.append("%s: %s%s" % (node.target.id, seg(node.annotation), " = ..." if node.value else ""))

    visit(tree.body, 0, True)
    return "\n".join(out)


# --- sql ------------------------------------------------------------------------

_SQL_START = re.compile(r"^(CREATE|ALTER)\b", re.I | re.M)
_SQL_GO = re.compile(r"^[ \t]*GO[ \t]*$", re.I | re.M)
_SQL_KIND = re.compile(r"(?:CREATE|ALTER)\s+(?:OR\s+(?:REPLACE|ALTER)\s+)?(?:UNIQUE\s+)?(?:(?:NON)?CLUSTERED\s+)?"
                       r"(TABLE|VIEW|PROCEDURE|PROC|FUNCTION|TRIGGER|INDEX)\b", re.I)


def _outline_sql(text: str, config: dict, ext: Optional[str]) -> str:
    m = mask(text, "sql")
    c = mask_comments(text, "sql")
    starts = [x.start() for x in _SQL_START.finditer(m)]
    out: List[str] = []
    for n, s in enumerate(starts):
        e = starts[n + 1] if n + 1 < len(starts) else len(m)
        go = _SQL_GO.search(m, s, e)
        if go:
            e = go.start()
        km = _SQL_KIND.match(m, s)
        if not km:
            continue
        kind = km.group(1).upper()
        if kind == "TABLE":
            depth, stop = 0, e
            for k in range(s, e):
                if m[k] == "(":
                    depth += 1
                elif m[k] == ")":
                    depth -= 1
                elif m[k] == ";" and depth <= 0:
                    stop = k + 1
                    break
            for line in c[s:stop].splitlines():
                if line.strip():
                    out.append(line.rstrip())
        elif kind == "INDEX":
            semi = m.find(";", s, e)
            out.append(_collapse(c[s:(semi + 1 if semi >= 0 else e)]))
        else:
            word = re.compile(r"\b(AS|BEGIN)\b", re.I).search(m, km.end(), e)
            if word:
                out.append(_collapse(c[s:word.start()]) + " " + c[word.start():word.end()] + " ...")
            else:
                out.append(_collapse(c[s:e]))
    return "\n".join(out)


# --- json -----------------------------------------------------------------------

def _json_type(v) -> str:
    if isinstance(v, bool):
        return "boolean"
    if v is None:
        return "null"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "array"
    return "object"


def _json_inline(v, depth: int, out: List[str], indent: int, key: str) -> None:
    prefix = IND * indent + key
    if isinstance(v, dict):
        if not v:
            out.append(prefix + "{}")
        elif depth > 3:
            out.append(prefix + "{%d key%s}" % (len(v), "" if len(v) == 1 else "s"))
        else:
            out.append(prefix + "{")
            for k, child in v.items():
                _json_inline(child, depth + 1, out, indent + 1, json.dumps(k, ensure_ascii=False) + ": ")
            out.append(IND * indent + "}")
    elif isinstance(v, list):
        out.append(prefix + ("[]" if not v else "[%d × %s]" % (len(v), _json_type(v[0]))))
    else:
        out.append(prefix + _json_type(v))


def _outline_json(text: str, config: dict, ext: Optional[str]) -> str:
    try:
        data = json.loads(text)
    except ValueError as exc:
        return "(invalid JSON: %s)" % exc
    out: List[str] = []
    _json_inline(data, 1, out, 0, "")
    return "\n".join(out)


# --- xml ------------------------------------------------------------------------

def _local(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def _xml_elem(el, depth: int, out: List[str], count: int) -> None:
    attrs = "".join(' %s="%s"' % (_local(k), v) for k, v in list(el.attrib.items())[:3])
    line = IND * (depth - 1) + "<%s%s>" % (_local(el.tag), attrs)
    if count > 1:
        line += " × %d" % count
    out.append(line)
    if depth >= 4:
        return
    groups: Dict[str, list] = {}
    for child in el:
        if not isinstance(child.tag, str):
            continue
        groups.setdefault(child.tag, []).append(child)
    for tag, items in groups.items():
        _xml_elem(items[0], depth + 1, out, len(items))


def _outline_xml(text: str, config: dict, ext: Optional[str]) -> str:
    body = re.sub(r"^\s*<\?xml[^>]*\?>", "", text)
    try:
        root = ET.fromstring(body)
    except ET.ParseError as exc:
        return "(invalid XML: %s)" % exc
    out: List[str] = []
    _xml_elem(root, 1, out, 1)
    return "\n".join(out)


# --- markup ---------------------------------------------------------------------

def _outline_markup(text: str, config: dict, ext: Optional[str]) -> str:
    ext = norm_ext(ext or ".md")
    out: List[str] = []
    if ext in (".html", ".htm"):
        for mm in re.finditer(r"<h([1-6])[^>]*>(.*?)</h\1>", text, re.I | re.S):
            out.append("h%s: %s" % (mm.group(1), _collapse(re.sub(r"<[^>]+>", "", mm.group(2)))))
    elif ext == ".css":
        m = mask(text, "markup")
        depth, last = 0, 0
        for k, ch in enumerate(m):
            if ch == "{":
                sel = _collapse(m[last:k])
                if sel:
                    out.append(IND * depth + sel)
                depth += 1
                last = k + 1
            elif ch in "};":
                if ch == "}":
                    depth = max(0, depth - 1)
                last = k + 1
    else:
        fence = None
        for line in text.splitlines():
            fm = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
            if fm:
                fence = None if fence and fm.group(1)[0] == fence else (fence or fm.group(1)[0])
                continue
            if fence is None and re.match(r"^#{1,6} ", line):
                out.append(line.rstrip())
    return "\n".join(out)


# --- keyword-block --------------------------------------------------------------

def _outline_keyword(text: str, config: dict, ext: Optional[str]) -> str:
    blocks = config.get("keyword_blocks") or {}
    rule = blocks.get(norm_ext(ext)) if ext else None
    if rule is None:
        raise KbError("no keyword-block rule for %s; use `kb config family %s keyword-block --start RE --end RE`"
                      % (ext, ext))
    start = re.compile(rule["start"], re.I)
    end = re.compile(rule["end"], re.I)
    m = mask(text, "keyword-block")
    src = text.splitlines()
    out: List[str] = []
    depth = 0
    for n, line in enumerate(m.splitlines()):
        if end.search(line):
            depth = max(0, depth - 1)
        elif start.search(line):
            out.append(IND * depth + src[n].strip())
            depth += 1
    return "\n".join(out)


BACKENDS: Dict[str, Dict[str, Callable]] = {
    "A": {},
    "B": {
        "c-like": _outline_c,
        "python": _outline_python,
        "sql": _outline_sql,
        "json": _outline_json,
        "xml": _outline_xml,
        "markup": _outline_markup,
        "keyword-block": _outline_keyword,
    },
}


def outline_text(text: str, family: str, config: dict, ext: Optional[str] = None) -> str:
    fn = BACKENDS["B"].get(family)
    if fn is None:
        raise KbError("unknown family `%s`; families: %s" % (family, ", ".join(FAMILIES)))
    return fn(text, config, ext)


def outline_file(ws_or_none, path: Path) -> OutlineResult:
    config = ws_or_none.config if ws_or_none is not None else DEFAULT_CONFIG
    path = Path(path)
    ext = norm_ext(path.suffix) if path.suffix else ""
    family = family_for(ext, config) if ext else None
    if family is None:
        raise KbError("`%s` has no outline family; map it with `kb config family %s <family>` (families: %s)"
                      % (path.name, ext or "<ext>", ", ".join(FAMILIES)))
    data = path.read_bytes()
    warning = ""
    try:
        text = decode_text(data, None)  # BOM, UTF-16 (with or without BOM), UTF-8
    except KbError:
        text = data.decode("cp1252", errors="replace")
        warning = " | warning: not UTF-8/UTF-16, read as cp1252"
    tier = "B"
    fn = BACKENDS["A"].get(family)
    if fn is not None and any((config.get("tiers") or {}).values()):
        tier = "A"
        body = fn(text, config)
    else:
        body = outline_text(text, family, config, ext)
    body = body.rstrip("\n") + "\n"
    size_after = len(body.encode("utf-8"))
    head = "tier: %s | family: %s | %d -> %d bytes%s" % (tier, family, len(data), size_after, warning)
    return OutlineResult(head + "\n" + body, tier, family, len(data), size_after)
