#!/usr/bin/env bash
# Cloud Agent / environment Build entrypoint (phase 1).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

export PATH="${HOME}/.local/bin:${PATH}"

bash scripts/west-bootstrap.sh
bash scripts/setup-toolchain.sh
# shellcheck source=/dev/null
source "${ROOT}/.ncs-toolchain-env.sh"
bash scripts/west-update.sh
bash scripts/build-matrix.sh
