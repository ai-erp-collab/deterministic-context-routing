"""Upgrade a workspace built with an earlier template: plan, snapshot, shipped files,
managed blocks, hooks merge, numbered migrations, manifest, version; resumable; rollback."""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import os
import posixpath
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from . import checks
from .checks import iter_files, register_check
from .issues import Issue, Scope
from .journal import Journal
from .links import _kb_pages

KB_PREFIX = "knowledge-base/"
from .markdown import extract_links
from .migrations import Question, all_migrations
from .migrations.m001_initial import LEGACY_READMES, UNIMPORTED, legacy_baseline
from .workspace import CURRENT_VERSION, KbError, Workspace

SHIPPED_PREFIXES = ("tools/kb/", "skills/kb/", ".codex/skills/kb/", "templates/")
HOOKS_JSON = ".codex/hooks.json"
BLOCK_BEGIN = "<!-- kb:begin -->"
BLOCK_END = "<!-- kb:end -->"
BLOCK_ASSET = "tools/kb/assets/agents-block.md"
RULE_FILES = ("AGENTS.md", "CLAUDE.md")
SNAPSHOT_ROOTS = ("knowledge-base", "modules.md", "source-artifacts/INDEX.md", "source-artifacts/registry.json",
                  "AGENTS.md", "CLAUDE.md", "skills", ".codex", ".kb") + LEGACY_READMES
KB_KEEP = ("backups/", "journal/", "upgrade-log.jsonl")
MAX_SNAPSHOT_BYTES = 5 * 1024 * 1024
LOG = "upgrade-log.jsonl"


def default_source() -> Path:
    """The template root that contains the running tools/kb/."""
    return Path(__file__).resolve().parents[3]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shipped_files(src: Path) -> List[str]:
    out = []
    for p in src.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(src).as_posix()
        if "__pycache__" in rel.split("/") or rel.endswith(".pyc"):
            continue
        if rel.startswith(SHIPPED_PREFIXES) or rel == HOOKS_JSON:
            out.append(rel)
    return sorted(out)


def workspace_version(ws) -> int:
    if not (ws.data_dir / "config.json").is_file():
        return 0
    try:
        return int(ws.config.get("workspace_version", 0))
    except (TypeError, ValueError):
        return 0


def apply_block(text: str, block: str) -> str:
    block = block.strip("\r\n").replace("\r\n", "\n")
    b = text.find(BLOCK_BEGIN)
    e = text.find(BLOCK_END, b + 1) if b >= 0 else -1
    if b >= 0 and e >= 0:
        return text[:b] + block + text[e + len(BLOCK_END):]
    base = text.rstrip("\r\n")
    return (base + "\n\n" if base else "") + block + "\n"


def imports_agents(text: str) -> bool:
    """A rule file that imports AGENTS.md already loads the block; a second copy would load it twice."""
    return re.search(r"(?:^|\s)@(?:\./)?AGENTS\.md(?![\w.])", text, re.M) is not None


def merge_hooks(current: dict, shipped: dict) -> dict:
    merged = copy.deepcopy(current)
    events = merged.setdefault("hooks", {})
    have = {(ev, h.get("command")) for ev, groups in events.items() for g in groups for h in g.get("hooks", [])}
    for ev, groups in (shipped.get("hooks") or {}).items():
        for g in groups:
            cmds = [(ev, h.get("command")) for h in g.get("hooks", [])]
            if any(c not in have for c in cmds):
                events.setdefault(ev, []).append(copy.deepcopy(g))
                have.update(cmds)
    return merged


def _read_json(path: Path, what: str) -> dict:
    try:
        data = json.loads(path.read_bytes().decode("utf-8-sig"))
    except ValueError as exc:
        raise KbError("%s is not valid JSON (%s); fix it, then run the upgrade again" % (what, exc))
    if not isinstance(data, dict):
        raise KbError("%s must hold a JSON object" % what)
    return data


@dataclass
class UpgradePlan:
    src: Path
    version: int
    add: List[str] = field(default_factory=list)
    replace: List[str] = field(default_factory=list)
    conflict: List[str] = field(default_factory=list)
    hooks: Optional[str] = None
    managed: List[str] = field(default_factory=list)
    migrations: List[str] = field(default_factory=list)
    questions: List[Question] = field(default_factory=list)
    block: str = ""
    legacy_links: list = field(default_factory=list)  # check-3 issues the upgrade's link step would meet
    rules_links: list = field(default_factory=list)  # check-2 issues in rules files and logs after the upgrade

    @property
    def empty(self) -> bool:
        return not (self.add or self.replace or self.conflict or self.hooks or self.managed or self.migrations
                    or self.version < CURRENT_VERSION)


def _answered(q: Question, answers: dict) -> bool:
    if q.id.startswith("evidence:"):
        name = q.id.split(":", 1)[1].casefold()
        return name in {k.casefold() for k in (answers.get("evidence") or {})}
    return False


def plan_upgrade(ws, src: Path, answers: Optional[dict] = None) -> UpgradePlan:
    answers = answers or {}
    src = Path(src).resolve()
    if not (src / "tools" / "kb" / "kb.py").is_file():
        raise KbError("%s is not a template root (no tools/kb/kb.py)" % src)
    plan = UpgradePlan(src, workspace_version(ws))
    manifest = {}
    if (ws.data_dir / "manifest.json").is_file():
        manifest = _read_json(ws.data_dir / "manifest.json", ".kb/manifest.json")
    same_tree = src == ws.root
    baseline = legacy_baseline() if plan.version == 0 else {}  # no manifest yet: 0.1.x bytes = unedited
    for rel in shipped_files(src):
        if rel == HOOKS_JSON or same_tree:
            continue
        s = _sha(src / rel)
        dest = ws.root / rel
        if not dest.is_file():
            plan.add.append(rel)
            continue
        d = _sha(dest)
        if d == s:
            continue
        if manifest.get(rel) == d or d in baseline.get(rel, ()):
            plan.replace.append(rel)
            continue
        pending = ws.root / (rel + ".new")
        if pending.is_file() and _sha(pending) == s:
            continue  # already offered; waiting for the project to merge it
        plan.conflict.append(rel)
    hooks_src = src / HOOKS_JSON
    if hooks_src.is_file() and not same_tree:
        dest = ws.root / HOOKS_JSON
        if not dest.is_file():
            plan.hooks = "add"
        else:
            try:
                current = _read_json(dest, HOOKS_JSON)
            except KbError:
                plan.hooks = "merge (current file is not valid JSON)"
            else:
                if merge_hooks(current, _read_json(hooks_src, "shipped " + HOOKS_JSON)) != current:
                    plan.hooks = "merge"
    asset = src / BLOCK_ASSET
    if not asset.is_file():
        asset = Path(__file__).resolve().parents[1] / "assets" / "agents-block.md"
    plan.block = asset.read_bytes().decode("utf-8-sig")
    for name in RULE_FILES:
        p = ws.root / name
        if p.is_file():
            text = p.read_bytes().decode("utf-8-sig").replace("\r\n", "\n")
            if name != "AGENTS.md" and imports_agents(text):
                continue
            if apply_block(text, plan.block) != text:
                plan.managed.append(name)
    for m in all_migrations():
        if m.needs(ws):
            plan.migrations.append(m.ID)
            plan.questions += [q for q in m.questions(ws) if not _answered(q, answers)]
    if plan.migrations:
        plan.legacy_links = checks.run_checks(ws, Scope(None), {3})
    arriving = set(plan.add)
    for i in checks.run_checks(ws, Scope(None), {2}):
        if i.file.startswith(KB_PREFIX):
            continue
        target = i.subject[len("link "):].rsplit(" line ", 1)[0]
        joined = posixpath.normpath(posixpath.join(posixpath.dirname(i.file), target.split("#")[0])).rstrip("/")
        if joined not in arriving:
            plan.rules_links.append(i)
    return plan


def format_plan(plan: UpgradePlan, applying: bool) -> List[str]:
    if plan.version == CURRENT_VERSION:
        what = "shipped files changed, workspace format %d unchanged" % plan.version
    else:
        what = "workspace format %d -> %d" % (plan.version, CURRENT_VERSION)
    head = "kb upgrade: %s, from %s (%s)" % (
        what, plan.src.as_posix(), "applying" if applying else "plan only; nothing written")
    lines = [head]
    for label, items in (("add", plan.add), ("replace", plan.replace),
                         ("conflict (project edits kept; <file>.new written beside them)", plan.conflict)):
        if items:
            lines.append("%s: %d file%s" % (label, len(items), "" if len(items) == 1 else "s"))
            lines += ["  - %s" % r for r in items]
    if plan.managed:
        lines.append("managed block (%s ... %s): %s" % (BLOCK_BEGIN, BLOCK_END, ", ".join(plan.managed)))
    if plan.hooks:
        lines.append("hooks: %s %s" % (HOOKS_JSON, plan.hooks))
    if plan.migrations:
        lines.append("migrations: %s" % ", ".join(plan.migrations))
    if plan.rules_links:
        lines.append("rules-file links that will not open: %d (new blocking issues once links in AGENTS.md "
                     "and session logs are checked; fix them or exclude them with link_ignore)" % len(plan.rules_links))
        for i in plan.rules_links[:10]:
            lines.append("  - %s" % i.symptom)
        if len(plan.rules_links) > 10:
            lines.append("  - ... %d more" % (len(plan.rules_links) - 10))
    if plan.legacy_links:
        conv = [i for i in plan.legacy_links if i.fix and i.fix.get("safe")]
        left = len(plan.legacy_links) - len(conv)
        lines.append("legacy links: %d convert, %d left as issues (every edit journaled; undo with kb upgrade --rollback)"
                     % (len(conv), left))
        for i in plan.legacy_links[:10]:
            lines.append("  - %s line %s: %s" % (i.file, i.subject.rsplit(" ", 1)[-1],
                                                  "%s -> %s" % (i.fix["old"], i.fix["new"]) if i in conv
                                                  else "%s (left: %s)" % (i.fix["old"], i.proposed_fix)))
        if len(plan.legacy_links) > 10:
            lines.append("  - ... %d more" % (len(plan.legacy_links) - 10))
    if plan.questions:
        lines.append("questions (%d open):" % len(plan.questions))
        for q in plan.questions:
            lines.append("  - %s: %s" % (q.id, q.text))
            if q.candidates:
                lines.append("    candidates: %s" % ", ".join(q.candidates))
            if q.how:
                lines.append("    answer with: %s" % q.how)
    if not applying:
        lines.append("next: %s" % ("answer the questions, then run again with --yes" if plan.questions
                                    else "run again with --yes to apply this plan"))
    return lines


# --- log -----------------------------------------------------------------------------

def read_log(ws) -> List[dict]:
    p = ws.data_dir / LOG
    out = []
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def _log(ws, upgrade_id: str, step: str, run: Optional[str] = None, **extra) -> None:
    ws.make_data_dir()
    rec = {"upgrade": upgrade_id, "step": step, "run": run,
           "time": datetime.datetime.now().isoformat(timespec="seconds")}
    rec.update(extra)
    with open(ws.data_dir / LOG, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _resume_state(ws) -> Tuple[Optional[str], Dict[str, dict]]:
    log = read_log(ws)
    if not log:
        return None, {}
    last = log[-1]["upgrade"]
    steps = {r["step"]: r for r in log if r["upgrade"] == last}
    if "done" in steps or "rollback" in steps:
        return None, {}
    return last, steps


# --- counts ----------------------------------------------------------------------------

def counts(ws) -> dict:
    issues = checks.run_checks(ws, Scope(None))
    total = 0
    for rel in _kb_pages(ws, Scope(None)):
        text = (ws.root / rel).read_bytes().decode("utf-8", errors="replace")
        total += sum(1 for ln in extract_links(text) if ln.kind != "wiki")
    by = lambda n: sum(1 for i in issues if i.check == n)  # noqa: E731
    return {"links_total": total, "links_valid": total - by(2), "duplicates": by(8), "untracked": by(9),
            "open": len(issues)}


def format_counts(label: str, c: dict) -> str:
    return "%s: links %d/%d valid, %d duplicate group%s, %d untracked evidence file%s, %d open issue%s" % (
        label, c["links_valid"], c["links_total"], c["duplicates"], "" if c["duplicates"] == 1 else "s",
        c["untracked"], "" if c["untracked"] == 1 else "s", c["open"], "" if c["open"] == 1 else "s")


# --- snapshot -------------------------------------------------------------------------

def _snapshot(ws) -> str:
    backups = ws.data_dir / "backups"
    ws.make_data_dir()
    backups.mkdir(parents=True, exist_ok=True)
    base = "%s-pre-upgrade" % datetime.date.today().isoformat()
    path = backups / (base + ".zip")
    n = 2
    while path.exists():
        path = backups / ("%s-%d.zip" % (base, n))
        n += 1
    skipped = []
    with zipfile.ZipFile(str(path), "w", zipfile.ZIP_DEFLATED) as z:
        for root in SNAPSHOT_ROOTS:
            p = ws.root / root
            files = [p] if p.is_file() else (sorted(x for x in p.rglob("*") if x.is_file()) if p.is_dir() else [])
            for f in files:
                rel = f.relative_to(ws.root).as_posix()
                if rel.startswith(".kb/backups/") or rel == ".kb/" + LOG:
                    continue
                if f.stat().st_size > MAX_SNAPSHOT_BYTES:
                    skipped.append(rel)
                    continue
                z.write(str(f), rel)
        z.writestr("backup-skipped.txt", "\n".join(skipped) + ("\n" if skipped else ""))
    return ws.rel(path)


GENERATED_KB = {".kb/entities.json", ".kb/issues.json", ".kb/manifest.json"}


def is_project_kb_data(rel: str) -> bool:
    """.kb/ files that hold project decisions (config, ignore rules, profiles, candidates),
    as opposed to regenerated data and the upgrade's own records."""
    return rel.startswith(".kb/") and rel not in GENERATED_KB and not rel[4:].startswith(KB_KEEP)


def _kb_digest(rel: str, data: bytes) -> str:
    if rel == ".kb/state.json":  # the hooks' per-session file list is not project data
        try:
            d = json.loads(data.decode("utf-8"))
            if isinstance(d, dict):
                d.pop("session_changed", None)
                data = json.dumps(d, sort_keys=True).encode("utf-8")
        except ValueError:
            pass
    return hashlib.sha256(data).hexdigest()


def kb_hashes(ws) -> Dict[str, str]:
    out = {}
    if ws.data_dir.is_dir():
        for p in ws.data_dir.rglob("*"):
            rel = p.relative_to(ws.root).as_posix()
            if p.is_file() and is_project_kb_data(rel):
                out[rel] = _kb_digest(rel, p.read_bytes())
    return out


def _snapshot_kb_hashes(ws, snapshot_rel: str) -> Dict[str, str]:
    with zipfile.ZipFile(str(ws.root / snapshot_rel)) as z:
        return {n: _kb_digest(n, z.read(n)) for n in z.namelist() if is_project_kb_data(n)}


def _restore_kb(ws, snapshot_rel: str) -> int:
    restored = 0
    with zipfile.ZipFile(str(ws.root / snapshot_rel)) as z:
        saved = {n: z.read(n) for n in z.namelist()
                 if n.startswith(".kb/") and not n[4:].startswith(KB_KEEP)}
    for p in sorted(ws.data_dir.rglob("*"), reverse=True):
        rel = p.relative_to(ws.root).as_posix()
        if rel[4:].startswith(KB_KEEP):
            continue
        if p.is_file() and rel not in saved:
            p.unlink()
        elif p.is_dir() and not any(p.iterdir()):
            p.rmdir()
    for rel, data in saved.items():
        dest = ws.root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.is_file() or dest.read_bytes() != data:
            dest.write_bytes(data)
            restored += 1
    return restored


# --- apply ------------------------------------------------------------------------------

def apply_upgrade(ws, plan: UpgradePlan, answers: dict, emit: Callable[[str], None]) -> int:
    upgrade_id, done = _resume_state(ws)
    if upgrade_id is None:
        upgrade_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + os.urandom(2).hex()
    else:
        emit("resuming upgrade %s; finished steps skipped: %s" % (upgrade_id, ", ".join(done)))
    src = plan.src

    def step(name: str, func: Callable, **extra) -> None:
        """Run a step under its own journal run. The run id is logged before the step starts,
        so a step that fails halfway can still be rolled back."""
        if name in done:
            return
        j = Journal(ws)
        run = j.start_run("upgrade " + name)
        _log(ws, upgrade_id, name + ":start", run)
        func(j)
        _log(ws, upgrade_id, name, run, kb=kb_hashes(ws), **extra)

    if "before" not in done:
        before = counts(ws)
        _log(ws, upgrade_id, "before", None, counts=before)
    else:
        before = done["before"].get("counts", {})

    def do_snapshot():
        path = _snapshot(ws)
        _log(ws, upgrade_id, "snapshot", None, snapshot=path)
        emit("snapshot: %s (knowledge base, rules files, .kb data; other file edits are in the undo journal)" % path)
        done["snapshot"] = {"snapshot": path}

    if "snapshot" not in done:
        do_snapshot()

    def do_files(j) -> str:
        rid = j.run_id
        for rel in plan.add:
            j.copy_file(src / rel, rel, "upgrade_add")
        for rel in plan.replace:
            j.copy_file(src / rel, rel, "upgrade_replace", overwrite=True)
        for rel in plan.conflict:
            j.copy_file(src / rel, rel + ".new", "upgrade_conflict", overwrite=True)
        emit("files: %d added, %d replaced, %d conflict%s written as .new"
             % (len(plan.add), len(plan.replace), len(plan.conflict), "" if len(plan.conflict) == 1 else "s"))
        return rid

    def do_blocks(j) -> str:
        rid = j.run_id
        for name in plan.managed:
            j.write_text(name, apply_block(j.read_text(name), plan.block), "upgrade_block")
        if plan.managed:
            emit("managed block written: %s" % ", ".join(plan.managed))
        return rid

    def do_hooks(j) -> str:
        rid = j.run_id
        if plan.hooks == "add":
            j.copy_file(src / HOOKS_JSON, HOOKS_JSON, "upgrade_hooks")
        elif plan.hooks:
            current = _read_json(ws.root / HOOKS_JSON, HOOKS_JSON)
            merged = merge_hooks(current, _read_json(src / HOOKS_JSON, "shipped " + HOOKS_JSON))
            j.write_text(HOOKS_JSON, json.dumps(merged, indent=2, ensure_ascii=False) + "\n", "upgrade_hooks")
        if plan.hooks:
            emit("hooks: %s %s" % (HOOKS_JSON, plan.hooks))
        return rid

    try:
        step("files", do_files)
        step("managed-blocks", do_blocks)
        step("hooks-json", do_hooks)
        for m in all_migrations():
            if m.ID not in plan.migrations:
                continue

            def do_migration(j, m=m) -> str:
                rid = j.run_id
                for line in m.apply(ws, answers, j):
                    emit("migration %s: %s" % (m.ID, line))
                applied = ws.config.setdefault("migrations_applied", [])
                if m.ID not in applied:
                    applied.append(m.ID)
                ws.save_config()
                return rid

            step("migration:" + m.ID, do_migration)

        def do_manifest(j):
            manifest = {rel: _sha(src / rel) for rel in shipped_files(src) if rel != HOOKS_JSON}
            if (ws.data_dir / "manifest.json").is_file():
                old = _read_json(ws.data_dir / "manifest.json", ".kb/manifest.json")
                old.update(manifest)
                manifest = old
            ws.make_data_dir()
            (ws.data_dir / "manifest.json").write_bytes(
                (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode("utf-8"))

        step("manifest", do_manifest)

        def do_version(j):
            ws.config["workspace_version"] = CURRENT_VERSION
            ws.save_config()

        step("version", do_version)
        fresh = Workspace.load(ws.root)
        after = counts(fresh)
        emit(format_counts("before", before))
        emit(format_counts("after", after))
        _log(ws, upgrade_id, "done", None, counts=after, kb=kb_hashes(ws))
    except (KbError, OSError) as exc:
        emit("kb upgrade: stopped: %s" % exc)
        emit("finished steps are recorded in .kb/%s; run the same command again to continue" % LOG)
        return 1
    return 0


# --- rollback ---------------------------------------------------------------------------

def rollback(ws, emit: Callable[[str], None]) -> int:
    log = read_log(ws)
    ids = [r["upgrade"] for r in log if r["step"] == "snapshot"]
    if not ids:
        emit("kb upgrade: nothing to roll back (no upgrade snapshot recorded)")
        return 1
    uid = ids[-1]
    recs = [r for r in log if r["upgrade"] == uid]
    if any(r["step"] == "rollback" for r in recs):
        emit("kb upgrade: upgrade %s was already rolled back" % uid)
        return 1
    snapshot = next(r["snapshot"] for r in recs if r["step"] == "snapshot")
    runs: List[str] = []
    for r in recs:
        if r.get("run") and r["run"] not in runs:
            runs.append(r["run"])
    j = Journal(ws)
    runs = [r for r in runs if j.entries(r)]
    changed = j.changed_since(runs)
    baseline = next((r["kb"] for r in reversed(recs) if "kb" in r), None)
    if baseline is None:
        baseline = _snapshot_kb_hashes(ws, snapshot)
    current = kb_hashes(ws)
    changed += sorted(rel for rel in set(current) | set(baseline)
                      if current.get(rel) != baseline.get(rel))
    if changed:
        emit("kb upgrade: rollback refused; these files changed after the upgrade:")
        for f in changed:
            emit("  - %s" % f)
        emit("restore or move those edits first; nothing was changed")
        return 1
    files = 0
    for rid in reversed(runs):
        files += len(Journal(ws).undo(rid))
    kb_files = _restore_kb(ws, snapshot)
    _log(ws, uid, "rollback", None)
    emit("kb upgrade: rolled back upgrade %s (%d workspace file%s reverted, %d .kb file%s restored from %s)"
         % (uid, files, "" if files == 1 else "s", kb_files, "" if kb_files == 1 else "s", snapshot))
    return 0


# --- check 16: pending merges -------------------------------------------------------------

def check_pending(ws, scope: Scope) -> List[Issue]:
    out = []
    for root in ("tools/kb", "skills/kb", "templates", ".codex"):
        for rel in iter_files(ws, root, ".new"):
            if not scope.includes(rel):
                continue
            target = rel[:-4]
            out.append(Issue(16, rel, "pending merge", "minor", "",
                             "`%s` holds the new shipped version of `%s`, which the project edited" % (rel, target),
                             "merge the wanted changes into `%s`, then delete `%s`" % (target, rel)))
    for rel in LEGACY_READMES:
        if (ws.root / rel).is_file() and scope.includes(rel):
            out.append(Issue(16, rel, "legacy readme", "minor", "",
                             "`%s` is a 0.1.x README the project edited; it still describes moving files "
                             "from raw to processed, but files never move now" % rel,
                             "move its project-specific rules into AGENTS.md `## Project-Specific Rules` "
                             "(drop any wording about moving files; status is a registry field), then delete it"))
    if (ws.root / UNIMPORTED).is_file() and scope.includes(UNIMPORTED):
        out.append(Issue(16, UNIMPORTED, "unimported rows", "minor", "",
                         "old ledger rows could not be imported into the registry (see `%s`)" % UNIMPORTED,
                         "register them with `kb ingest` or in `registry.json`, then delete the file"))
    return out


register_check(16, check_pending)
