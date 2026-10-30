#!/usr/bin/env bash
# Install NCS toolchain bundle matching the checked-out sdk-nrf revision.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NRF="${ROOT}/ncs/nrf"
ENV_SCRIPT="${ROOT}/.ncs-toolchain-env.sh"

if [[ ! -d "${NRF}" ]]; then
  echo "Run scripts/west-bootstrap.sh first (missing ${NRF})" >&2
  exit 1
fi

if ! command -v nrfutil >/dev/null 2>&1; then
  echo "Installing nrfutil..."
  tmp="$(mktemp)"
  curl -fsSL \
    "https://files.nordicsemi.com/artifactory/swtools/external/nrfutil/executables/x86_64-unknown-linux-gnu/nrfutil" \
    -o "${tmp}"
  sudo install -m 0755 "${tmp}" /usr/local/bin/nrfutil
  rm -f "${tmp}"
fi

nrfutil install toolchain-manager || true

TOOLCHAIN_ID="$("${NRF}/scripts/print_toolchain_checksum.sh")"
echo "Toolchain bundle id for this sdk-nrf tree: ${TOOLCHAIN_ID}"

if ! nrfutil toolchain-manager install --toolchain-bundle-id "${TOOLCHAIN_ID}"; then
  echo "toolchain-manager install failed; retrying with search index refresh..." >&2
  nrfutil toolchain-manager search >/dev/null || true
  nrfutil toolchain-manager install --toolchain-bundle-id "${TOOLCHAIN_ID}"
fi

nrfutil toolchain-manager env --as-script > "${ENV_SCRIPT}"
# Safe to source under `set -u` (CI uses nounset; LD_LIBRARY_PATH may be unset).
sed -i 's/\$LD_LIBRARY_PATH/${LD_LIBRARY_PATH:-}/g' "${ENV_SCRIPT}"
echo "Wrote ${ENV_SCRIPT}"
