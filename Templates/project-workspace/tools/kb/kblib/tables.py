"""Table exports: readers, column profiles, `table learn`, table page generation."""
from __future__ import annotations

import csv
import io
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional, Tuple

from .workspace import KbError

ROLES = ("field", "description", "type", "length", "precision", "nullable", "key_position", "sample",
         "sub_table", "notes")
NULLABLE_TRUE = ["v", "yes", "y", "1", "true"]
SS_NS = "urn:schemas-microsoft-com:office:spreadsheet"


# --- readers ---------------------------------------------------------------------

def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _col_index(ref: str) -> int:
    letters = re.match(r"[A-Za-z]+", ref)
    n = 0
    for ch in (letters.group(0) if letters else ""):
        n = n * 26 + (ord(ch.upper()) - 64)
    return n - 1


def _put(rows: List[List[str]], r: int, c: int, value: str) -> None:
    while len(rows) <= r:
        rows.append([])
    row = rows[r]
    while len(row) <= c:
        row.append("")
    row[c] = value


def _text_of(el) -> str:
    return "".join(t.text or "" for t in el.iter() if _local(t.tag) == "t")


def _read_xlsx(path: Path) -> List[List[str]]:
    with zipfile.ZipFile(str(path)) as z:
        names = z.namelist()
        shared: List[str] = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = [_text_of(si) for si in root if _local(si.tag) == "si"]
        sheet = None
        if "xl/workbook.xml" in names and "xl/_rels/workbook.xml.rels" in names:
            wb = ET.fromstring(z.read("xl/workbook.xml"))
            rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
            targets = {r.get("Id"): r.get("Target") for r in rels}
            for el in wb.iter():
                if _local(el.tag) == "sheet":
                    rid = next((v for k, v in el.attrib.items() if _local(k) == "id"), None)
                    target = targets.get(rid)
                    if target:
                        target = target.lstrip("/")
                        sheet = target if target.startswith("xl/") else "xl/" + target
                    break
        if sheet is None or sheet not in names:
            sheets = sorted((n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml$", n)),
                            key=lambda n: int(re.findall(r"\d+", n)[-1]))
            if not sheets:
                raise KbError("%s has no worksheet" % path.name)
            sheet = sheets[0]
        root = ET.fromstring(z.read(sheet))
    rows: List[List[str]] = []
    next_row = 0
    for row in root.iter():
        if _local(row.tag) != "row":
            continue
        r = int(row.get("r")) - 1 if row.get("r") else next_row
        next_row = r + 1
        while len(rows) <= r:
            rows.append([])
        next_col = 0
        for cell in row:
            if _local(cell.tag) != "c":
                continue
            c = _col_index(cell.get("r")) if cell.get("r") else next_col
            next_col = c + 1
            t = cell.get("t")
            v = next((x.text or "" for x in cell if _local(x.tag) == "v"), "")
            if t == "s":
                value = shared[int(v)] if v.strip().isdigit() and int(v) < len(shared) else ""
            elif t == "inlineStr":
                value = "".join(_text_of(x) for x in cell if _local(x.tag) == "is")
            else:
                value = v
            _put(rows, r, c, value)
    return rows


def _read_spreadsheetml(root) -> List[List[str]]:
    table = next((el for el in root.iter() if _local(el.tag) == "Table"), None)
    if table is None:
        return []
    rows: List[List[str]] = []
    r = -1
    for row in table:
        if _local(row.tag) != "Row":
            continue
        idx = row.get("{%s}Index" % SS_NS)
        r = int(idx) - 1 if idx else r + 1
        while len(rows) <= r:
            rows.append([])
        c = -1
        for cell in row:
            if _local(cell.tag) != "Cell":
                continue
            cidx = cell.get("{%s}Index" % SS_NS)
            c = int(cidx) - 1 if cidx else c + 1
            data = next((x for x in cell if _local(x.tag) == "Data"), None)
            value = "".join(data.itertext()) if data is not None else ""
            _put(rows, r, c, value)
    return rows


def decode_text(data: bytes, hint: Optional[str]) -> str:
    if data.startswith(b"\xef\xbb\xbf"):
        return data[3:].decode("utf-8", errors="replace")
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    if len(data) >= 4:
        even, odd = data[0::2].count(0), data[1::2].count(0)
        half = len(data) // 2
        if odd >= half * 0.2 and even == 0:
            return data.decode("utf-16-le", errors="replace")
        if even >= half * 0.2 and odd == 0:
            return data.decode("utf-16-be", errors="replace")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        if hint:
            try:
                return data.decode(hint)
            except (LookupError, UnicodeDecodeError) as exc:
                raise KbError("cannot decode with %s: %s" % (hint, exc))
        raise KbError("not UTF-8 or UTF-16; record the code page in the profile (`--encoding`)")


def _sniff_delimiter(text: str) -> str:
    lines = [ln for ln in text.splitlines() if ln.strip()][:20]
    best, best_n = ",", -1
    for d in ("\t", ";", ","):
        n = sum(1 for ln in lines if d in ln)
        if n > best_n:
            best, best_n = d, n
    return best


def read_rows(path: Path, encoding_hint: Optional[str]) -> List[List[str]]:
    path = Path(path)
    ext = path.suffix.lower()
    if ext in (".xlsx", ".xlsm"):
        try:
            return _read_xlsx(path)
        except (zipfile.BadZipFile, ET.ParseError, KeyError, ValueError) as exc:
            raise KbError("%s is not a readable .xlsx: %s" % (path.name, exc))
    data = path.read_bytes()
    if ext == ".xml":
        try:
            root = ET.fromstring(data)
        except ET.ParseError as exc:
            raise KbError("%s is not well-formed XML: %s" % (path.name, exc))
        if _local(root.tag) != "Workbook":
            raise KbError("%s is XML but not a SpreadsheetML workbook" % path.name)
        return _read_spreadsheetml(root)
    if ext in (".csv", ".tsv", ".txt"):
        text = decode_text(data, encoding_hint)
        delim = "\t" if ext == ".tsv" else _sniff_delimiter(text)
        return [[c.strip() for c in row] for row in csv.reader(io.StringIO(text), delimiter=delim)]
    raise KbError("unsupported export format %s (xlsx, SpreadsheetML xml, csv, tsv, txt)" % ext)


# --- profiles ----------------------------------------------------------------------

def load_profiles(ws) -> Dict[str, dict]:
    out = {}
    folder = ws.data_dir / "profiles"
    if folder.is_dir():
        for p in sorted(folder.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except ValueError:
                continue
            if isinstance(data, dict) and "columns" in data and "field" in data["columns"]:
                out[data.get("name") or p.stem] = data
    return out


def detect_profile(rows: List[List[str]], profiles: Dict[str, dict]) -> Optional[Tuple[str, int]]:
    """(profile name, 1-based header row) of the best match, or None."""
    best = None
    for name in sorted(profiles):
        prof = profiles[name]
        keywords = {k.casefold() for k in prof.get("header_keywords", [])}
        if not keywords:
            continue
        need = min(3, len(keywords))
        placed = prof.get("column_headers") or {}
        for r, row in enumerate(rows[:int(prof.get("header_search_rows", 10))]):
            cells = {c.strip().casefold() for c in row if c.strip()}
            hits = len(keywords & cells)
            if placed and any(_cell(row, prof["columns"].get(role)).casefold() != head
                              for role, head in placed.items()):
                continue  # same words, different column order: not this layout
            if hits >= need and (best is None or hits > best[2]):
                best = (name, r + 1, hits)
    return (best[0], best[1]) if best else None


def _cell(row: List[str], col: Optional[int]) -> str:
    if not col or col < 1 or col > len(row):
        return ""
    return row[col - 1].strip()


def parse_fields(rows: List[List[str]], prof: dict, header_row: int) -> List[Dict[str, str]]:
    cols = prof["columns"]
    out = []
    for row in rows[header_row:]:
        rec = {role: _cell(row, cols.get(role)) for role in ROLES}
        if rec["field"]:
            out.append(rec)
    return out


def header_candidates(rows: List[List[str]], n: int = 5) -> List[Tuple[int, List[str]]]:
    scored = []
    for r, row in enumerate(rows[:20]):
        score = sum(1 for c in row if c.strip() and len(c.strip()) <= 40
                    and not re.match(r"^[\d\s.,+-]+$", c.strip()))
        if score:
            scored.append((score, r, row))
    top = sorted(scored, key=lambda t: (-t[0], t[1]))[:n]
    return [(r + 1, row) for _s, r, row in sorted(top, key=lambda t: t[1])]


def format_row(r: int, row: List[str]) -> str:
    return "row %d: %s" % (r, " | ".join("%d=%s" % (k + 1, c.strip()) for k, c in enumerate(row) if c.strip()))


def learn(ws, export: Path, name: str, header_row: int, mapping: Dict[str, int],
          encoding: Optional[str]) -> Tuple[Optional[dict], List[Dict[str, str]], str]:
    """Returns (profile or None, parsed fields, error message)."""
    unknown = [k for k in mapping if k not in ROLES]
    if unknown:
        return None, [], "unknown roles: %s (roles: %s)" % (", ".join(unknown), ", ".join(ROLES))
    if "field" not in mapping:
        return None, [], "`field` must be mapped"
    rows = read_rows(export, encoding)
    if header_row < 1 or header_row > len(rows) or not any(c.strip() for c in rows[header_row - 1]):
        return None, [], "header row %d is empty or outside the export" % header_row
    header = rows[header_row - 1]
    bad = [k for k, i in mapping.items() if i < 1 or i > len(header) or not header[i - 1].strip()]
    if bad:
        return None, [], "mapped columns not in header row %d: %s" % (
            header_row, ", ".join("%s=%d" % (k, mapping[k]) for k in bad))
    prof = {
        "name": name,
        "header_keywords": sorted({header[i - 1].strip().casefold() for i in mapping.values()}),
        "column_headers": {role: header[i - 1].strip().casefold() for role, i in mapping.items()},
        "header_search_rows": max(10, header_row),
        "columns": dict(mapping),
        "nullable_true": list(NULLABLE_TRUE),
        "encoding": encoding,
        "table_name_from": "filename",
    }
    fields = parse_fields(rows, prof, header_row)
    if not fields:
        return None, [], "no field rows parsed below header row %d" % header_row
    return prof, fields, ""


# --- pages --------------------------------------------------------------------------

def field_line(rec: Dict[str, str], prof: dict) -> str:
    typ = rec["type"]
    size = ",".join(x for x in (rec["length"], rec["precision"]) if x)
    if typ and size:
        typ = "%s(%s)" % (typ, size)
    flags = []
    if rec["key_position"]:
        flags.append("key")
    nullable = rec["nullable"].casefold()
    if nullable:
        flags.append("null" if nullable in [v.casefold() for v in prof.get("nullable_true", NULLABLE_TRUE)]
                     else "required")
    head = "- `%s`" % rec["field"]
    if typ or flags:
        head += " " + " ".join(([typ] if typ else []) + flags)
    desc = "; ".join(x for x in (rec["description"], rec["notes"]) if x)
    return head + (": " + desc if desc else "")


def table_name(export: Path, rows: List[List[str]], prof: dict) -> str:
    rule = prof.get("table_name_from") or "filename"
    m = re.match(r"cell:(\d+),(\d+)$", rule)
    if m:
        r, c = int(m.group(1)), int(m.group(2))
        if r <= len(rows) and c <= len(rows[r - 1]) and rows[r - 1][c - 1].strip():
            return rows[r - 1][c - 1].strip()
    return export.stem


def group_tables(main: str, fields: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    groups: Dict[str, List[Dict[str, str]]] = {main: []}
    for rec in fields:
        name = "%s.%s" % (main, rec["sub_table"]) if rec["sub_table"] else main
        groups.setdefault(name, []).append(rec)
    return {k: v for k, v in groups.items() if v}


def render_page(name: str, source: str, recs: List[Dict[str, str]], prof: dict) -> str:
    keys = ["- `%s`: key position %s" % (r["field"], r["key_position"]) for r in recs if r["key_position"]]
    return "\n".join([
        "# %s" % name, "",
        "kind: table",
        "source: %s" % source,
        "status: partial",
        "confidence: schema-confirmed",
        "", "## Purpose", "",
        "- (business meaning not curated yet; confidence above covers structure only)",
        "", "## Keys", "",
    ] + (keys or ["- none recorded"]) + [
        "", "## Fields", "",
    ] + [field_line(r, prof) for r in recs] + [
        "", "## Relations", "",
        "- none recorded",
        "", "## Evidence", "",
        "- `%s` (table export)" % source,
        "",
    ])


_FIELD_NAME = re.compile(r"^\s*-\s+`([^`]+)`")
_FIELD_PARTS = re.compile(r"^\s*-\s+`([^`]+)`([^:]*)(?::\s*(.*))?$")
GONE = " (not in the latest export)"


def _merge_line(old: str, new: str) -> str:
    """Structure (type, size, flags) from the export; curated description from the page."""
    om, nm = _FIELD_PARTS.match(old), _FIELD_PARTS.match(new)
    if not om or not nm or not (om.group(3) or "").strip():
        return new
    desc = om.group(3).strip()
    if desc.endswith(GONE):
        desc = desc[:-len(GONE)]
    return "- `%s`%s: %s" % (nm.group(1), nm.group(2).rstrip(), desc)


def replace_fields(text: str, new_lines: List[str]) -> Tuple[str, List[str]]:
    """Merge the export's fields into the `## Fields` section; returns (new text, diff lines).
    Curated descriptions and prose stay; fields missing from the export are kept and marked."""
    lines = text.split("\n")
    start = next((k for k, ln in enumerate(lines) if ln.rstrip("\r") == "## Fields"), None)
    if start is None:
        old_lines: List[str] = []
    else:
        end = start + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        old_lines = [ln.rstrip("\r") for ln in lines[start + 1:end]]
    old: Dict[str, str] = {}
    prose: List[str] = []
    for ln in old_lines:
        m = _FIELD_NAME.match(ln)
        if m:
            old[m.group(1)] = ln.strip()
        elif ln.strip():
            prose.append(ln)
    merged: List[str] = []
    new: Dict[str, str] = {}
    for ln in new_lines:
        m = _FIELD_NAME.match(ln)
        name = m.group(1) if m else ln
        line = _merge_line(old[name], ln) if name in old else ln
        new[name] = line
        merged.append(line)
    gone = [k for k in old if k not in new]
    for k in gone:
        merged.append(old[k] if old[k].endswith(GONE) else old[k] + GONE)
    section = [""] + prose + merged + [""]
    if start is None:
        body = text.rstrip("\n") + "\n\n## Fields\n" + "\n".join(section) + "\n"
    else:
        body = "\n".join(lines[:start + 1] + section + lines[end:])
    diff = ["+ `%s`" % k for k in new if k not in old]
    diff += ["- `%s`" % k for k in gone if not old[k].endswith(GONE)]
    diff += ["~ `%s`" % k for k in new if k in old and old[k] != new[k]]
    return body, diff


def page_folder(ws, module: Optional[str], shared: bool) -> str:
    if shared:
        return "knowledge-base/shared/tables"
    for m in ws.modules:
        if m.name == module and m.wiki and "<" not in m.wiki:
            return m.wiki.rstrip("/") + "/tables"
    return "knowledge-base/modules/%s/tables" % module


def source_for(ws, export_rel: str) -> Tuple[str, bool]:
    """(registry copy path, registered?)"""
    from .artifacts import Registry
    reg = Registry.load(ws)
    for row in reg.rows.values():
        if row.copy == export_rel or row.origin == export_rel:
            return row.copy, True
    return export_rel, False


def export_rel(ws, path: Path) -> str:
    try:
        return path.resolve().relative_to(ws.root).as_posix()
    except ValueError:
        return PurePosixPath(path.as_posix()).as_posix()
