#!/usr/bin/env python3
"""Parse tests/build-matrix.yaml and drive west builds."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = REPO_ROOT / "tests" / "build-matrix.yaml"
NCS_DIR = REPO_ROOT / "ncs"
NRF_DIR = NCS_DIR / "nrf"
ARTIFACTS_DIR = REPO_ROOT / "artifacts"


def load_matrix(path: Path = MATRIX_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def git_sha(repo: Path) -> str | None:
    if not (repo / ".git").exists():
        return None
    out = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        text=True,
    )
    return out.strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", s).strip("-") or "file"


def collect_hex_files(build_dir: Path, globs: list[str]) -> list[Path]:
    if not build_dir.is_dir():
        return []
    found: list[Path] = []
    for path in build_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(build_dir).as_posix()
        for pattern in globs:
            if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(path.name, pattern):
                found.append(path)
                break
    # Prefer merged / application hex when multiple matches exist.
    found.sort(key=lambda p: (0 if "merged" in p.name.lower() else 1, len(p.parts), p.as_posix()))
    return found


def build_target(target: dict[str, Any], env: dict[str, str]) -> dict[str, Any]:
    tid = target["id"]
    board = target["board"]
    sample = target["sample"]
    sysbuild = target.get("sysbuild", True)
    pristine = target.get("pristine", True)
    extra = target.get("extra_west_args") or []
    hex_globs = target.get("hex_globs") or ["**/zephyr.hex"]

    build_dir = NCS_DIR / "build" / slug(tid)
    if build_dir.exists() and pristine:
        import shutil

        shutil.rmtree(build_dir)

    cmd = ["west", "build"]
    if pristine:
        cmd.append("-p")
    cmd.extend(["-d", str(build_dir), "-b", board])
    if sysbuild:
        cmd.append("--sysbuild")
    cmd.extend(extra)
    cmd.append(sample)

    run(cmd, cwd=NRF_DIR, env=env)

    hex_paths = collect_hex_files(build_dir, hex_globs)
    if not hex_paths:
        raise RuntimeError(f"No hex files matched {hex_globs!r} under {build_dir}")

    out_dir = ARTIFACTS_DIR / slug(tid)
    out_dir.mkdir(parents=True, exist_ok=True)
    copied: list[dict[str, Any]] = []
    for idx, src in enumerate(hex_paths):
        name = src.name if len(hex_paths) == 1 else f"{idx:02d}-{src.name}"
        dest = out_dir / name
        dest.write_bytes(src.read_bytes())
        copied.append(
            {
                "name": name,
                "path": str(dest.relative_to(REPO_ROOT)),
                "sha256": sha256_file(dest),
                "size_bytes": dest.stat().st_size,
                "source_build_path": str(src.relative_to(REPO_ROOT)),
            }
        )

    return {
        "id": tid,
        "board": board,
        "sample": sample,
        "status": "ok",
        "build_dir": str(build_dir.relative_to(REPO_ROOT)),
        "hex_files": copied,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build all targets in tests/build-matrix.yaml")
    parser.add_argument(
        "--matrix",
        type=Path,
        default=MATRIX_PATH,
        help="Path to build matrix YAML",
    )
    args = parser.parse_args()

    matrix = load_matrix(args.matrix)
    env = os.environ.copy()

    results: list[dict[str, Any]] = []
    failed: list[str] = []

    for target in matrix.get("targets") or []:
        tid = target.get("id", "<unknown>")
        try:
            results.append(build_target(target, env))
        except subprocess.CalledProcessError as e:
            failed.append(tid)
            results.append({"id": tid, "status": "error", "error": f"command failed: {e}"})
        except Exception as e:  # noqa: BLE001 — collect per-target failures
            failed.append(tid)
            results.append({"id": tid, "status": "error", "error": str(e)})

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_sha": git_sha(REPO_ROOT),
        "sdk_nrf_sha": git_sha(NRF_DIR),
        "sdk_nrf_revision": (matrix.get("manifest") or {}).get("revision"),
        "targets": results,
        "failed_target_ids": failed,
    }

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = ARTIFACTS_DIR / "build-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {manifest_path}", flush=True)

    if failed:
        print(f"FAILED targets: {', '.join(failed)}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
