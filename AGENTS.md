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

GitHub Actions workflow [`.github/workflows/nightly-build.yml`](.github/workflows/nightly-build.yml) runs on `ubuntu-latest`, installs the NCS toolchain bundle via `nrfutil` (matching the checked-out `sdk-nrf` main), then runs the same matrix build as [`scripts/install-cloud.sh`](scripts/install-cloud.sh).

## Phase 2: flash and UART on hardware (self-hosted worker)

Run on a machine with the **nRF9151 DK** attached (Linux bench worker), from a clone of this repo:

```bash
# Hex from a prior cloud/CI build, or --build-if-missing on a toolchain-equipped bench
bash scripts/flash-and-verify.sh --target nrf9151dk-net-download
# Optional: --serial /dev/ttyACM1  or export NCS_SERIAL_DEVICE=...
```

Trigger a **self-hosted** Cloud Agent (Project chat / runtime picker), e.g. worker **`jokv-linux.nordicsemi.no#/home/jokv`** (`workerId` `66e3bfa7-dc18-424c-966c-22f7ec3b4acc`), with:

> Run `bash scripts/flash-and-verify.sh --target nrf9151dk-net-download` from the repo root.

Phase 2 v1 checks only the **Zephyr boot banner** on UART (`Booting Zephyr OS` in [`tests/build-matrix.yaml`](tests/build-matrix.yaml)). Network/SIM checks come later.
