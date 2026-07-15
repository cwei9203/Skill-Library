#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/lib.sh"
repo=$(skilllib_repo_root)
migrate=false

if [[ "${1:-}" == "--migrate" ]]; then
  migrate=true
elif [[ $# -gt 0 ]]; then
  echo "usage: $0 [--migrate]" >&2
  exit 2
fi

skilllib_use_macos_proxy
git -C "$repo" submodule sync --recursive
git -C "$repo" submodule update --init --recursive --depth 1
python3 "$repo/scripts/skilllib.py" sources --repo "$repo"
python3 "$repo/scripts/skilllib.py" build --repo "$repo"
python3 "$repo/scripts/skilllib.py" verify --repo "$repo"

args=(install-global --repo "$repo")
if [[ "$migrate" == true ]]; then
  args+=(--migrate)
fi
python3 "$repo/scripts/skilllib.py" "${args[@]}"
python3 "$repo/scripts/skilllib.py" verify-global --repo "$repo"
