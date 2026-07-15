#!/usr/bin/env python3
"""Build and verify a portable directory of enabled skill symlinks."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import datetime, timezone
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


GLOBAL_SKILL_ROOTS = (Path(".agents/skills"), Path(".claude/skills"))


def _next_backup_dir(repo: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = repo / ".migration-backups" / stamp
    suffix = 1
    while root.exists():
        root = repo / ".migration-backups" / f"{stamp}-{suffix}"
        suffix += 1
    return root


def install_global_links(repo: Path, home: Path, migrate: bool) -> Path:
    repo = repo.resolve()
    home = home.expanduser().resolve()
    verify_repo(repo)
    enabled = (repo / "enabled").resolve()
    targets = [(relative, home / relative) for relative in GLOBAL_SKILL_ROOTS]

    for _, target in targets:
        if target.is_symlink() and target.resolve() == enabled:
            continue
        if (target.exists() or target.is_symlink()) and not migrate:
            raise RegistryError(
                f"global skill directory exists: {target}; rerun with --migrate"
            )

    backup = _next_backup_dir(repo)
    for relative, target in targets:
        if target.is_symlink() and target.resolve() == enabled:
            continue
        if target.exists() or target.is_symlink():
            backup_target = backup / relative
            backup_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), str(backup_target))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(enabled, target_is_directory=True)
    return backup


def verify_global_links(repo: Path, home: Path) -> int:
    enabled = (repo.resolve() / "enabled").resolve()
    for relative in GLOBAL_SKILL_ROOTS:
        target = home.expanduser().resolve() / relative
        if not target.is_symlink():
            raise RegistryError(f"global skill root is not a symlink: {target}")
        if target.resolve() != enabled:
            raise RegistryError(f"global skill root points elsewhere: {target}")
    return len(GLOBAL_SKILL_ROOTS)


def write_sources_md(repo: Path) -> Path:
    repo = repo.resolve()
    registry = load_registry(repo)
    lines = [
        "# 第三方 Skill 来源",
        "",
        "第三方内容通过 Git submodule 固定版本，本仓库只保存上游 commit 指针、启用清单和软链接，不复制其历史。",
        "",
        "| 分组 | 上游仓库 | 本仓库路径 | 官方/兼容安装命令 |",
        "|---|---|---|---|",
    ]
    for source in registry.get("sources", []):
        title = str(source.get("title", source["id"])).replace("|", "\\|")
        url = str(source["url"])
        display_url = url[:-4] if url.endswith(".git") else url
        command = str(source.get("installCommand", "—")).replace("|", "\\|")
        lines.append(
            f"| {title} | [{source['id']}]({display_url}) | "
            f"`{source['checkout']}` | `{command}` |"
        )
    lines.extend(
        [
            "",
            "当前固定版本可通过以下命令查看：",
            "",
            "```bash",
            "git submodule status",
            "```",
            "",
            "本仓库的日常使用不执行上表中的逐项安装命令；`scripts/bootstrap.sh` 会统一初始化来源并建立全局链接。安装命令仅用于来源追溯和故障恢复。",
            "",
        ]
    )
    output = repo / "SOURCES.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("build", "verify", "sources", "install-global", "verify-global"),
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--migrate", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "build":
            result = len(build_links(args.repo))
        elif args.command == "verify":
            result = len(verify_repo(args.repo))
        elif args.command == "sources":
            write_sources_md(args.repo)
            result = len(load_registry(args.repo).get("sources", []))
        elif args.command == "install-global":
            backup = install_global_links(args.repo, args.home, args.migrate)
            result = verify_global_links(args.repo, args.home)
            print(f"backup: {backup}")
        else:
            result = verify_global_links(args.repo, args.home)
    except RegistryError as error:
        parser.error(str(error))
    print(f"{args.command}: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
