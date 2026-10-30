#!/usr/bin/env bash
# Source nrfutil-generated .ncs-toolchain-env.sh under bash nounset (set -u).
# The env script references $LD_LIBRARY_PATH before it may be set.

__source_ncs_toolchain_env() {
  local root="${1:?repo root required}"
  local env_script="${root}/.ncs-toolchain-env.sh"
  if [[ ! -f "${env_script}" ]]; then
    echo "Missing ${env_script}; run scripts/setup-toolchain.sh" >&2
    return 1
  fi
  export LD_LIBRARY_PATH="${LD_LIBRARY_PATH-}"
  local nounset_was_on=0
  if [[ $- == *u* ]]; then
    nounset_was_on=1
    set +u
  fi
  # shellcheck source=/dev/null
  source "${env_script}"
  if (( nounset_was_on )); then
    set -u
  fi
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  set -euo pipefail
  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  __source_ncs_toolchain_env "${ROOT}"
fi
