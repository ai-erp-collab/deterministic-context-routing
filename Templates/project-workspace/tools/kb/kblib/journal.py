"""Journaled text writes with undo. Preserves BOM and newline style."""
from __future__ import annotations

import base64
import datetime
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .workspace import KbError

BOM = b"\xef\xbb\xbf"


def decode_bytes(data: bytes, where: str = "") -> Tuple[str, bool]:
    """UTF-8 text and whether a BOM was present. Raises KbError on invalid UTF-8."""
    bom = data.startswith(BOM)
    if bom:
        data = data[len(BOM):]
    try:
        return data.decode("utf-8"), bom
    except UnicodeDecodeError as exc:
        raise KbError("%s is not valid UTF-8 (%s)" % (where or "file", exc))


def encode_text(text: str, bom: bool, crlf: bool) -> bytes:
    if crlf:
        text = re.sub(r"(?<!\r)\n", "\r\n", text)
    return (BOM if bom else b"") + text.encode("utf-8")


def read_text_file(path: Path) -> Tuple[str, bool, bool]:
    """(text with original newlines, bom, crlf)."""
    data = path.read_bytes()
    text, bom = decode_bytes(data, str(path))
    return text, bom, b"\r\n" in data


def write_text_preserving(path: Path, text: str) -> None:
    """Write text keeping the existing file's BOM and newline style (unjournaled)."""
    bom, crlf = False, False
    if path.is_file():
        data = path.read_bytes()
        bom, crlf = data.startswith(BOM), b"\r\n" in data
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode_text(text, bom, crlf))


def _splice(before: str, new_text: str, crlf: bool) -> str:
    """Keep the original text outside the changed span byte for byte; only the inserted
    span takes the file's newline style (mixed-ending files stay as they were)."""
    n = min(len(before), len(new_text))
    p = 0
    while p < n and before[p] == new_text[p]:
        p += 1
    s = 0
    while s < n - p and before[len(before) - 1 - s] == new_text[len(new_text) - 1 - s]:
        s += 1
    # a shared "\n" that ended "\r\n" in the old text but a bare line in the new one is new text
    while s > 0 and before[len(before) - s] == "\n" and before[len(before) - s - 1:len(before) - s] == "\r" \
            and new_text[len(new_text) - s - 1:len(new_text) - s] != "\r":
        s -= 1
    middle = new_text[p:len(new_text) - s]
    if crlf and middle:
        lead = "\r" if p > 0 and before[p - 1] == "\r" and middle.startswith("\n") else ""
        middle = re.sub(r"(?<!\r)\n", "\r\n", middle)
        if lead and middle.startswith("\r\n"):
            middle = middle[1:]
    return before[:p] + middle + before[len(before) - s:]


def _changed_lines(old: str, new: str) -> Tuple[str, str]:
    a, b = old.splitlines(), new.splitlines()
    i = 0
    while i < len(a) and i < len(b) and a[i] == b[i]:
        i += 1
    j = 0
    while j < len(a) - i and j < len(b) - i and a[len(a) - 1 - j] == b[len(b) - 1 - j]:
        j += 1
    return " / ".join(a[i:len(a) - j]), " / ".join(b[i:len(b) - j])


class Journal:
    def __init__(self, ws, dry_run: bool = False):
        self.ws = ws
        self.dry_run = dry_run
        self.run_id: Optional[str] = None
        self.command = ""
        self.overlay: Dict[str, Tuple[str, bool, bool]] = {}
        self.edits: List[Tuple[str, str, str]] = []

    @property
    def journal_dir(self) -> Path:
        return self.ws.data_dir / "journal"

    def start_run(self, command: str) -> str:
        now = datetime.datetime.now()
        self.run_id = now.strftime("%Y%m%d-%H%M%S") + "-" + os.urandom(2).hex()
        self.command = command
        return self.run_id

    def _state(self, relpath: str) -> Optional[Tuple[str, bool, bool]]:
        if relpath in self.overlay:
            return self.overlay[relpath]
        p = self.ws.root / relpath
        if not p.is_file():
            return None
        return read_text_file(p)

    def exists(self, relpath: str) -> bool:
        return self._state(relpath) is not None

    def read_text(self, relpath: str) -> str:
        st = self._state(relpath)
        if st is None:
            raise KbError("%s does not exist" % relpath)
        return st[0]

    def write_text(self, relpath: str, new_text: str, rule: str) -> None:
        if self.run_id is None:
            self.start_run(rule)
        st = self._state(relpath)
        before, bom, crlf = (st if st is not None else (None, False, False))
        after = new_text if before is None else _splice(before, new_text, crlf)
        if before == after:
            return
        old_seg, new_seg = _changed_lines(before or "", after)
        self.edits.append((relpath, old_seg, new_seg))
        self.overlay[relpath] = (after, bom, crlf)
        if self.dry_run:
            return
        path = self.ws.root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encode_text(after, bom, False))  # newlines already settled by _splice
        self._append({"file": relpath, "rule": rule, "before": before, "after": after, "bom": bom})

    def copy_file(self, src: Path, relpath: str, rule: str, overwrite: bool = False) -> None:
        """Copy a (possibly binary) file into the workspace; journaled by hash.
        With overwrite=True the previous bytes are kept in the journal so undo restores them."""
        if self.run_id is None:
            self.start_run(rule)
        dest = self.ws.root / relpath
        if (dest.exists() or relpath in self.overlay) and not overwrite:
            raise KbError("%s already exists" % relpath)
        data = Path(src).read_bytes()
        before = dest.read_bytes() if dest.is_file() else None
        self.edits.append((relpath, "(new file)" if before is None else "(replaced)", "copy of %s" % src))
        self.overlay[relpath] = ("", False, False)
        if self.dry_run:
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        rec = {"file": relpath, "rule": rule, "before": None, "after": None, "binary": True,
               "sha256": hashlib.sha256(data).hexdigest()}
        if before is not None:
            rec["before_b64"] = base64.b64encode(before).decode("ascii")
        self._append(rec)

    def delete_file(self, relpath: str, rule: str) -> None:
        """Delete a workspace file; its bytes stay in the journal so undo restores them."""
        if self.run_id is None:
            self.start_run(rule)
        p = self.ws.root / relpath
        if not p.is_file():
            return
        before = p.read_bytes()
        self.edits.append((relpath, "(file)", "(deleted)"))
        if self.dry_run:
            return
        p.unlink()
        self._append({"file": relpath, "rule": rule, "before": None, "after": None, "binary": True,
                      "deleted": True, "before_b64": base64.b64encode(before).decode("ascii")})

    def _append(self, record: dict) -> None:
        self.ws.make_data_dir()
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.datetime.now()
        rec = {"run": self.run_id, "time": now.isoformat(timespec="seconds"), "command": self.command}
        rec.update(record)
        with open(self.journal_dir / (now.strftime("%Y-%m-%d") + ".jsonl"), "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def entries(self, run_id: str) -> List[dict]:
        out = []
        if not self.journal_dir.is_dir():
            return out
        for jf in sorted(self.journal_dir.glob("*.jsonl")):
            for line in jf.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("run") == run_id:
                    out.append(rec)
        return out

    def changed_since(self, run_ids: List[str]) -> List[str]:
        """Files whose current bytes differ from what the last of these runs wrote."""
        last: Dict[str, dict] = {}
        for rid in run_ids:
            for rec in self.entries(rid):
                last[rec["file"]] = rec
        return self._changed(last)

    def _changed(self, last: Dict[str, dict]) -> List[str]:
        changed = []
        for f, rec in last.items():
            p = self.ws.root / f
            if rec.get("deleted"):
                if p.exists():
                    changed.append(f)
                continue
            if rec.get("binary"):
                if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != rec["sha256"]:
                    changed.append(f)
                continue
            expected = encode_text(rec["after"], rec.get("bom", False), False)
            if not p.is_file() or p.read_bytes() != expected:
                changed.append(f)
        return sorted(changed)

    def undo(self, run_id: str) -> List[str]:
        recs = self.entries(run_id)
        if not recs:
            raise KbError("no journal entries for run %s" % run_id)
        first: Dict[str, dict] = {}
        last: Dict[str, dict] = {}
        for rec in recs:
            first.setdefault(rec["file"], rec)
            last[rec["file"]] = rec
        changed = self._changed(last)
        if changed:
            raise KbError("run %s not undone; changed since: %s" % (run_id, ", ".join(sorted(changed))))
        self.start_run("undo " + run_id)
        restored = []
        for f in reversed(list(first.keys())):
            rec = first[f]
            p = self.ws.root / f
            if rec.get("before_b64") is not None:
                p.write_bytes(base64.b64decode(rec["before_b64"]))
            elif rec["before"] is None:
                p.unlink()
            else:
                p.write_bytes(encode_text(rec["before"], rec.get("bom", False), False))
            if last[f].get("binary"):
                self._append({"file": f, "rule": "undo", "before": None, "after": None, "binary": True,
                              "removed_sha256": last[f].get("sha256", "")})
            else:
                self._append({"file": f, "rule": "undo", "before": last[f]["after"], "after": rec["before"],
                              "bom": rec.get("bom", False)})
            restored.append(f)
        return restored
