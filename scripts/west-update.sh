#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NCS="${ROOT}/ncs"

if [[ ! -d "${NCS}/.west" ]]; then
  echo "West workspace missing; run scripts/west-bootstrap.sh first" >&2
  exit 1
fi

if ! command -v west >/dev/null 2>&1; then
  echo "west not on PATH; source .ncs-toolchain-env.sh or use NCS toolchain image" >&2
  exit 1
fi

echo "Running west update in ${NCS} (may take several minutes)..."
(
  cd "${NCS}"
  west update
)

echo "sdk-nrf HEAD after update: $(git -C "${NCS}/nrf" rev-parse HEAD)"
