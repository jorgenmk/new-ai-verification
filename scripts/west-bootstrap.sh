#!/usr/bin/env bash
# Idempotent west workspace init for sdk-nrf main (does not run west update).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NCS="${ROOT}/ncs"
MANIFEST_URL="${NCS_MANIFEST_URL:-https://github.com/nrfconnect/sdk-nrf}"
MANIFEST_REV="${NCS_MANIFEST_REVISION:-main}"

cd "${ROOT}"

if ! command -v west >/dev/null 2>&1; then
  python3 -m pip install --user -q west
  export PATH="${HOME}/.local/bin:${PATH}"
fi

if [[ ! -d "${NCS}/.west" ]]; then
  echo "Initializing west workspace at ${NCS} (${MANIFEST_REV})"
  west init -m "${MANIFEST_URL}" --mr "${MANIFEST_REV}" "${NCS}"
fi

git config --global --add safe.directory '*' || true

if [[ -d "${NCS}/nrf/.git" ]]; then
  echo "sdk-nrf manifest checkout: $(git -C "${NCS}/nrf" rev-parse HEAD)"
fi
