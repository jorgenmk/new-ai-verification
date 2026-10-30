#!/usr/bin/env python3
"""Load a single target from tests/build-matrix.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MATRIX = REPO_ROOT / "tests" / "build-matrix.yaml"


def load_matrix(path: Path = DEFAULT_MATRIX) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_target(target_id: str, path: Path = DEFAULT_MATRIX) -> dict[str, Any]:
    matrix = load_matrix(path)
    for target in matrix.get("targets") or []:
        if target.get("id") == target_id:
            return target
    raise KeyError(f"Unknown target id {target_id!r} in {path}")
