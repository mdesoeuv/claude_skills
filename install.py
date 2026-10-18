#!/usr/bin/env python3
"""Install the skills in this repository into a Claude Code skills directory.

Examples:
  ./install.py                   core skills -> ~/.claude/skills (personal)
  ./install.py --all             core + recommended -> ~/.claude/skills
  ./install.py --project         core skills -> ./.claude/skills of the current repo
  ./install.py --all --copy      copy instead of symlink (for committing into a repo)
  ./install.py --uninstall       remove everything this repo installed, any tier
  ./install.py --list            show skills and tiers without touching anything

Symlinks stay in sync with `git pull`. Copies get a hidden marker file so a later
run can refresh them. Directories this script did not create are never touched.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
SKILLS_DIR = REPO_DIR / "skills"
MARKER = ".installed-from"
TIERS = ("core", "recommended")


def tier_of(skill_dir: Path) -> str:
    """Read metadata.tier from the SKILL.md frontmatter (no YAML dependency)."""
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise ValueError(f"{skill_dir.name}: SKILL.md has no frontmatter")
    tier = re.search(r"^\s+tier:\s*(\S+)", match.group(1), re.M)
    if not tier or tier.group(1) not in TIERS:
        raise ValueError(f"{skill_dir.name}: metadata.tier must be one of {TIERS}")
    return tier.group(1)


def repo_skills() -> list[tuple[str, str, Path]]:
    return sorted(
        (d.name, tier_of(d), d)
        for d in SKILLS_DIR.iterdir()
        if d.is_dir() and (d / "SKILL.md").is_file()
    )


def managed_by_us(dest: Path) -> str | None:
    """Return 'link' or 'copy' if dest was installed from this repo, else None."""
    if dest.is_symlink():
        try:
            if dest.resolve().parent == SKILLS_DIR.resolve():
                return "link"
        except OSError:
            pass
        return None
    marker = dest / MARKER
    if dest.is_dir() and marker.is_file():
        if marker.read_text(encoding="utf-8").strip() == str(SKILLS_DIR.resolve()):
            return "copy"
    return None


def remove(dest: Path) -> None:
    if dest.is_symlink():
        dest.unlink()
    else:
        shutil.rmtree(dest)


def install_one(src: Path, dest: Path, copy: bool, dry_run: bool) -> str:
    owner = managed_by_us(dest)
    if (dest.exists() or dest.is_symlink()) and owner is None:
        return "skip (exists and was not installed by this script)"
    if not dry_run:
        if owner:
            remove(dest)
        if copy:
            shutil.copytree(src, dest)
            (dest / MARKER).write_text(str(SKILLS_DIR.resolve()) + "\n", encoding="utf-8")
        else:
            dest.symlink_to(src, target_is_directory=True)
    return "copy" if copy else "link"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--all", action="store_true", help="install recommended skills too")
    parser.add_argument("--project", action="store_true",
                        help="target ./.claude/skills in the current directory instead of ~/.claude/skills")
    parser.add_argument("--target", type=Path, help="explicit skills directory (overrides --project)")
    parser.add_argument("--copy", action="store_true", help="copy instead of symlink")
    parser.add_argument("--uninstall", action="store_true",
                        help="remove every skill this repo installed, regardless of tier")
    parser.add_argument("--list", action="store_true", help="list skills and tiers, change nothing")
    parser.add_argument("--dry-run", action="store_true", help="print actions without performing them")
    args = parser.parse_args(argv)

    try:
        skills = repo_skills()
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    if args.list:
        for name, tier, _ in skills:
            print(f"{name:22} {tier}")
        return 0

    if args.target:
        target = args.target.expanduser().resolve()
    elif args.project:
        target = Path.cwd() / ".claude" / "skills"
    else:
        target = Path.home() / ".claude" / "skills"

    if args.uninstall:
        removed = 0
        for name, _, _ in skills:
            dest = target / name
            owner = managed_by_us(dest)
            if owner:
                if not args.dry_run:
                    remove(dest)
                print(f"removed  {dest} ({owner})")
                removed += 1
        print(f"{removed} skill(s) removed from {target}" + (" [dry run]" if args.dry_run else ""))
        return 0

    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)
    wanted = [s for s in skills if args.all or s[1] == "core"]
    for name, tier, src in wanted:
        dest = target / name
        result = install_one(src, dest, args.copy, args.dry_run)
        print(f"{result:8} {dest} ({tier})")
    print(f"{len(wanted)} skill(s) processed into {target}" + (" [dry run]" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
