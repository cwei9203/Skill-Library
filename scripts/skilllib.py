#!/usr/bin/env python3
"""Build and verify a portable directory of enabled skill symlinks."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict


class RegistryError(RuntimeError):
    pass


def load_registry(repo: Path) -> dict:
    path = repo / "registry.json"
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise RegistryError(f"registry not found: {path}") from error
    if registry.get("schemaVersion") != 1:
        raise RegistryError("unsupported registry schema")
    return registry


def _skill_dirs(root: Path) -> Dict[str, Path]:
    if not root.is_dir():
        return {}
    found: Dict[str, Path] = {}
    for skill_md in sorted(root.rglob("SKILL.md")):
        skill_dir = skill_md.parent
        name = skill_dir.name
        if name in found and found[name] != skill_dir:
            raise RegistryError(
                f"duplicate skill '{name}' in {found[name]} and {skill_dir}"
            )
        found[name] = skill_dir
    return found


def collect_skills(repo: Path) -> Dict[str, Path]:
    registry = load_registry(repo)
    collected: Dict[str, Path] = {}

    def add(name: str, path: Path) -> None:
        if name in collected and collected[name] != path:
            raise RegistryError(
                f"duplicate skill '{name}' in {collected[name]} and {path}"
            )
        collected[name] = path

    for root_name in registry.get("localRoots", []):
        for name, path in _skill_dirs(repo / root_name).items():
            add(name, path)

    for source in registry.get("sources", []):
        available: Dict[str, Path] = {}
        checkout = repo / source["checkout"]
        for root_name in source.get("skillRoots", []):
            for name, path in _skill_dirs(checkout / root_name).items():
                if name in available and available[name] != path:
                    raise RegistryError(
                        f"duplicate skill '{name}' inside source {source['id']}"
                    )
                available[name] = path
        for name in source.get("include", []):
            if name not in available:
                raise RegistryError(
                    f"declared skill '{name}' missing from source {source['id']}"
                )
            add(name, available[name])

    return dict(sorted(collected.items()))


def build_links(repo: Path) -> list[str]:
    repo = repo.resolve()
    skills = collect_skills(repo)
    enabled = repo / "enabled"
    enabled.mkdir(parents=True, exist_ok=True)

    for entry in enabled.iterdir():
        if entry.is_symlink():
            entry.unlink()
        else:
            raise RegistryError(f"generated directory contains non-link entry: {entry}")

    for name, target in skills.items():
        relative_target = os.path.relpath(target, start=enabled)
        (enabled / name).symlink_to(relative_target, target_is_directory=True)
    return list(skills)


def verify_repo(repo: Path) -> list[str]:
    repo = repo.resolve()
    enabled = repo / "enabled"
    if not enabled.is_dir():
        raise RegistryError("enabled directory is missing")

    actual = {entry.name: entry for entry in enabled.iterdir()}
    for name, link in sorted(actual.items()):
        if not link.is_symlink():
            raise RegistryError(f"enabled entry is not a symlink: {name}")
        if not link.exists():
            raise RegistryError(f"broken enabled symlink: {name}")

    expected = collect_skills(repo)
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise RegistryError(f"enabled set mismatch; missing={missing}, extra={extra}")

    for name, link in sorted(actual.items()):
        if not (link.resolve() / "SKILL.md").is_file():
            raise RegistryError(f"SKILL.md missing behind enabled link: {name}")
    return sorted(actual)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        names = (
            build_links(args.repo)
            if args.command == "build"
            else verify_repo(args.repo)
        )
    except RegistryError as error:
        parser.error(str(error))
    print(f"{args.command}: {len(names)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
