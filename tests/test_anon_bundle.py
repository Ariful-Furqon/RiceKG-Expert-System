"""Tests for the double-blind review bundle builder and its deny-list gate.

The bundle is the artifact a reviewer receives. A leaked identifier there is a
desk-reject, so the deny-list scan is the part that must be trusted: these tests
check that it passes on a correctly built bundle and fails on a planted leak.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "analysis"))

import build_anon_bundle as bab  # noqa: E402


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    """Build a real bundle once into a temp directory (no git, for speed)."""
    out = tmp_path_factory.mktemp("anon") / "ricekg-review"
    rc = subprocess.run(
        [sys.executable, str(BASE_DIR / "analysis" / "build_anon_bundle.py"),
         "--out", str(out), "--no-git", "--quiet"],
        cwd=BASE_DIR, capture_output=True, text=True,
    )
    assert rc.returncode == 0, f"bundle build failed:\n{rc.stdout}\n{rc.stderr}"
    return out


def test_bundle_is_clean_against_deny_list(bundle):
    """The shipped bundle must contain no deny-list term, in content or path."""
    violations = bab.verify(bundle, bab.load_rules())
    assert violations == [], "deny-list violations:\n" + "\n".join(violations[:20])


def test_deny_list_catches_a_planted_leak(bundle, tmp_path):
    """A planted identifier must be detected — the gate must not be vacuous."""
    planted = tmp_path / "planted"
    shutil.copytree(bundle, planted)
    (planted / "docs" / "leak.md").write_text(
        "Contact: ariful.furqon@unej.ac.id\n", encoding="utf-8"
    )
    violations = bab.verify(planted, bab.load_rules())
    assert violations, "deny-list scan failed to detect a planted identifier"
    assert any("leak.md" in v for v in violations)


def test_builder_exits_nonzero_when_verification_fails(tmp_path, monkeypatch):
    """A bundle that cannot be verified must not be produced at all."""
    rules = bab.load_rules()
    rules["substitutions"] = []          # disable anonymisation entirely
    monkeypatch.setattr(bab, "load_rules", lambda: rules)
    monkeypatch.setattr(sys, "argv",
                        ["build_anon_bundle.py", "--out", str(tmp_path / "b"),
                         "--no-git", "--quiet"])
    assert bab.main() == 1
    assert not (tmp_path / "b").exists(), "failed bundle was left on disk"


def test_tooling_files_are_excluded(bundle):
    """The rules file and builder must never travel with the bundle."""
    for rel in json.loads(
        (BASE_DIR / "analysis" / "anon_rules.json").read_text(encoding="utf-8")
    )["exclude_from_bundle"]:
        assert not (bundle / rel).exists(), f"{rel} leaked into the bundle"


def test_substitution_order_removes_bare_surname(bundle):
    """Regression: 'Furqon, Muhammad Ariful' once left 'Furqon,' behind."""
    rules = bab.load_rules()
    out = bab.substitute("author = {Furqon, Muhammad Ariful}", rules)
    assert "Furqon" not in out and "Ariful" not in out, out


def test_working_tree_is_untouched():
    """Building a bundle must never modify the repository it is built from."""
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", ":!anon_bundle"],
        cwd=BASE_DIR, capture_output=True, text=True,
    ).stdout
    before = set(dirty.splitlines())
    subprocess.run(
        [sys.executable, str(BASE_DIR / "analysis" / "build_anon_bundle.py"),
         "--no-git", "--quiet"],
        cwd=BASE_DIR, capture_output=True, check=True,
    )
    after = set(subprocess.run(
        ["git", "status", "--porcelain", "--", ":!anon_bundle"],
        cwd=BASE_DIR, capture_output=True, text=True,
    ).stdout.splitlines())
    assert before == after, f"working tree changed: {after - before}"
