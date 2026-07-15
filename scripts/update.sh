#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/lib.sh"
repo=$(skilllib_repo_root)
verify_global=true

if [[ "${1:-}" == "--no-global" ]]; then
  verify_global=false
elif [[ $# -gt 0 ]]; then
  echo "usage: $0 [--no-global]" >&2
  exit 2
fi

skilllib_use_macos_proxy
git -C "$repo" submodule sync --recursive
git -C "$repo" submodule update --init --recursive --depth 1
git -C "$repo" submodule update --remote --merge --recursive
python3 "$repo/scripts/skilllib.py" build --repo "$repo"
python3 "$repo/scripts/skilllib.py" verify --repo "$repo"
python3 -m unittest discover -s "$repo/tests" -v

if [[ "$verify_global" == true ]]; then
  python3 "$repo/scripts/skilllib.py" verify-global --repo "$repo"
fi

git -C "$repo" status --short
