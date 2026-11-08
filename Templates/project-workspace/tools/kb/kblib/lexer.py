"""Comment and string masking per language family.

mask() returns text of the same length with the same newlines: comments become
spaces, string/char literal contents become spaces (quotes kept). Structure
scanners (outline, symbols) then look for braces and semicolons safely.
"""
from __future__ import annotations

import io
import re
import tokenize
from typing import List, Tuple

Span = Tuple[str, int, int]  # (kind 'comment'|'string', start, end)


def mask(text: str, family: str) -> str:
    return _apply(text, spans(text, family), strings=True)


def mask_comments(text: str, family: str) -> str:
    """Comments blanked, string literals kept (for emitting readable headers)."""
    return _apply(text, spans(text, family), strings=False)


def _apply(text: str, sp: List[Span], strings: bool) -> str:
    out = list(text)
    for kind, a, b in sp:
        if kind == "string" and not strings:
            continue
        for k in range(a, b):
            if out[k] not in "\r\n":
                out[k] = " "
    return "".join(out)


def spans(text: str, family: str) -> List[Span]:
    if family == "c-like":
        return _c_spans(text)
    if family == "sql":
        return _sql_spans(text)
    if family == "python":
        return _py_spans(text)
    if family == "keyword-block":
        return _kw_spans(text)
    if family == "markup":
        return _markup_spans(text)
    return []


# --- c-like ---------------------------------------------------------------------

def _end_simple(text: str, i: int, q: str) -> int:
    """i = index after the opening quote. Returns index of the closing quote, or of the
    line end when unterminated."""
    n = len(text)
    j = i
    while j < n:
        ch = text[j]
        if ch == "\\":
            j += 2
            continue
        if ch == q or ch == "\n":
            return j
        j += 1
    return n


def _end_verbatim(text: str, i: int, holes: bool) -> int:
    n = len(text)
    j = i
    while j < n:
        ch = text[j]
        if ch == '"':
            if j + 1 < n and text[j + 1] == '"':
                j += 2
                continue
            return j
        if holes and ch == "{":
            if j + 1 < n and text[j + 1] == "{":
                j += 2
                continue
            j = _end_hole(text, j + 1) + 1
            continue
        j += 1
    return n


def _end_interpolated(text: str, i: int) -> int:
    n = len(text)
    j = i
    while j < n:
        ch = text[j]
        if ch == "\\":
            j += 2
            continue
        if ch == '"' or ch == "\n":
            return j
        if ch == "{":
            if j + 1 < n and text[j + 1] == "{":
                j += 2
                continue
            j = _end_hole(text, j + 1) + 1
            continue
        j += 1
    return n


def _end_template(text: str, i: int) -> int:
    n = len(text)
    j = i
    while j < n:
        ch = text[j]
        if ch == "\\":
            j += 2
            continue
        if ch == "`":
            return j
        if ch == "$" and j + 1 < n and text[j + 1] == "{":
            j = _end_hole(text, j + 2) + 1
            continue
        j += 1
    return n


def _end_hole(text: str, i: int) -> int:
    """i = index after '{'. Returns the index of the matching '}'."""
    n = len(text)
    depth = 1
    j = i
    while j < n:
        lit = _literal_at(text, j)
        if lit is not None:
            _kind, _a, _b, after = lit
            j = after
            continue
        ch = text[j]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return n - 1


_RAW_RE = re.compile(r'\$*("{3,})')
_REGEX_BEFORE = set("(,=:[!&|?{};~+-*%<>^")
_REGEX_WORDS = {"return", "typeof", "case", "in", "of", "yield", "await", "delete", "void", "throw", "new", "else"}


def _regex_allowed(text: str, i: int) -> bool:
    """A '/' starts a JS/TS regex literal where an expression may start, not after a value."""
    k = i - 1
    while k >= 0 and text[k] in " \t\r\n":
        k -= 1
    if k < 0:
        return True
    if text[k] in _REGEX_BEFORE:
        return True
    if text[k].isalnum() or text[k] in "_$":
        j = k
        while j >= 0 and (text[j].isalnum() or text[j] in "_$"):
            j -= 1
        return text[j + 1:k + 1] in _REGEX_WORDS
    return False


def _end_regex(text: str, i: int):
    """i = index after the opening '/'. Index of the closing '/', or None if the line ends first."""
    n = len(text)
    j = i
    in_class = False
    while j < n:
        ch = text[j]
        if ch == "\\":
            j += 2
            continue
        if ch == "\n":
            return None
        if ch == "[":
            in_class = True
        elif ch == "]":
            in_class = False
        elif ch == "/" and not in_class:
            return j if j > i else None
        j += 1
    return None


def _literal_at(text: str, i: int):
    """If a comment or literal starts at i: (kind, content_start, content_end, after)."""
    n = len(text)
    ch = text[i]
    nxt = text[i + 1] if i + 1 < n else ""
    if ch == "/" and nxt == "/":
        end = text.find("\n", i)
        end = n if end < 0 else end
        return ("comment", i, end, end)
    if ch == "/" and nxt == "*":
        end = text.find("*/", i + 2)
        end = n if end < 0 else end + 2
        return ("comment", i, end, end)
    if ch == "/" and _regex_allowed(text, i):
        end = _end_regex(text, i + 1)
        if end is not None:
            after = end + 1
            while after < n and text[after].isalpha():
                after += 1
            return ("string", i + 1, end, after)
    if ch in '$"':
        m = _RAW_RE.match(text, i)
        if m:
            q = m.group(1)
            start = m.end()
            end = text.find(q, start)
            end = n if end < 0 else end
            after = min(n, end + len(q))
            while after < n and text[after] == '"':  # closing run longer than opening
                after += 1
            return ("string", start, end, after)
    if (ch == "$" and nxt == "@") or (ch == "@" and nxt == "$"):
        if i + 2 < n and text[i + 2] == '"':
            end = _end_verbatim(text, i + 3, holes=True)
            return ("string", i + 3, end, min(n, end + 1))
    if ch == "@" and nxt == '"':
        end = _end_verbatim(text, i + 2, holes=False)
        return ("string", i + 2, end, min(n, end + 1))
    if ch == "$" and nxt == '"':
        end = _end_interpolated(text, i + 2)
        return ("string", i + 2, end, min(n, end + 1) if end < n and text[end] == '"' else end)
    if ch == '"':
        end = _end_simple(text, i + 1, '"')
        return ("string", i + 1, end, min(n, end + 1) if end < n and text[end] == '"' else end)
    if ch == "'":
        end = _end_simple(text, i + 1, "'")
        if end < n and text[end] == "'":
            return ("string", i + 1, end, end + 1)
        return None  # lone apostrophe (e.g. a lifetime): not a literal
    if ch == "`":
        end = _end_template(text, i + 1)
        return ("string", i + 1, end, min(n, end + 1))
    return None


def _c_spans(text: str) -> List[Span]:
    out: List[Span] = []
    n = len(text)
    i = 0
    while i < n:
        ch = text[i]
        if ch in "/\"'`$@":
            lit = _literal_at(text, i)
            if lit is not None:
                kind, a, b, after = lit
                if b > a:
                    out.append((kind, a, b))
                i = max(after, i + 1)
                continue
        i += 1
    return out


# --- sql --------------------------------------------------------------------------

def _sql_spans(text: str) -> List[Span]:
    out: List[Span] = []
    n = len(text)
    i = 0
    while i < n:
        ch = text[i]
        if ch == "-" and text.startswith("--", i):
            end = text.find("\n", i)
            end = n if end < 0 else end
            out.append(("comment", i, end))
            i = end
            continue
        if ch == "/" and text.startswith("/*", i):
            end = text.find("*/", i + 2)
            end = n if end < 0 else end + 2
            out.append(("comment", i, end))
            i = end
            continue
        if ch == "'":
            j = i + 1
            while j < n:
                if text[j] == "'":
                    if j + 1 < n and text[j + 1] == "'":
                        j += 2
                        continue
                    break
                j += 1
            out.append(("string", i + 1, j))
            i = j + 1
            continue
        i += 1
    return out


# --- python -----------------------------------------------------------------------

def _py_spans(text: str) -> List[Span]:
    starts = [0]
    for line in text.splitlines(True):
        starts.append(starts[-1] + len(line))

    def off(pos):
        row, col = pos
        return starts[row - 1] + col if row - 1 < len(starts) else len(text)

    out: List[Span] = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            name = tokenize.tok_name.get(tok.type, "")
            a, b = off(tok.start), off(tok.end)
            if name == "COMMENT":
                out.append(("comment", a, b))
            elif name == "STRING":
                m = re.match(r"[A-Za-z]*('''|\"\"\"|'|\")", tok.string)
                q = len(m.group(1)) if m else 1
                pre = m.end() if m else 1
                if b - a >= pre + q:
                    out.append(("string", a + pre, b - q))
            elif name == "FSTRING_MIDDLE":
                out.append(("string", a, b))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return out


# --- keyword-block / markup --------------------------------------------------------

def _kw_spans(text: str) -> List[Span]:
    out: List[Span] = []
    n = len(text)
    i = 0
    while i < n:
        if text.startswith("//", i):
            end = text.find("\n", i)
            end = n if end < 0 else end
            out.append(("comment", i, end))
            i = end
            continue
        if text[i] == '"':
            j = i + 1
            while j < n and text[j] != "\n":
                if text[j] == '"':
                    if j + 1 < n and text[j + 1] == '"':
                        j += 2
                        continue
                    break
                j += 1
            out.append(("string", i + 1, j))
            i = j + 1
            continue
        i += 1
    return out


def _markup_spans(text: str) -> List[Span]:
    out: List[Span] = []
    for rx in (r"/\*.*?\*/", r"<!--.*?-->"):
        for m in re.finditer(rx, text, re.S):
            out.append(("comment", m.start(), m.end()))
    return out
