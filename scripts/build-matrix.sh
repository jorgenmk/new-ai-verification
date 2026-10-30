#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

python3 -m pip install --user -q -r scripts/requirements.txt

if [[ -f "${ROOT}/.ncs-toolchain-env.sh" ]]; then
  # shellcheck source=/dev/null
  source "${ROOT}/scripts/source-ncs-toolchain-env.sh"
  __source_ncs_toolchain_env "${ROOT}"
elif [[ -z "${ZEPHYR_BASE:-}" ]]; then
  echo "Missing toolchain env: run scripts/setup-toolchain.sh or use ghcr.io/nrfconnect/sdk-nrf-toolchain" >&2
  exit 1
fi

export PYTHONPATH="${ROOT}/scripts/lib:${PYTHONPATH:-}"
exec python3 "${ROOT}/scripts/lib/build_matrix.py" "$@"
