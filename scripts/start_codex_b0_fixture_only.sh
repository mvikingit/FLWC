#!/usr/bin/env bash
set -euo pipefail

cd /data/strategy/flwc

if ! command -v codex-lsdserv >/dev/null 2>&1; then
  echo "FAIL_CLOSED: codex-lsdserv not found"
  exit 2
fi

codex-lsdserv --version
STATUS="$(codex-lsdserv login status 2>/dev/null || true)"
printf '%s\n' "$STATUS"

if ! printf '%s\n' "$STATUS" | grep -qi 'Logged in'; then
  echo "FAIL_CLOSED: codex-lsdserv login status is not confirmed. Do not start Codex prompt."
  exit 2
fi

exec codex-lsdserv "$(cat prompts/codex/B0_FIXTURE_ONLY_CODEX_PROMPT.md)"
