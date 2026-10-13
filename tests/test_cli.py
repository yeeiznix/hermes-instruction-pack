import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-m", "hermes_instruction_pack.cli", *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=env,
        timeout=120,
    )


def test_inspect_exit_zero():
    p = run_cli("inspect")
    assert p.returncode == 0, p.stderr
    assert "hip version" in p.stdout


def test_sources_list():
    p = run_cli("sources", "list")
    assert p.returncode == 0, p.stderr
    assert "total:" in p.stdout


def test_modules_list_and_validate():
    p = run_cli("modules", "list")
    assert p.returncode == 0
    assert "core-builder" in p.stdout
    p2 = run_cli("modules", "validate")
    assert p2.returncode == 0, p2.stdout + p2.stderr


def test_resolve_ok_and_fail():
    p = run_cli("resolve", "coding", "--persona", "axiom")
    assert p.returncode == 0, p.stderr
    assert "persona-axiom" in p.stdout
    p2 = run_cli("resolve", "nonsense-task")
    assert p2.returncode == 1
    assert "ERROR" in p2.stderr
