#!/usr/bin/env python3
"""Create and apply reviewable copy plans for bee-static assets."""

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, Request, build_opener


PLAN_VERSION = 2
CDN_BASE_URL = "https://static-cdn-test.mifengjiaoyu.com/"
CDN_CHECK_MAX_AGE_SECONDS = 600
ICONFONT_FOLDER_PATTERN = re.compile(r"^font_.+_([a-z0-9]+)$")
ICONFONT_ROOT = Path("hashIconfontDir")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_destination(destination):
    raw = str(destination).replace("\\", "/")
    path = PurePosixPath(raw)
    if not raw or path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ValueError("destination must be a non-empty relative path inside the repository")
    if ".git" in path.parts:
        raise ValueError("destination cannot include .git")
    return Path(*path.parts)


def _inside(path, root):
    try:
        return os.path.commonpath([str(path), str(root)]) == str(root)
    except ValueError:
        return False


def _reject_symlink(path):
    if path.is_symlink():
        raise ValueError(f"symbolic link sources are not allowed: {path}")


def _source_files(source):
    source = Path(source).expanduser()
    if not source.exists():
        raise ValueError(f"source does not exist: {source}")
    _reject_symlink(source)
    if source.is_file():
        return [(source.resolve(), Path(source.name))]
    if not source.is_dir():
        raise ValueError(f"source is not a regular file or directory: {source}")
    files = []
    for candidate in sorted(source.rglob("*")):
        _reject_symlink(candidate)
        if candidate.is_file():
            files.append((candidate.resolve(), candidate.relative_to(source)))
    if not files:
        raise ValueError(f"source directory contains no files: {source}")
    return files


def extract_iconfont_hash(source):
    source = Path(source).expanduser()
    if not source.is_dir() or source.is_symlink():
        raise ValueError(f"iconfont source must be a regular directory: {source}")
    match = ICONFONT_FOLDER_PATTERN.fullmatch(source.name)
    if not match:
        raise ValueError(
            f"iconfont folder must match font_<project-id>_<hash>; got: {source.name}"
        )
    return match.group(1)


def _git_context(repo):
    def run(*args):
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else None

    return {
        "branch": run("branch", "--show-current"),
        "remote": run("remote", "get-url", "origin"),
        "head": run("rev-parse", "HEAD"),
    }


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _probe_cdn(url, timeout):
    opener = build_opener(_NoRedirect)

    def request(method, headers=None):
        try:
            with opener.open(Request(url, method=method, headers=headers or {}), timeout=timeout) as response:
                return response.status
        except HTTPError as error:
            return error.code

    status = request("HEAD")
    if status in (405, 501):
        status = request("GET", {"Range": "bytes=0-0"})
    return status


def _cdn_url(relative_target):
    relative_target = _validate_destination(relative_target).as_posix()
    return CDN_BASE_URL + quote(relative_target, safe="/-._~")


def check_cdn(plan, probe=None, timeout=10):
    if plan.get("version") != PLAN_VERSION:
        raise ValueError("unsupported plan version")
    probe = probe or _probe_cdn
    checked = copy.deepcopy(plan)
    counts = {"available": 0, "exists": 0, "unknown": 0}
    for item in checked.get("files", []):
        url = _cdn_url(item["relative_target"])
        error_message = None
        try:
            http_status = int(probe(url, timeout))
        except Exception as error:
            http_status = None
            error_message = f"{type(error).__name__}: {error}"
        if http_status in (404, 410):
            status = "available"
        elif http_status is not None and 200 <= http_status < 400:
            status = "exists"
        else:
            status = "unknown"
        counts[status] += 1
        item["cdn"] = {"url": url, "status": status, "http_status": http_status}
        if error_message:
            item["cdn"]["error"] = error_message
    checked["cdn_check"] = {
        "base_url": CDN_BASE_URL,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "counts": counts,
    }
    return checked


def build_plan(repo, sources, destination):
    repo = Path(repo).expanduser().resolve()
    if not repo.is_dir():
        raise ValueError(f"repository directory does not exist: {repo}")
    destination = _validate_destination(destination)
    destination_root = (repo / destination).resolve()
    if not _inside(destination_root, repo) or destination_root == repo:
        raise ValueError("destination must resolve inside the repository")

    planned = []
    targets = set()
    for source in sources:
        for source_file, relative in _source_files(source):
            target = (destination_root / relative).resolve()
            if not _inside(target, repo):
                raise ValueError(f"target escapes repository: {target}")
            target_key = str(target)
            if target_key in targets:
                raise ValueError(f"multiple sources map to the same target: {target}")
            targets.add(target_key)
            source_hash = sha256(source_file)
            if not target.exists():
                status = "new"
            elif not target.is_file() or target.is_symlink():
                status = "conflict"
            elif sha256(target) == source_hash:
                status = "identical"
            else:
                status = "conflict"
            planned.append(
                {
                    "source": str(source_file),
                    "target": str(target),
                    "relative_target": target.relative_to(repo).as_posix(),
                    "sha256": source_hash,
                    "size": source_file.stat().st_size,
                    "status": status,
                }
            )

    return {
        "version": PLAN_VERSION,
        "repo": str(repo),
        "destination": destination.as_posix(),
        "git": _git_context(repo),
        "files": planned,
    }


def build_iconfont_plan(repo, source):
    repo_path = Path(repo).expanduser().resolve()
    iconfont_root = repo_path / ICONFONT_ROOT
    if iconfont_root.is_symlink() or (iconfont_root.exists() and not iconfont_root.is_dir()):
        raise ValueError(f"hashIconfontDir must be a directory: {iconfont_root}")
    root_status = "existing" if iconfont_root.is_dir() else "create"
    iconfont_hash = extract_iconfont_hash(source)
    destination = ICONFONT_ROOT / iconfont_hash
    plan = build_plan(repo, [source], destination)
    plan["iconfont"] = {
        "source_folder": Path(source).expanduser().name,
        "hash": iconfont_hash,
        "root": ICONFONT_ROOT.as_posix(),
        "root_status": root_status,
    }
    return plan


def apply_plan(plan_file, overwrite_conflicts=False, allow_cdn_overwrite=False, cdn_probe=None):
    plan_file = Path(plan_file).expanduser()
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    if plan.get("version") != PLAN_VERSION:
        raise ValueError("unsupported plan version")
    repo = Path(plan["repo"]).resolve()
    if not repo.is_dir():
        raise ValueError(f"repository directory does not exist: {repo}")
    cdn_check = plan.get("cdn_check")
    if not cdn_check or cdn_check.get("base_url") != CDN_BASE_URL:
        raise ValueError("completed CDN check is required before apply")
    try:
        checked_at = datetime.fromisoformat(cdn_check["checked_at"])
        age = (datetime.now(timezone.utc) - checked_at).total_seconds()
    except (KeyError, TypeError, ValueError):
        raise ValueError("CDN check timestamp is invalid")
    if age < -60 or age > CDN_CHECK_MAX_AGE_SECONDS:
        raise ValueError("CDN check is stale; check again and reconfirm if results changed")
    fresh_plan = check_cdn(plan, probe=cdn_probe)
    if len(fresh_plan.get("files", [])) != len(plan.get("files", [])):
        raise ValueError("CDN status changed since confirmation; create a new plan")
    for previous, current in zip(plan["files"], fresh_plan["files"]):
        if (
            previous.get("relative_target") != current.get("relative_target")
            or previous.get("cdn", {}).get("status") != current.get("cdn", {}).get("status")
        ):
            raise ValueError("CDN status changed since confirmation; create a new plan")
    plan = fresh_plan
    destination = _validate_destination(plan["destination"])
    planned_git = plan.get("git", {})
    current_git = _git_context(repo)
    for key in ("branch", "remote", "head"):
        if planned_git.get(key) is not None and planned_git[key] != current_git.get(key):
            raise ValueError(f"git {key} changed since planning")

    actions = []
    for item in plan.get("files", []):
        source = Path(item["source"])
        target = Path(item["target"])
        relative_target = _validate_destination(item["relative_target"])
        try:
            relative_target.relative_to(destination)
        except ValueError:
            raise ValueError(f"inconsistent target outside planned destination: {target}")
        expected_target = (repo / relative_target).resolve()
        if target.resolve() != expected_target:
            raise ValueError(f"inconsistent target in plan: {target}")
        cdn = item.get("cdn", {})
        if cdn.get("url") != _cdn_url(item["relative_target"]):
            raise ValueError(f"CDN check is missing or inconsistent: {target}")
        if cdn.get("status") == "unknown":
            raise ValueError(f"CDN URL availability is unknown: {cdn['url']}")
        if cdn.get("status") == "exists" and not allow_cdn_overwrite:
            raise ValueError(f"CDN URL already exists; explicit overwrite permission required: {cdn['url']}")
        if cdn.get("status") not in ("available", "exists"):
            raise ValueError(f"CDN check is missing or inconsistent: {target}")
        _reject_symlink(source)
        if not source.is_file() or sha256(source) != item["sha256"]:
            raise ValueError(f"source changed since planning: {source}")
        if not _inside(target.resolve(), repo):
            raise ValueError(f"target escapes repository: {target}")
        if target.exists():
            if target.is_file() and not target.is_symlink() and sha256(target) == item["sha256"]:
                actions.append(("skip", source, target))
            elif overwrite_conflicts:
                actions.append(("copy", source, target))
            else:
                raise ValueError(f"conflicting target requires explicit overwrite: {target}")
        else:
            actions.append(("copy", source, target))

    copied = skipped = 0
    for action, source, target in actions:
        if action == "skip":
            skipped += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as temporary:
            temporary_path = Path(temporary.name)
        try:
            shutil.copy2(source, temporary_path)
            os.replace(str(temporary_path), str(target))
        finally:
            if temporary_path.exists():
                temporary_path.unlink()
        copied += 1
    return {"copied": copied, "skipped": skipped, "repo": str(repo)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan_parser = subparsers.add_parser("plan", help="create a JSON copy plan")
    plan_parser.add_argument("--repo", required=True)
    destination_group = plan_parser.add_mutually_exclusive_group(required=True)
    destination_group.add_argument("--destination")
    destination_group.add_argument(
        "--iconfont",
        action="store_true",
        help="place a font_<project-id>_<hash> source under hashIconfontDir/<hash>",
    )
    plan_parser.add_argument("--source", action="append", required=True)
    plan_parser.add_argument("--output", required=True)
    check_parser = subparsers.add_parser("check-cdn", help="check planned CDN URLs and update the plan")
    check_parser.add_argument("--plan", required=True)
    check_parser.add_argument("--timeout", type=float, default=10)
    apply_parser = subparsers.add_parser("apply", help="apply a confirmed JSON plan")
    apply_parser.add_argument("--plan", required=True)
    apply_parser.add_argument("--overwrite-conflicts", action="store_true")
    apply_parser.add_argument("--allow-cdn-overwrite", action="store_true")
    args = parser.parse_args()

    if args.command == "plan":
        if args.iconfont:
            if len(args.source) != 1:
                parser.error("--iconfont requires exactly one --source directory")
            plan = build_iconfont_plan(args.repo, args.source[0])
        else:
            plan = build_plan(args.repo, args.source, args.destination)
        output = Path(args.output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    elif args.command == "check-cdn":
        plan_path = Path(args.plan).expanduser()
        plan = check_cdn(json.loads(plan_path.read_text(encoding="utf-8")), timeout=args.timeout)
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print(
            json.dumps(
                apply_plan(args.plan, args.overwrite_conflicts, args.allow_cdn_overwrite),
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
