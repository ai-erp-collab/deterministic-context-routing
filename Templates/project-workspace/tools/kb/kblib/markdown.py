"""Markdown model: links, fields, headings. Pure text functions."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple
from urllib.parse import unquote


@dataclass
class Link:
    target: str
    line: int
    kind: str  # 'md' | 'path' | 'wiki'
    raw: str
    start: int
    end: int
    alias: Optional[str] = None  # wiki alias or markdown link text


_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_CODE_SPAN_RE = re.compile(r"(`+)(.+?)\1")
_WIKI_RE = re.compile(r"\[\[([^\]|\n]+)(?:\|([^\]\n]*))?\]\]")
_MD_RE = re.compile(r"\[([^\]\n]*)\]\(([^)\n]*)\)")
_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_TITLE_SUFFIX_RE = re.compile(r"\s+(\"[^\"]*\"|'[^']*')\s*$")


def _is_placeholder(target: str) -> bool:
    return "..." in target or "<" in target or ">" in target or "*" in target


def _external(target: str) -> bool:
    return bool(_SCHEME_RE.match(target)) or target.startswith("//")


def _iter_lines(text: str):
    """Yield (line_no, offset, line_without_newline, in_fence)."""
    offset = 0
    fence: Optional[str] = None
    for no, line in enumerate(text.splitlines(True), start=1):
        body = line.rstrip("\r\n")
        m = _FENCE_RE.match(body)
        if fence is None and m:
            fence = m.group(1)
            yield no, offset, body, True
        elif fence is not None:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not body[m.end():].strip():
                fence = None
            yield no, offset, body, True
        else:
            yield no, offset, body, False
        offset += len(line)


def _frontmatter_end(text: str) -> int:
    """Line number of the closing marker of a YAML front matter block, or 0 when there is none.
    The block opens with `---` on line 1 and closes with `---` or `...`."""
    lines = text.splitlines()
    if not lines or lines[0].lstrip("﻿").rstrip() != "---":
        return 0
    for no, line in enumerate(lines[1:], start=2):
        if line.rstrip() in ("---", "..."):
            return no
    return 0


def extract_links(text: str) -> List[Link]:
    """Links in the page body; YAML front matter is metadata, not links."""
    links: List[Link] = []
    front = _frontmatter_end(text)
    for no, off, body, in_fence in _iter_lines(text):
        if in_fence or no <= front:
            continue
        taken = [False] * len(body)

        def free(a: int, b: int) -> bool:
            return not any(taken[a:b])

        def take(a: int, b: int) -> None:
            for i in range(a, b):
                taken[i] = True

        found: List[Link] = []
        # inline code spans: path links or masked text
        for m in _CODE_SPAN_RE.finditer(body):
            take(m.start(), m.end())
            content = m.group(2).strip()
            if (
                content
                and " " not in content
                and (content.endswith(".md") or content.endswith("/"))
                and content != "/"
                and not _is_placeholder(content)
                and not _external(content)
            ):
                found.append(Link(content, no, "path", m.group(0), off + m.start(), off + m.end()))
        for m in _WIKI_RE.finditer(body):
            if not free(m.start(), m.end()):
                continue
            take(m.start(), m.end())
            target = m.group(1).strip()
            if not target or _is_placeholder(target):
                continue
            alias = m.group(2).strip() if m.group(2) is not None else None
            found.append(Link(target, no, "wiki", m.group(0), off + m.start(), off + m.end(), alias))
        for m in _MD_RE.finditer(body):
            if not free(m.start(), m.end()):
                continue
            take(m.start(), m.end())
            target = _TITLE_SUFFIX_RE.sub("", m.group(2)).strip()
            if not target or target.startswith("#") or _external(target) or _is_placeholder(target):
                continue
            found.append(Link(target, no, "md", m.group(0), off + m.start(), off + m.end(), m.group(1)))
        found.sort(key=lambda l: l.start)
        links.extend(found)
    return links


def split_target(target: str) -> Tuple[str, Optional[str]]:
    """Split 'path#anchor'; percent-decode the path."""
    path, sep, anchor = target.partition("#")
    return unquote(path), (anchor if sep else None)


def _before_h2(text: str) -> List[str]:
    out = []
    for no, _off, body, in_fence in _iter_lines(text):
        if not in_fence and body.startswith("## "):
            break
        out.append(body)
    return out


def field(text: str, name: str) -> Optional[str]:
    """Value of the first 'name: value' line before the first '## ' heading."""
    rx = re.compile(r"^" + re.escape(name) + r"\s*:\s*(.*?)\s*$")
    for body in _before_h2(text):
        m = rx.match(body)
        if m:
            return m.group(1)
    return None


def headings(text: str, level: int = 2) -> List[str]:
    prefix = "#" * level + " "
    out = []
    for _no, _off, body, in_fence in _iter_lines(text):
        if not in_fence and body.startswith(prefix):
            out.append(body[len(prefix):].strip())
    return out


def title(text: str) -> Optional[str]:
    h = headings(text, 1)
    return h[0] if h else None
