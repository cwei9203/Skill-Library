#!/usr/bin/env bash

skilllib_repo_root() {
  cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd
}

skilllib_use_macos_proxy() {
  if [[ "$(uname -s)" != "Darwin" ]] || [[ -n "${HTTPS_PROXY:-${https_proxy:-}}" ]]; then
    return
  fi

  local enabled host port
  enabled=$(scutil --proxy | awk '/HTTPSEnable/ { print $3; exit }')
  host=$(scutil --proxy | awk '/HTTPSProxy/ { print $3; exit }')
  port=$(scutil --proxy | awk '/HTTPSPort/ { print $3; exit }')
  if [[ "$enabled" == "1" && -n "$host" && -n "$port" ]]; then
    export HTTPS_PROXY="http://${host}:${port}"
    export HTTP_PROXY="$HTTPS_PROXY"
  fi
}
