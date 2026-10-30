# new-ai-verification

Nightly-style verification for **nRF Connect SDK** sample builds, with a path toward on-device flash and UART checks on a self-hosted worker.

## Phase 1 — build matrix (implemented)

1. West workspace under [`ncs/`](ncs/) tracks [`nrfconnect/sdk-nrf`](https://github.com/nrfconnect/sdk-nrf) **`main`**.
2. [`tests/build-matrix.yaml`](tests/build-matrix.yaml) lists boards and samples to build.
3. [`scripts/build-matrix.sh`](scripts/build-matrix.sh) builds each target and copies `.hex` files to [`artifacts/<id>/`](artifacts/).
4. [`artifacts/build-manifest.json`](artifacts/build-manifest.json) records repo SHAs, per-target status, and checksums.

**First target:** `nrf9151dk/nrf9151/ns` + `samples/net/download`.

### Local / agent commands

```bash
bash scripts/west-bootstrap.sh
bash scripts/setup-toolchain.sh
source .ncs-toolchain-env.sh
bash scripts/west-update.sh
bash scripts/build-matrix.sh
```

Cloud agents use [`.cursor/environment.json`](.cursor/environment.json) (`scripts/install-cloud.sh`) instead.

### Nightly GitHub Actions

[`.github/workflows/nightly-build.yml`](.github/workflows/nightly-build.yml) runs on a schedule and `workflow_dispatch` on GitHub-hosted runners (toolchain via `nrfutil`, same steps as local), and uploads hex artifacts from the matrix.

## Phase 2 — flash and verify (planned)

[`scripts/flash-and-verify.sh`](scripts/flash-and-verify.sh) will program firmware on an **nRF9151 DK** via a self-hosted Cursor worker and assert serial/network output defined under `verify:` in the matrix.

See [`AGENTS.md`](AGENTS.md) for agent-facing workflow notes.
