"""hip — Hermes Instruction Pack CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

from . import __version__
from .importer import SourceImporter
from .manifest import Manifest


def find_root(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for cand in [p, *p.parents]:
        if (cand / "sources" / "manifest.yaml").exists() or (cand / "pyproject.toml").exists():
            try:
                text = (cand / "pyproject.toml").read_text(encoding="utf-8")
            except OSError:
                text = ""
            if "hermes-instruction-pack" in text or (cand / "sources").is_dir():
                return cand
    return p


def cmd_inspect(args: argparse.Namespace) -> int:
    root = find_root()
    print(f"hip version: {__version__}")
    print(f"project root: {root}")
    mpath = root / "sources" / "manifest.yaml"
    if mpath.exists():
        m = Manifest.load(mpath)
        print(f"manifest: {mpath} sources={m.counts()}")
    else:
        print("manifest: MISSING (run `hip sources import`)")
    for label, path in [
        ("core", root / "core"),
        ("personas", root / "personas"),
        ("protocols", root / "protocols"),
        ("adapters", root / "adapters" / "hermes"),
        ("tests", root / "tests"),
    ]:
        n = len(list(path.glob("**/*"))) if path.exists() else 0
        print(f"{label}: {path} ({n} entries)")
    return 0


def cmd_sources_list(args: argparse.Namespace) -> int:
    root = find_root()
    m = Manifest.load(root / "sources" / "manifest.yaml")
    rows = m.all()
    if args.status:
        rows = [r for r in rows if r.get("status") == args.status]
    if args.json:
        print(json.dumps(rows, indent=1))
        return 0
    if not rows:
        print("no sources recorded")
        return 0
    for r in rows:
        print(
            f"{r.get('id'):32} {r.get('status'):8} {r.get('kind'):12} "
            f"{(r.get('size') or 0):>8}B  {r.get('url', '')[:70]}"
        )
    print(f"total: {len(rows)}  counts: {m.counts()}")
    return 0


def cmd_sources_import(args: argparse.Namespace) -> int:
    root = find_root()
    imp = SourceImporter(root)
    failures = 0
    if args.gist_user:
        try:
            imp.import_gist_user(args.gist_user)
        except Exception as e:
            print(f"ERROR gist_user {args.gist_user}: {e}", file=sys.stderr)
            failures += 1
    for url in args.pinned or []:
        rec = imp.import_gist_pinned(url)
        if rec.get("status") == "failed":
            failures += 1
    for url in args.repo or []:
        rec = imp.import_repo(url)
        if rec.get("status") == "failed":
            failures += 1
    if not (args.gist_user or args.pinned or args.repo):
        print("nothing to import; pass --gist-user/--pinned/--repo", file=sys.stderr)
        return 2
    counts = imp.finalize()
    print(f"import finished: {counts}")
    return 1 if failures else 0


def cmd_sources_audit(args: argparse.Namespace) -> int:
    from .audit import run_audit

    root = find_root()
    return run_audit(root)


def cmd_classify(args: argparse.Namespace) -> int:
    from .classifier import run_classify

    return run_classify(find_root())


def cmd_normalize(args: argparse.Namespace) -> int:
    from .normalizer import run_normalize

    return run_normalize(find_root())


def cmd_modules_list(args: argparse.Namespace) -> int:
    from .modules import module_index

    idx = module_index(find_root())
    if args.json:
        print(json.dumps(idx, indent=1))
        return 0
    for m in idx["modules"]:
        status = "OK " if m.get("valid") else "BAD"
        print(
            f"{status} {m.get('module_id','?'):28} {m.get('kind','?'):9} "
            f"prio={m.get('priority','-'):<4} act={m.get('activation','?'):9} {m.get('path','')}"
        )
    print(f"total: {idx['count']}  duplicate_ids: {idx['duplicate_ids'] or 'none'}")
    return 0


def cmd_modules_validate(args: argparse.Namespace) -> int:
    from .validator import run_validate

    return run_validate(find_root())


def cmd_resolve(args: argparse.Namespace) -> int:
    from .resolver import ResolveError, resolve

    try:
        result = resolve(find_root(), args.task_type, persona=args.persona)
    except ResolveError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=1))
        return 0
    print(f"task_type: {result['task_type']}  persona: {result['persona'] or 'none'}")
    for m in result["selected"]:
        print(f"  + {m['module_id']:28} ({m['kind']}, prio {m['priority']}) <- {m['path']}")
    for r in result["reasons"]:
        print(f"    why {r['module']}: {r['reason']}")
    return 0


def cmd_adapter_check(args: argparse.Namespace) -> int:
    from .adapter_hermes import check

    result = check(find_root())
    if args.json:
        print(json.dumps(result, indent=1))
    else:
        for k, v in result.items():
            if k in ("findings", "warnings", "pack_personalities", "existing_hip_personalities"):
                print(f"{k}:")
                for x in v or []:
                    print(f"  - {x}")
            else:
                print(f"{k}: {v}")
    return 0 if result.get("compatible") else 1


def cmd_adapter_install(args: argparse.Namespace) -> int:
    from .adapter_hermes import install

    try:
        result = install(find_root(), dry_run=args.dry_run, with_instructions=args.with_instructions)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=1))
    return 0


def cmd_adapter_rollback(args: argparse.Namespace) -> int:
    from .adapter_hermes import rollback

    try:
        result = rollback(find_root())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=1))
    return 0


def cmd_adapter_uninstall(args: argparse.Namespace) -> int:
    from .adapter_hermes import uninstall_personalities

    try:
        result = uninstall_personalities(find_root())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=1))
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    import subprocess

    root = find_root()
    env = {**os.environ, "PYTHONPATH": str(root / "src")}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q"],
        cwd=str(root),
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )
    print(proc.stdout[-4000:])
    if proc.returncode != 0:
        print(proc.stderr[-2000:], file=sys.stderr)
    return proc.returncode


def cmd_report(args: argparse.Namespace) -> int:
    from .reporting import generate_report

    return generate_report(find_root())


def cmd_techniques(args: argparse.Namespace) -> int:
    from .technique_extractor import run_extract

    return run_extract(find_root())


def cmd_evaluate(args: argparse.Namespace) -> int:
    from .evaluate import run_evaluate

    return run_evaluate(
        find_root(),
        backend=args.backend,
        scenario_id=args.scenario,
        as_json=args.json,
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hip", description="Hermes Instruction Engineering Pack CLI")
    p.add_argument("--version", action="version", version=f"hip {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("inspect", help="environment and package overview")
    sp.set_defaults(func=cmd_inspect)

    src = sub.add_parser("sources", help="source acquisition and audit")
    ssub = src.add_subparsers(dest="src_cmd", required=True)

    sl = ssub.add_parser("list", help="list recorded sources")
    sl.add_argument("--status", choices=["fetched", "failed", "skipped", "pending"])
    sl.add_argument("--json", action="store_true")
    sl.set_defaults(func=cmd_sources_list)

    si = ssub.add_parser("import", help="fetch sources (idempotent)")
    si.add_argument("--gist-user", default="jczzbczz-rgb")
    si.add_argument("--pinned", action="append", help="pinned raw gist URL")
    si.add_argument("--repo", action="append", help="github repo URL")
    si.add_argument(
        "--spec",
        action="store_true",
        help="import the full spec source set (default gist user + pinned + both repos)",
    )
    si.set_defaults(func=cmd_sources_import)

    sa = ssub.add_parser("audit", help="post-import file audit (hashes, risks)")
    sa.set_defaults(func=cmd_sources_audit)

    cl = sub.add_parser("classify", help="classify archived sources into categories")
    cl.set_defaults(func=cmd_classify)

    nz = sub.add_parser("normalize", help="build operational modules with provenance")
    nz.set_defaults(func=cmd_normalize)

    mods = sub.add_parser("modules", help="module registry operations")
    msub = mods.add_subparsers(dest="mods_cmd", required=True)
    ml = msub.add_parser("list", help="list discovered modules")
    ml.add_argument("--json", action="store_true")
    ml.set_defaults(func=cmd_modules_list)
    mv = msub.add_parser("validate", help="validate modules and archive separation")
    mv.set_defaults(func=cmd_modules_validate)

    rs = sub.add_parser("resolve", help="resolve modules for a task context")
    rs.add_argument("task_type")
    rs.add_argument("--persona", default=None, help="persona name or 'none'")
    rs.add_argument("--json", action="store_true")
    rs.set_defaults(func=cmd_resolve)

    ad = sub.add_parser("adapter", help="Hermes Agent integration")
    adsub = ad.add_subparsers(dest="adapter_cmd", required=True)
    ac = adsub.add_parser("check", help="check Hermes compatibility")
    ac.add_argument("--json", action="store_true")
    ac.set_defaults(func=cmd_adapter_check)
    ai = adsub.add_parser("install", help="install hip-* personalities into Hermes config (backup first)")
    ai.add_argument("--dry-run", action="store_true")
    ai.add_argument("--with-instructions", action="store_true", help="also append core instruction file paths")
    ai.set_defaults(func=cmd_adapter_install)
    ar = adsub.add_parser("rollback", help="restore config from pack backup")
    ar.set_defaults(func=cmd_adapter_rollback)
    au = adsub.add_parser("uninstall", help="remove hip-* personalities (backup first)")
    au.set_defaults(func=cmd_adapter_uninstall)

    tp = sub.add_parser("test", help="run the automated test suite")
    tp.set_defaults(func=cmd_test)

    rp = sub.add_parser("report", help="generate reports/status-summary.md")
    rp.set_defaults(func=cmd_report)

    tc = sub.add_parser("techniques", help="extract jailbreak technique index per file")
    tc.set_defaults(func=cmd_techniques)

    ev = sub.add_parser("evaluate", help="run evaluation scenarios (backend: none|mock|openai)")
    ev.add_argument("--backend", choices=["none", "mock", "openai"], default="none")
    ev.add_argument("--scenario", help="run a single scenario id (e.g. S01-multifile-feature)")
    ev.add_argument("--json", action="store_true")
    ev.set_defaults(func=cmd_evaluate)
    return p


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "src_cmd", None) == "import" and getattr(args, "spec", False):
        args.pinned = list(args.pinned or []) + [
            "https://gist.githubusercontent.com/jczzbczz-rgb/5590e4adb53115dfe353919b27757181/raw/aaa10d10426baff855e2c6e0aaced0ed753227a2/gistfile1.txt"
        ]
        args.repo = list(args.repo or []) + [
            "https://github.com/togg53192-cmd/jailbreaks",
            "https://github.com/Mrzimia99/hellowork",
        ]
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
