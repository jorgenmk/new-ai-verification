# Agent instructions — new-ai-verification

## Phase 1 (current): cloud builds only

Build Nordic Connect SDK samples from **`sdk-nrf` `main`** using the declarative matrix in [`tests/build-matrix.yaml`](tests/build-matrix.yaml).

| Runtime | Role |
|---------|------|
| **Cursor Cloud Agent** | `west init` / `west update`, compile matrix targets, write hex files under `artifacts/` and `artifacts/build-manifest.json` |
| **Self-hosted worker** | Not used in phase 1 |

### Adding a board or sample

Append a row under `targets:` in `tests/build-matrix.yaml`:

- **`id`**: stable artifact folder name (e.g. `nrf9160dk-net-download`)
- **`board`**: west board (e.g. `nrf9151dk/nrf9151/ns`)
- **`sample`**: path under `ncs/nrf` (e.g. `samples/net/download`)
- **`hex_globs`**: patterns to collect firmware after build (sysbuild layouts vary)
- **`verify`**: leave `null` until phase 2 (flash + UART/network checks)

Then run `bash scripts/build-matrix.sh` (after toolchain and `west update`).

### Cloud environment

[`.cursor/environment.json`](.cursor/environment.json) runs [`scripts/install-cloud.sh`](scripts/install-cloud.sh) during environment **Build**: bootstrap workspace, install toolchain bundle matching the manifest checkout, `west update`, build matrix.

### Nightly CI

GitHub Actions workflow [`.github/workflows/nightly-build.yml`](.github/workflows/nightly-build.yml) resolves the official `ghcr.io/nrfconnect/sdk-nrf-toolchain` tag from current `sdk-nrf` main, then runs the same matrix build.

## Phase 2 (later): flash and test on hardware

Target the Linux bench worker (e.g. `worker=jokv-linux.nordicsemi.no`) and implement [`scripts/flash-and-verify.sh`](scripts/flash-and-verify.sh) using `verify:` blocks in the matrix.

` samples/net/download` needs network/SIM at runtime — define expectations in `verify:` when enabling phase 2.
