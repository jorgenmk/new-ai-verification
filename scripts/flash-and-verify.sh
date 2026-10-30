#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

python3 -m pip install --user -q -r "${ROOT}/scripts/requirements.txt"
export PATH="${HOME}/.local/bin:${PATH}"

exec python3 "${ROOT}/scripts/lib/bench_verify.py" "$@"
