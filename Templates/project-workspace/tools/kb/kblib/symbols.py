"""Symbol definitions (never call sites), overload selection, body hashing."""
from __future__ import annotations

import ast
import hashlib
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .lexer import mask, mask_comments, spans
from .outline import (CONTAINER_WORDS, _collapse, _expression_brace, _is_container, _match_brace, _render,
                      _stmt_end_after_arrow, norm_ext)
from .workspace import KbError


@dataclass
class Symbol:
    name: str
    signature: str
    start: int
    end: int
    body: str
    snippet: str = ""  # body dedented to its first line; filled by recipe code


# --- c-like --------------------------------------------------------------------------

_IDENT = r"[A-Za-z_$][\w$]*"


def _strip_attrs(head: str) -> str:
    """Drop leading [Attributes] and @Annotations(...)."""
    h = head.strip()
    while True:
        if h.startswith("["):
            depth = 0
            for k, ch in enumerate(h):
                if ch == "[":
                    depth += 1
                elif ch == "]":
                    depth -= 1
                    if depth == 0:
                        h = h[k + 1:].lstrip()
                        break
            else:
                return h
            continue
        m = re.match(r"@" + _IDENT + r"(?:\.\w+)*", h)
        if m:
            rest = h[m.end():].lstrip()
            if rest.startswith("("):
                depth = 0
                for k, ch in enumerate(rest):
                    if ch == "(":
                        depth += 1
                    elif ch == ")":
                        depth -= 1
                        if depth == 0:
                            rest = rest[k + 1:]
                            break
            h = rest.lstrip()
            continue
        return h


def _top_level_index(s: str, target: str) -> int:
    depth = 0
    for k, ch in enumerate(s):
        if ch in "(<[{":
            depth += 1
        elif ch in ")>]}":
            depth = max(0, depth - 1)
        elif ch == target and depth == 0:
            if target == "=" and k + 1 < len(s) and s[k + 1] in "=>":
                continue
            return k
    return -1


def declared_name(head_m: str) -> Tuple[Optional[str], Optional[str]]:
    """(declared name, raw parameter list or None) of a masked header."""
    h = _strip_attrs(head_m)
    before_paren = h.split("(", 1)[0]
    if _is_container(h):
        words = re.findall(_IDENT, before_paren)
        for k, w in enumerate(words):
            if w in CONTAINER_WORDS and k + 1 < len(words):
                return words[k + 1], _params_of(h, h.find("("))
        return None, None
    eq = _top_level_index(h, "=")
    paren = h.find("(")
    if eq >= 0 and (paren < 0 or eq < paren):
        ids = re.findall(_IDENT, h[:eq])
        return (ids[-1] if ids else None), None
    if paren >= 0:
        pre = h[:paren].rstrip()
        if pre.endswith(">"):  # generic method Name<T>(
            depth = 0
            for k in range(len(pre) - 1, -1, -1):
                if pre[k] == ">":
                    depth += 1
                elif pre[k] == "<":
                    depth -= 1
                    if depth == 0:
                        pre = pre[:k].rstrip()
                        break
        m = re.search(_IDENT + r"$", pre)
        return (m.group(0) if m else None), _params_of(h, paren)
    ids = re.findall(_IDENT, h)
    return (ids[-1] if ids else None), None


def _params_of(h: str, paren: int) -> Optional[str]:
    if paren < 0:
        return None
    depth = 0
    for k in range(paren, len(h)):
        if h[k] == "(":
            depth += 1
        elif h[k] == ")":
            depth -= 1
            if depth == 0:
                return h[paren + 1:k]
    return h[paren + 1:]


def _split_top(s: str) -> List[str]:
    out, depth, cur = [], 0, []
    for ch in s:
        if ch in "(<[{":
            depth += 1
        elif ch in ")>]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if "".join(cur).strip():
        out.append("".join(cur))
    return [p.strip() for p in out if p.strip()]


def _param_keys(raw: Optional[str]) -> List[Tuple[str, str]]:
    """[(type, name)] with spaces removed from types."""
    if raw is None:
        return []
    keys = []
    for p in _split_top(raw):
        p = re.sub(r"\[[^\]]*\]\s*", "", p) if p.startswith("[") else p
        eq = _top_level_index(p, "=")
        if eq >= 0:
            p = p[:eq]
        p = p.strip()
        if ":" in p and not p.startswith(("ref ", "out ", "in ")):
            name, typ = p.split(":", 1)
            name = re.sub(r"^(?:private|public|protected|readonly|\s)+", "", name).strip().rstrip("?")
            keys.append((typ.replace(" ", ""), name))
            continue
        m = re.search(_IDENT + r"$", p)
        name = m.group(0) if m else p
        typ = p[:m.start()] if m else ""
        typ = re.sub(r"^(?:this|ref|out|in|params|final|const)\s+", "", typ.strip())
        keys.append((typ.replace(" ", ""), name))
    return keys


@dataclass
class _Def:
    name: Optional[str]
    params: Optional[str]
    start: int
    head_end: int
    end: int
    signature: str


def _c_defs(m: str, c: str, start: int, end: int, out: List[_Def]) -> None:
    i = stmt = start
    paren = 0
    while i < end:
        ch = m[i]
        if ch in "([":
            paren += 1
        elif ch in ")]":
            paren = max(0, paren - 1)
        elif ch == ";" and paren == 0:
            i += 1
            stmt = i
            continue
        elif ch == "=" and paren == 0 and i + 1 < end and m[i + 1] == ">":
            head_m = m[stmt:i]
            hs = stmt + len(head_m) - len(head_m.lstrip())
            j = _stmt_end_after_arrow(m, i + 2, end)
            name, params = declared_name(m[hs:i])
            out.append(_Def(name, params, hs, i, j + 1, _render(m, c, hs, i)))
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
            hs = stmt + len(head_m) - len(head_m.lstrip())
            name, params = declared_name(m[hs:i])
            out.append(_Def(name, params, hs, i, j + 1, _render(m, c, hs, i)))
            if _is_container(head_m):
                _c_defs(m, c, i + 1, j, out)
            i = j + 1
            stmt = i
            paren = 0
            continue
        elif ch == "}":
            i += 1
            stmt = i
            continue
        i += 1


def _c_symbols(text: str, name: str) -> List[Tuple[Symbol, List[Tuple[str, str]]]]:
    m = mask(text, "c-like")
    c = mask_comments(text, "c-like")
    defs: List[_Def] = []
    _c_defs(m, c, 0, len(m), defs)
    out = []
    for d in defs:
        if d.name == name:
            out.append((Symbol(name, d.signature, d.start, d.end, text[d.start:d.end]), _param_keys(d.params)))
    return out


# --- python --------------------------------------------------------------------------

def _py_symbols(text: str, name: str) -> List[Tuple[Symbol, List[Tuple[str, str]]]]:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        raise KbError("python syntax error at line %s: %s" % (exc.lineno, exc.msg))
    c = mask_comments(text, "python")
    lines = text.splitlines(True)
    starts = [0]
    for ln in lines:
        starts.append(starts[-1] + len(ln))

    def off(lineno: int, col: int) -> int:
        line = lines[lineno - 1] if lineno - 1 < len(lines) else ""
        return starts[lineno - 1] + len(line.encode("utf-8")[:col].decode("utf-8", errors="ignore"))

    out = []

    def visit(body, in_class: bool):
        for node in body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if node.name == name:
                a = off(node.lineno, node.col_offset)
                if node.decorator_list:
                    d = node.decorator_list[0]
                    a = c.rfind("@", 0, off(d.lineno, d.col_offset))
                b = off(node.end_lineno, node.end_col_offset)
                hs = off(node.lineno, node.col_offset)
                he = off(node.body[0].lineno, node.body[0].col_offset)
                head = c[hs:he].rstrip()
                cut = head.rfind(":")
                sig = _collapse(head[:cut + 1] if cut >= 0 else head)
                keys = []
                if not isinstance(node, ast.ClassDef):
                    args = list(getattr(node.args, "posonlyargs", [])) + list(node.args.args) + list(node.args.kwonlyargs)
                    if in_class and args and args[0].arg in ("self", "cls"):
                        args = args[1:]
                    for arg in args:
                        typ = ast.get_source_segment(text, arg.annotation) if arg.annotation is not None else ""
                        keys.append(((typ or "").replace(" ", ""), arg.arg))
                out.append((Symbol(name, sig, a, b, text[a:b]), keys))
            if isinstance(node, ast.ClassDef):
                visit(node.body, True)

    visit(tree.body, False)
    return out


# --- keyword-block -------------------------------------------------------------------

def _kw_symbols(text: str, name: str, config: Optional[dict], ext: Optional[str]):
    rule = ((config or {}).get("keyword_blocks") or {}).get(norm_ext(ext)) if ext else None
    if rule is None:
        raise KbError("no keyword-block rule for %s" % ext)
    start_rx = re.compile(rule["start"], re.I)
    end_rx = re.compile(rule["end"], re.I)
    m = mask(text, "keyword-block")
    mlines = m.splitlines(True)
    offs = [0]
    for ln in mlines:
        offs.append(offs[-1] + len(ln))
    out = []
    for n, line in enumerate(mlines):
        sm = start_rx.search(line)
        if not sm or end_rx.search(line):
            continue
        rest = line[sm.end():].lstrip()
        if not re.match(re.escape(name) + r"(?!\w)", rest):
            continue
        depth = 0
        stop = len(mlines) - 1
        for k in range(n, len(mlines)):
            if end_rx.search(mlines[k]):
                depth -= 1
                if depth == 0:
                    stop = k
                    break
            elif start_rx.search(mlines[k]):
                depth += 1
        a = offs[n] + (len(line) - len(line.lstrip()))
        b = offs[stop] + len(mlines[stop].rstrip("\r\n"))
        sig = text[offs[n]:offs[n] + len(line)].strip()
        out.append((Symbol(name, sig, a, b, text[a:b]), []))
    return out


# --- public API ------------------------------------------------------------------------

def _candidates(text: str, family: str, name: str, config=None, ext=None):
    if family == "c-like":
        return _c_symbols(text, name)
    if family == "python":
        return _py_symbols(text, name)
    if family == "keyword-block":
        return _kw_symbols(text, name, config, ext)
    raise KbError("symbol extraction supports c-like, python and keyword-block, not %s" % family)


def find_symbols(text: str, family: str, name: str, config: Optional[dict] = None,
                 ext: Optional[str] = None) -> List[Symbol]:
    return [s for s, _k in _candidates(text, family, name, config, ext)]


def _params_match(keys: List[Tuple[str, str]], wanted: List[str]) -> bool:
    if len(keys) != len(wanted):
        return False
    for (typ, nm), w in zip(keys, wanted):
        w = w.replace(" ", "")
        if w.casefold() not in (typ.casefold(), nm.casefold()):
            return False
    return True


def extract_symbol(text: str, family: str, name: str, params: Optional[str] = None,
                   config: Optional[dict] = None, ext: Optional[str] = None) -> Symbol:
    cands = _candidates(text, family, name, config, ext)
    if not cands:
        raise KbError("symbol `%s` not found (definitions only)" % name)
    if params is not None:
        wanted = [p.strip() for p in params.split(",") if p.strip()]
        picked = [s for s, keys in cands if _params_match(keys, wanted)]
    else:
        picked = [s for s, _k in cands]
    if len(picked) == 1:
        return picked[0]
    sigs = "; ".join(s.signature for s, _k in cands)
    if not picked:
        raise KbError("no `%s` matches --params %s; signatures: %s" % (name, params, sigs))
    raise KbError("`%s` is ambiguous; pick one with --params: %s" % (name, sigs))


def normalize_for_hash(body: str, family: str) -> str:
    """Comments removed, string contents kept verbatim, whitespace collapsed elsewhere."""
    chars = list(body)
    protected = [False] * len(chars)
    for kind, a, b in spans(body, family):
        for k in range(a, min(b, len(chars))):
            if kind == "comment":
                chars[k] = " "
            else:
                protected[k] = True
    out = []
    prev_space = False
    for ch, prot in zip(chars, protected):
        if not prot and ch.isspace():
            if not prev_space:
                out.append(" ")
            prev_space = True
            continue
        out.append(ch)
        prev_space = False
    return "".join(out).strip()


def symbol_hash(body: str, family: str) -> str:
    return hashlib.sha256(normalize_for_hash(body, family).encode("utf-8")).hexdigest()
