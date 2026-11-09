"""kb: knowledge-base integrity tool. Usage: python tools/kb/kb.py <command> [options]."""
from __future__ import annotations

import argparse
import contextlib
import datetime
import io
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple

sys.dont_write_bytecode = True  # no __pycache__ in the workspace

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from kblib import checks  # noqa: E402
from kblib import issues as issues_mod  # noqa: E402
from kblib import links  # noqa: E402,F401  (registers checks 2-4)
from kblib import resolve  # noqa: E402  (registers check 15)
from kblib import pages  # noqa: E402,F401  (registers checks 7-8)
from kblib import artifacts  # noqa: E402  (registers checks 9-11, 13)
from kblib import outline  # noqa: E402
from kblib import doctor  # noqa: E402  (registers check 14)
from kblib import recipe, symbols  # noqa: E402  (recipe registers check 12)
from kblib import tables  # noqa: E402
from kblib import hooks  # noqa: E402
from kblib import upgrade  # noqa: E402  (registers check 16)
from kblib.journal import Journal  # noqa: E402
from kblib.workspace import KbError, NoWorkspace, Workspace  # noqa: E402

# name -> (add_args(parser), handler(ws, args) -> int)
COMMANDS: Dict[str, Tuple[Callable[[argparse.ArgumentParser], None], Callable]] = {}


def _root_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--root", default=argparse.SUPPRESS, help="workspace root (default: walk up from cwd)")


# --- root -----------------------------------------------------------------

def _root_add(p: argparse.ArgumentParser) -> None:
    pass


def _root_run(ws: Workspace, args) -> int:
    print("kb root: %s" % ws.root)
    return 0


COMMANDS["root"] = (_root_add, _root_run)


# --- shared helpers -----------------------------------------------------------

def changed_paths(ws: Workspace, paths: Optional[List[str]]) -> Optional[Set[str]]:
    """Normalize --changed values to workspace-relative posix paths."""
    if paths is None:
        return None
    out = set()
    for p in paths:
        pp = Path(p)
        if pp.is_absolute():
            try:
                out.add(ws.rel(pp))
            except ValueError:
                continue
        else:
            out.add(pp.as_posix())  # Path() already drops a leading "./"
    return out


def parse_only(value: Optional[str]) -> Optional[Set[int]]:
    if not value:
        return None
    try:
        return {int(x) for x in value.replace(" ", "").split(",") if x}
    except ValueError:
        raise KbError("--only takes check numbers like 2,4")


summary_line = issues_mod.summary_line


# --- check --------------------------------------------------------------------

def _check_add(p: argparse.ArgumentParser) -> None:
    p.add_argument("--changed", nargs="+", metavar="P", help="limit to these workspace paths")
    p.add_argument("--summary", action="store_true", help="print only; write no report")
    p.add_argument("--json", action="store_true", help="print issues as JSON after the summary line")
    p.add_argument("--only", metavar="N,N", help="run only these check numbers")


def _check_run(ws: Workspace, args) -> int:
    changed = changed_paths(ws, args.changed)
    only = parse_only(args.only)
    issues = checks.run_checks(ws, checks.Scope(changed), only)
    print(summary_line("check", issues))
    full = changed is None and only is None and not args.summary
    ids = {}
    if full:
        report = issues_mod.write_reports(ws, issues, datetime.date.today().isoformat())
        ids = {row["key"]: row["id"] for row in issues_mod.load_state(ws)["open"]}
        if issues:
            print("report: %s" % ws.rel(report))
    if args.json:
        print(json.dumps([dict(asdict(i), key=i.key, id=ids.get(i.key)) for i in issues], ensure_ascii=False, indent=1))
    else:
        for i in issues:
            prefix = "#%d " % ids[i.key] if i.key in ids else ""
            print("%s[%s] %s: %s" % (prefix, i.severity, i.file, i.symptom))
    return 1 if issues else 0


COMMANDS["check"] = (_check_add, _check_run)


# --- fix ----------------------------------------------------------------------

def _fix_add(p: argparse.ArgumentParser) -> None:
    p.add_argument("--safe", action="store_true", help="apply every safe fix")
    p.add_argument("--ids", nargs="+", type=int, metavar="N", help="apply the proposed fix of these issue ids")
    p.add_argument("--dry-run", action="store_true", help="print the edits; write nothing")
    p.add_argument("--changed", nargs="+", metavar="P", help="limit to these workspace paths")
    p.add_argument("--only", metavar="N,N", help="limit to these check numbers")


def _fix_run(ws: Workspace, args) -> int:
    if not args.safe and not args.ids:
        raise KbError("pass --safe or --ids N...")
    issues = checks.run_checks(ws, checks.Scope(changed_paths(ws, args.changed)), parse_only(args.only))
    selected, unfixable = [], []
    if args.ids:
        by_id = {row["id"]: row["key"] for row in issues_mod.load_state(ws)["open"]}
        current = {i.key: i for i in issues}
        for n in args.ids:
            if n not in by_id:
                unfixable.append("#%d: unknown issue id; run kb check for the current numbers" % n)
            elif by_id[n] not in current:
                unfixable.append("#%d: no longer found; run kb check" % n)
            elif not current[by_id[n]].fix:
                unfixable.append("#%d: no automatic fix; resolve it by hand (see docs/checks/OPEN.md)" % n)
            elif current[by_id[n]] not in selected:
                selected.append(current[by_id[n]])
    if args.safe:
        selected += [i for i in issues if i.fix and i.fix.get("safe") and i not in selected]
    journal = Journal(ws, dry_run=args.dry_run)
    run_id = journal.start_run("fix")
    notes = io.StringIO()
    with contextlib.redirect_stdout(notes):  # the summary line comes first
        skipped = {}
        applied = checks.apply_fixes(ws, selected, journal, safe_only=False, skipped=skipped)
    if args.dry_run:
        print("kb fix: %d edits would be made (dry run, nothing written)" % len(journal.edits))
    else:
        n_edits = len(journal.edits)
        print("kb fix: %d fix%s applied, %d file edit%s%s, run_id: %s" % (
            applied, "" if applied == 1 else "es", n_edits, "" if n_edits == 1 else "s",
            " (the files already held the fixed text)" if applied and not n_edits else "", run_id))
    for edit in journal.edits:
        print("%s: %s -> %s" % edit)
    if args.ids:
        key_ids = {by_id[n]: n for n in args.ids if n in by_id}
        unfixable += ["#%d: no automatic fix (%s); resolve it by hand (see docs/checks/OPEN.md)" % (key_ids[k], why)
                      for k, why in skipped.items() if k in key_ids]
    for line in unfixable:
        print(line)
    sys.stdout.write(notes.getvalue())
    return 1 if unfixable else 0


COMMANDS["fix"] = (_fix_add, _fix_run)


# --- undo ---------------------------------------------------------------------

def _undo_add(p: argparse.ArgumentParser) -> None:
    p.add_argument("run_id", help="run id printed by fix")


def _undo_run(ws: Workspace, args) -> int:
    restored = Journal(ws).undo(args.run_id)
    print("kb undo: %d files restored, run_id: %s" % (len(restored), args.run_id))
    for f in restored:
        print(f)
    return 0


COMMANDS["undo"] = (_undo_add, _undo_run)


# --- resolve ------------------------------------------------------------------

def _resolve_add(p: argparse.ArgumentParser) -> None:
    p.add_argument("query", help="name, alias, term, or transliteration to look up")
    p.add_argument("--domain", help="only pages of this domain/module")
    p.add_argument("--kind", help="only pages of this kind (table, class, term, ...)")
    p.add_argument("--top", type=int, default=5, help="number of hits (default 5)")
    p.add_argument("--fulltext", action="store_true", help="also match page text")
    p.add_argument("--json", action="store_true", help="print hits as JSON after the summary line")


def _resolve_run(ws: Workspace, args) -> int:
    hits = resolve.query(ws, args.query, args.domain, args.kind, args.top, args.fulltext)
    min_score = float(ws.config.get("resolve_min_score", 0.75))
    confident = [h for h in hits if h.score >= min_score]
    print("kb resolve: %d confident hit%s for `%s` (%d shown)"
          % (len(confident), "" if len(confident) == 1 else "s", args.query, len(hits)))
    if args.json:
        print(json.dumps([resolve.hit_dict(h) for h in hits], ensure_ascii=False, indent=1))
    else:
        for h in hits:
            print("%.2f  %s  [%s, %s]  %s: %s" % (h.score, h.path, h.kind or "-", h.domain or "-", h.name, h.why))
    return 0 if confident else 1


COMMANDS["resolve"] = (_resolve_add, _resolve_run)


# --- config -------------------------------------------------------------------

# name -> (add_args, handler(ws, args) -> int); later tasks add entries
CONFIG_COMMANDS: Dict[str, Tuple[Callable[[argparse.ArgumentParser], None], Callable]] = {}


def _accept_dup_add(p: argparse.ArgumentParser) -> None:
    p.add_argument("paths", nargs="+", metavar="path", help="the duplicate pages (two or more)")


def _accept_dup_run(ws: Workspace, args) -> int:
    paths = sorted({Path(p).as_posix() for p in args.paths})
    if len(paths) < 2:
        raise KbError("accept-duplicate needs at least two different paths")
    missing = [p for p in paths if not (ws.root / p).is_file()]
    if missing:
        raise KbError("not found: %s" % ", ".join(missing))
    accepted = ws.config.setdefault("accepted_duplicates", [])
    if paths in accepted:
        print("kb config: duplicate already accepted")
        return 0
    accepted.append(paths)
    ws.save_config()
    print("kb config: accepted duplicate %s" % " + ".join(paths))
    return 0


CONFIG_COMMANDS["accept-duplicate"] = (_accept_dup_add, _accept_dup_run)


def user_path(ws: Workspace, p: str) -> Path:
    """A path argument: absolute, relative to cwd if it exists there, else relative to the root."""
    cand = Path(p)
    if cand.is_absolute():
        return cand
    if cand.exists():
        return cand.resolve()
    return (ws.root / p).resolve()


def _family_add(p: argparse.ArgumentParser) -> None:
    p.add_argument("ext", help="file extension, e.g. .xyz")
    p.add_argument("family", help="one of: %s" % ", ".join(outline.FAMILIES))
    p.add_argument("--start", help="keyword-block: regex of a block start line")
    p.add_argument("--end", help="keyword-block: regex of a block end line")
    p.add_argument("--sample", help="outline this file first; refuse if the outline is empty")


def _family_run(ws: Workspace, args) -> int:
    import copy
    import re as _re

    ext = outline.norm_ext(args.ext)
    if args.family not in outline.FAMILIES:
        raise KbError("unknown family `%s`; families: %s" % (args.family, ", ".join(outline.FAMILIES)))
    cfg = copy.deepcopy(ws.config)
    cfg.setdefault("families", {})[ext] = args.family
    if args.family == "keyword-block":
        if not args.start or not args.end:
            raise KbError("keyword-block needs --start RE and --end RE")
        for rx in (args.start, args.end):
            try:
                _re.compile(rx)
            except _re.error as exc:
                raise KbError("bad regex `%s`: %s" % (rx, exc))
        cfg.setdefault("keyword_blocks", {})[ext] = {"start": args.start, "end": args.end}
    if args.sample:
        sample = user_path(ws, args.sample)
        if not sample.is_file():
            raise KbError("sample %s not found" % args.sample)
        text = sample.read_bytes().decode("utf-8-sig", errors="replace")
        body = outline.outline_text(text, args.family, cfg, ext)
        if not body.strip():
            print("kb config: outline of %s with family %s is empty; nothing saved" % (args.sample, args.family))
            return 1
    ws.config = cfg
    ws.save_config()
    print("kb config: %s -> %s" % (ext, args.family))
    return 0


CONFIG_COMMANDS["family"] = (_family_add, _family_run)


def _config_add(p: argparse.ArgumentParser) -> None:
    sub = p.add_subparsers(dest="config_command", parser_class=_Parser)
    for name, (add_args, _h) in CONFIG_COMMANDS.items():
        sp = sub.add_parser(name)
        _root_args(sp)
        add_args(sp)


def _config_run(ws: Workspace, args) -> int:
    name = getattr(args, "config_command", None)
    if not name:
        raise KbError("config needs a subcommand: %s" % ", ".join(CONFIG_COMMANDS))
    return CONFIG_COMMANDS[name][1](ws, args)


COMMANDS["config"] = (_config_add, _config_run)


# --- ingest -------------------------------------------------------------------

def _ingest_add(p: argparse.ArgumentParser) -> None:
    p.add_argument("paths", nargs="+", metavar="path", help="evidence files or folders (every file under them) to copy into source-artifacts/")
    p.add_argument("--module", required=True, help="module name from modules.md")
    p.add_argument("--kind", choices=artifacts.KINDS, help="artifact kind (default: from the extension)")


def _ingest_run(ws: Workspace, args) -> int:
    journal = Journal(ws)
    run_id = journal.start_run("ingest")
    rows = artifacts.ingest(ws, args.paths, args.module, args.kind, journal)
    print("kb ingest: %d file%s registered, run_id: %s" % (len(rows), "" if len(rows) == 1 else "s", run_id))
    for r in rows:
        print("%s -> %s" % (r.origin, r.copy))
    return 0


COMMANDS["ingest"] = (_ingest_add, _ingest_run)


# --- outline ------------------------------------------------------------------

def _outline_add(p: argparse.ArgumentParser) -> None:
    p.add_argument("file", help="source file to outline")
    p.add_argument("--out", help="write the outline to this file instead of stdout")


def _outline_run(ws: Workspace, args) -> int:
    src = user_path(ws, args.file)
    if not src.is_file():
        raise KbError("%s not found" % args.file)
    result = outline.outline_file(ws, src)
    try:
        shown = ws.rel(src)
    except ValueError:
        shown = src.as_posix()
    print("kb outline: %s (tier %s, %s, %d -> %d bytes)"
          % (shown, result.tier, result.family, result.size_before, result.size_after))
    if args.out:
        dest = user_path(ws, args.out)
        try:
            rel = ws.rel(dest)
        except ValueError:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(result.text.encode("utf-8"))
        else:
            journal = Journal(ws)
            journal.start_run("outline")
            journal.write_text(rel, result.text, "outline")
        print("written: %s" % args.out)
    else:
        sys.stdout.write(result.text)
    return 0


COMMANDS["outline"] = (_outline_add, _outline_run)


# --- doctor -------------------------------------------------------------------

def _doctor_add(p: argparse.ArgumentParser) -> None:
    pass


def _doctor_run(ws: Workspace, args) -> int:
    tiers, mapped, unknown = doctor.run_doctor(ws)
    yn = {True: "yes", False: "no"}
    print("kb doctor: dotnet=%s tree-sitter=%s; %d extension%s mapped, %d unknown"
          % (yn[tiers["dotnet"]], yn[tiers["tree_sitter"]], len(mapped), "" if len(mapped) == 1 else "s",
             len(unknown)))
    print("outline tier: %s" % ("A available for some families" if any(tiers.values()) and outline.BACKENDS["A"]
                                else "B (standard library)"))
    for ext, fam in sorted(mapped.items()):
        print("mapped: %s -> %s" % (ext, fam))
    for ext, rel in sorted(unknown.items()):
        print("unknown: %s (e.g. %s) -> kb config family %s <family>" % (ext, rel, ext))
    return 0


COMMANDS["doctor"] = (_doctor_add, _doctor_run)


# --- recipe -------------------------------------------------------------------

def _symbol_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("file", help="donor source file")
    p.add_argument("--symbol", required=True, help="symbol name (definition)")
    p.add_argument("--params", help="parameter types or names, comma-separated, to pick an overload")


def _donor_rel(ws: Workspace, p: str) -> str:
    path = user_path(ws, p)
    try:
        return ws.rel(path)
    except ValueError:
        raise KbError("%s is outside the workspace" % p)


def _recipe_add(p: argparse.ArgumentParser) -> None:
    sub = p.add_subparsers(dest="recipe_command", parser_class=_Parser)
    ex = sub.add_parser("extract", help="print a symbol's signature, hash and body")
    _root_args(ex)
    _symbol_args(ex)
    pr = sub.add_parser("promote", help="write a recipe page and its ready-solutions index row")
    _root_args(pr)
    _symbol_args(pr)
    pr.add_argument("--domain", required=True)
    pr.add_argument("--title", required=True)
    pr.add_argument("--owner", required=True, help="owner module")
    dr = sub.add_parser("drift", help="same as check --only 12")
    _root_args(dr)
    ca = sub.add_parser("candidates", help="list cooldown candidates ready for promotion")
    _root_args(ca)
    cd = sub.add_parser("candidate", help="register or tick promotion candidates")
    _root_args(cd)
    csub = cd.add_subparsers(dest="candidate_command", parser_class=_Parser)
    add = csub.add_parser("add")
    _root_args(add)
    _symbol_args(add)
    add.add_argument("--module", required=True)
    tick = csub.add_parser("tick")
    _root_args(tick)
    tick.add_argument("--module", required=True)


def _recipe_run(ws: Workspace, args) -> int:
    cmd = getattr(args, "recipe_command", None)
    if cmd == "extract":
        rel = _donor_rel(ws, args.file)
        family, sym = recipe.donor_symbol(ws, rel, args.symbol, args.params)
        print("kb recipe extract: %s %s" % (rel, args.symbol))
        print("signature: %s" % sym.signature)
        print("hash: %s" % symbols.symbol_hash(sym.body, family))
        print(sym.snippet or sym.body)
        return 0
    if cmd == "promote":
        rel = _donor_rel(ws, args.file)
        journal = Journal(ws)
        run_id = journal.start_run("recipe promote")
        try:
            page = recipe.promote(ws, rel, args.symbol, args.params, args.domain, args.title, args.owner, journal)
        except FileExistsError as exc:
            print("kb recipe promote: %s already exists; nothing written" % exc)
            return 1
        print("kb recipe promote: wrote %s, run_id: %s" % (page, run_id))
        return 0
    if cmd == "drift":
        issues = checks.run_checks(ws, checks.Scope(None), {12})
        print(summary_line("recipe drift", issues))
        for i in issues:
            print("[%s] %s: %s" % (i.severity, i.file, i.symptom))
        return 1 if issues else 0
    if cmd == "candidates":
        ready = recipe.ready_candidates(ws)
        print("kb recipe candidates: %d ready (threshold %s unchanged session closes)"
              % (len(ready), ws.config.get("cooldown_sessions", 3)))
        for c in ready:
            print("%s %s%s [%s] unchanged for %d closes"
                  % (c["file"], c["symbol"], " (%s)" % c["params"] if c.get("params") else "", c["module"],
                     c["closes_unchanged"]))
        return 0
    if cmd == "candidate":
        sub = getattr(args, "candidate_command", None)
        if sub == "add":
            rel = _donor_rel(ws, args.file)
            recipe.candidate_add(ws, rel, args.symbol, args.params, args.module)
            print("kb recipe candidate: registered %s %s for %s" % (rel, args.symbol, args.module))
            return 0
        if sub == "tick":
            ticked = recipe.candidate_tick(ws, args.module)
            print("kb recipe candidate: %d candidate%s of %s updated"
                  % (len(ticked), "" if len(ticked) == 1 else "s", args.module))
            return 0
        raise KbError("recipe candidate needs add or tick")
    raise KbError("recipe needs a subcommand: extract, promote, drift, candidates, candidate")


COMMANDS["recipe"] = (_recipe_add, _recipe_run)


# --- table --------------------------------------------------------------------

def _table_add(p: argparse.ArgumentParser) -> None:
    p.add_argument("rest", nargs=argparse.REMAINDER,
                   help="<export> --module M [--shared]  |  learn <export> --name N --header-row R --map role=col,...")


def _table_parsers():
    tp = _Parser(prog="kb table")
    _root_args(tp)
    tp.add_argument("export")
    tp.add_argument("--module", required=True)
    tp.add_argument("--shared", action="store_true", help="write pages under knowledge-base/shared/tables/")
    tp.add_argument("--encoding", help="code page of a text export that is not UTF-8/UTF-16")
    lp = _Parser(prog="kb table learn")
    _root_args(lp)
    lp.add_argument("export")
    lp.add_argument("--name", required=True, help="profile name")
    lp.add_argument("--header-row", type=int, required=True, help="1-based header row number")
    lp.add_argument("--map", required=True, help="role=column pairs, 1-based, e.g. field=2,type=4")
    lp.add_argument("--encoding", help="code page of a text export that is not UTF-8/UTF-16")
    return tp, lp


def _parse_map(value: str) -> Dict[str, int]:
    out = {}
    for part in value.split(","):
        if not part.strip():
            continue
        if "=" not in part:
            raise KbError("--map takes role=column pairs, e.g. field=2,type=4")
        k, v = part.split("=", 1)
        try:
            out[k.strip()] = int(v)
        except ValueError:
            raise KbError("column for `%s` must be a number" % k.strip())
    return out


def _table_learn(ws: Workspace, a) -> int:
    export = user_path(ws, a.export)
    if not export.is_file():
        raise KbError("%s not found" % a.export)
    prof, fields, err = tables.learn(ws, export, a.name, a.header_row, _parse_map(a.map), a.encoding)
    if prof is None:
        print("kb table learn: nothing saved: %s" % err)
        return 1
    folder = ws.data_dir / "profiles"
    ws.make_data_dir()
    folder.mkdir(parents=True, exist_ok=True)
    (folder / (a.name + ".json")).write_bytes((json.dumps(prof, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    print("kb table learn: profile `%s` saved, %d field%s parsed (first 10 below; show them to the user)"
          % (a.name, len(fields), "" if len(fields) == 1 else "s"))
    for rec in fields[:10]:
        extra = ", ".join("%s=%s" % (k, rec[k]) for k in tables.ROLES if k != "field" and rec[k])
        print("%s%s" % (rec["field"], (" | " + extra) if extra else ""))
    return 0


def _table_pages(ws: Workspace, a) -> int:
    export = user_path(ws, a.export)
    if not export.is_file():
        raise KbError("%s not found" % a.export)
    module = artifacts._module_name(ws, a.module)
    rel = tables.export_rel(ws, export)
    profiles = tables.load_profiles(ws)
    try:
        rows = tables.read_rows(export, a.encoding)
    except KbError:
        if a.encoding:
            raise
        rows = None
        for prof in profiles.values():
            if prof.get("encoding"):
                try:
                    rows = tables.read_rows(export, prof["encoding"])
                    break
                except KbError:
                    continue
        if rows is None:
            raise KbError("%s is not UTF-8/UTF-16 and no profile knows its code page; "
                          "run again with --encoding <code page> (e.g. cp1251)" % rel)
    found = tables.detect_profile(rows, profiles)
    if found is None:
        print("kb table: no profile matches %s; register the layout with `kb table learn`" % rel)
        print("header candidates (columns numbered from 1):")
        for r, row in tables.header_candidates(rows):
            print(tables.format_row(r, row))
        return 3
    pname, header_row = found
    prof = profiles[pname]
    if prof.get("encoding") and not a.encoding and export.suffix.lower() in (".csv", ".tsv", ".txt"):
        rows = tables.read_rows(export, prof["encoding"])
    fields = tables.parse_fields(rows, prof, header_row)
    main_name = tables.table_name(export, rows, prof)
    groups = tables.group_tables(main_name, fields)
    source, registered = tables.source_for(ws, rel)
    index = resolve.ensure_index(ws)
    folder = tables.page_folder(ws, module, a.shared)
    journal = Journal(ws)
    run_id = journal.start_run("table")
    lines, failed, written = [], 0, 0
    pages_written: List[str] = []
    for name, recs in groups.items():
        # same table = a `kind: table` page with the same file stem (letter case aside); never by alias
        existing = sorted(p for p, e in index["pages"].items()
                          if (e.get("kind") or "").casefold() == "table"
                          and p.rsplit("/", 1)[-1][:-3].casefold() == name.casefold() and (ws.root / p).is_file())
        if len(existing) > 1:
            failed += 1
            lines.append("skipped %s: pages share this name: %s (merge them first)" % (name, ", ".join(existing)))
            continue
        new_lines = [tables.field_line(r, prof) for r in recs]
        if existing:
            page = existing[0]
            text, diff = tables.replace_fields(journal.read_text(page), new_lines)
            journal.write_text(page, text, "table_fields")
            written += 1
            lines.append("updated %s (fields only)" % page)
            pages_written.append(page)
            lines += ["  " + d for d in diff] or ["  no field changes"]
        else:
            page = "%s/%s.md" % (folder, name)
            journal.write_text(page, tables.render_page(name, source, recs, prof), "table_page")
            written += 1
            lines.append("created %s" % page)
            pages_written.append(page)
    if registered and pages_written and artifacts.mark_processed(ws, source, pages_written, journal):
        lines.append("registry: %s marked processed" % source)
    print("kb table: %d page%s from %s (profile %s), run_id: %s"
          % (written, "" if written == 1 else "s", rel, pname, run_id))
    if not registered:
        print("note: %s has no registry row; `kb ingest` it so `source:` points at a stable copy" % rel)
    for ln in lines:
        print(ln)
    return 1 if failed else 0


def _table_run(ws: Workspace, args) -> int:
    rest = list(args.rest or [])
    tp, lp = _table_parsers()
    try:
        if rest and rest[0] == "learn":
            return _table_learn(ws, lp.parse_args(rest[1:]))
        return _table_pages(ws, tp.parse_args(rest))
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2


COMMANDS["table"] = (_table_add, _table_run)


# --- hook ---------------------------------------------------------------------

def _hook_add(p: argparse.ArgumentParser) -> None:
    p.add_argument("event", choices=sorted(hooks.EVENTS), help="hook event; payload JSON on stdin")


def _hook_run(ws: Workspace, args) -> int:
    out = hooks.render(args.event, hooks.EVENTS[args.event](ws, hooks.read_payload(sys.stdin)))
    if out:
        print(out)
    return 0


def run_hook(args) -> int:
    """Hooks never fail the agent session: silent outside a workspace, one error line otherwise."""
    try:
        root = getattr(args, "root", None)
        try:
            ws = Workspace.load(Path(root) if root else None)
        except NoWorkspace:
            return 0
        return _hook_run(ws, args)
    except Exception as exc:  # noqa: BLE001 - a hook must not break the session
        msg = "KB hook error: %s" % (str(exc).splitlines()[0] if str(exc) else type(exc).__name__)
        if args.event == "stop":
            print(msg, file=sys.stderr)  # plain text on stdout is invalid for Stop hooks
        else:
            print(hooks.render(args.event, [msg]))
        return 0


COMMANDS["hook"] = (_hook_add, _hook_run)


# --- upgrade ------------------------------------------------------------------

def _upgrade_add(p: argparse.ArgumentParser) -> None:
    p.add_argument("--from", dest="src", help="template root to upgrade from (default: the one holding this kb.py)")
    p.add_argument("--dry-run", action="store_true", help="print the plan; write nothing")
    p.add_argument("--rollback", action="store_true", help="restore the state before the last upgrade")
    p.add_argument("--set-evidence", action="append", default=[], metavar="MODULE=path;path",
                   help="answer an evidence question (repeatable; MODULE= for none)")
    p.add_argument("--set-shared-evidence", metavar="path;path", help="workspace-level shared evidence roots")
    p.add_argument("--yes", action="store_true", help="the user approved the printed plan: apply it")


def _upgrade_answers(ws: Workspace, args) -> dict:
    evidence: Dict[str, List[str]] = {}
    names = {m.name.casefold(): m.name for m in ws.modules}
    for item in args.set_evidence:
        if "=" not in item:
            raise KbError("--set-evidence takes MODULE=path;path")
        mod, paths = item.split("=", 1)
        if mod.strip().casefold() not in names:
            raise KbError("unknown module `%s` in --set-evidence" % mod.strip())
        evidence[names[mod.strip().casefold()]] = [p.strip().replace("\\", "/") for p in paths.split(";") if p.strip()]
    shared = None
    if args.set_shared_evidence:
        shared = [p.strip().replace("\\", "/") for p in args.set_shared_evidence.split(";") if p.strip()]
    return {"evidence": evidence, "shared_evidence": shared}


def _upgrade_run(ws: Workspace, args) -> int:
    if args.rollback:
        return upgrade.rollback(ws, print)
    answers = _upgrade_answers(ws, args)
    src = Path(args.src).resolve() if args.src else upgrade.default_source()
    plan = upgrade.plan_upgrade(ws, src, answers)
    if plan.empty:
        print("kb upgrade: workspace is up to date (version %d)" % plan.version)
        return 0
    if args.dry_run or not args.yes:
        for line in upgrade.format_plan(plan, applying=False):
            print(line)
        return 4 if plan.questions else 0
    if plan.questions:
        for line in upgrade.format_plan(plan, applying=False):
            print(line)
        print("nothing written: %d question%s open" % (len(plan.questions), "" if len(plan.questions) == 1 else "s"))
        return 4
    for line in upgrade.format_plan(plan, applying=True):
        print(line)
    return upgrade.apply_upgrade(ws, plan, answers, print)


COMMANDS["upgrade"] = (_upgrade_add, _upgrade_run)


# --- dispatch ---------------------------------------------------------------

class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stdout)
        print("kb: error: %s" % message)
        raise SystemExit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="kb", description="Knowledge-base integrity tool.")
    _root_args(parser)
    sub = parser.add_subparsers(dest="command", parser_class=_Parser)
    for name, (add_args, _handler) in COMMANDS.items():
        sp = sub.add_parser(name)
        _root_args(sp)
        add_args(sp)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    if not getattr(args, "command", None):
        parser.print_usage(sys.stdout)
        print("kb: error: a command is required")
        return 2
    _add, handler = COMMANDS[args.command]
    if args.command == "hook":
        return run_hook(args)
    try:
        root = getattr(args, "root", None)
        ws = Workspace.load(Path(root) if root else None)
        return int(handler(ws, args) or 0)
    except KbError as exc:
        print("kb %s: error: %s" % (args.command, exc))
        return 2


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    sys.exit(main(sys.argv[1:]))
