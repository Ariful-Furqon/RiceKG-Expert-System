from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RULES_PATH = BASE_DIR / "analysis" / "anon_rules.json"
DEFAULT_OUT = BASE_DIR / "anon_bundle" / "ricekg-review"


def rmtree(path: Path, attempts: int = 5) -> None:
    # Remove a directory tree, tolerating Windows/OneDrive locking.
    #
    # Cloud-sync clients hold transient handles on freshly written files, and git
    # marks objects read-only, so a plain shutil.rmtree raises PermissionError
    # here. Clear the read-only bit and retry briefly before giving up.
    def on_error(func, target, _exc):
        os.chmod(target, 0o700)
        func(target)

    for attempt in range(attempts):
        if not path.exists():
            return
        try:
            # `onexc` only exists on Python 3.12+; `onerror` is deprecated there.
            if sys.version_info >= (3, 12):
                shutil.rmtree(path, onexc=on_error)
            else:
                shutil.rmtree(path, onerror=on_error)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.4 * (attempt + 1))


def load_rules() -> dict:
    with RULES_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def tracked_files() -> list[str]:
    # Repo-relative paths of all git-tracked files (POSIX separators).
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=BASE_DIR, capture_output=True, check=True,
    ).stdout.decode("utf-8")
    return [p for p in out.split("\0") if p]


def is_text(rel_path: str, rules: dict) -> bool:
    name = Path(rel_path).name
    return (
        name in rules["text_filenames"]
        or Path(rel_path).suffix.lower() in rules["text_extensions"]
    )


def substitute(text: str, rules: dict) -> str:
    for needle, replacement in rules["substitutions"]:
        text = text.replace(needle, replacement)
    return text


def copy_and_anonymise(out_dir: Path, rules: dict, quiet: bool) -> int:
    excluded = set(rules["exclude_from_bundle"])
    copied = 0
    for rel in tracked_files():
        if rel in excluded:
            continue
        src = BASE_DIR / rel
        if not src.exists():          # deleted-but-staged edge case
            continue
        dst = out_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if is_text(rel, rules):
            try:
                original = src.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                shutil.copy2(src, dst)
                copied += 1
                continue
            dst.write_text(substitute(original, rules), encoding="utf-8")
        else:
            shutil.copy2(src, dst)
        copied += 1
    if not quiet:
        print(f"  copied {copied} files (excluded {len(excluded)} tooling files)")
    return copied


def verify(out_dir: Path, rules: dict) -> list[str]:
    # Return a list of deny-list violations found anywhere in the bundle.
    violations: list[str] = []
    deny = rules["deny_list"]
    for path in sorted(out_dir.rglob("*")):
        if path.is_dir() or ".git" in path.parts:
            continue
        rel = path.relative_to(out_dir).as_posix()
        for term in deny:
            if term in rel:
                violations.append(f"{rel}: path contains {term!r}")
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue                   # binary asset: nothing to scan
        for lineno, line in enumerate(content.splitlines(), 1):
            for term in deny:
                if term in line:
                    violations.append(f"{rel}:{lineno}: contains {term!r}")
    return violations


def squash_history(out_dir: Path, quiet: bool) -> None:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Anonymous",
        "GIT_AUTHOR_EMAIL": "review@anonymous.invalid",
        "GIT_COMMITTER_NAME": "Anonymous",
        "GIT_COMMITTER_EMAIL": "review@anonymous.invalid",
    }
    run = lambda *a: subprocess.run(a, cwd=out_dir, env=env, check=True,
                                    capture_output=True)
    run("git", "init", "-q")
    run("git", "add", "-A")
    run("git", "commit", "-q", "-m", "Initial submission")
    if not quiet:
        print("  history squashed to a single anonymous commit")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build an anonymised review bundle for double-blind submission.")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--no-git", action="store_true",
                    help="skip git init/commit (used by the test suite)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    out_dir = args.out if args.out.is_absolute() else BASE_DIR / args.out
    rules = load_rules()

    if not args.quiet:
        print(f"Building anonymised review bundle in {out_dir} ...")

    rmtree(out_dir)
    out_dir.mkdir(parents=True)

    copy_and_anonymise(out_dir, rules, args.quiet)
    if not args.no_git:
        squash_history(out_dir, args.quiet)

    violations = verify(out_dir, rules)
    if violations:
        print("\nANONYMISATION FAILED — deny-list matches in the bundle:\n",
              file=sys.stderr)
        for v in violations[:40]:
            print(f"  {v}", file=sys.stderr)
        if len(violations) > 40:
            print(f"  ... and {len(violations) - 40} more", file=sys.stderr)
        print("\nThe bundle has been deleted. Add substitution rules to "
              "analysis/anon_rules.json and rebuild.", file=sys.stderr)
        rmtree(out_dir)
        return 1

    if not args.quiet:
        print(f"\nVerified clean against {len(rules['deny_list'])} deny-list terms.")
        print(f"Bundle: {out_dir}")
        print("Upload to anonymous.4open.science or a restricted Zenodo deposit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
