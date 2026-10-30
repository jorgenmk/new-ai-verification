#!/usr/bin/env python3
"""Flash hex and run UART expectations for one build-matrix target."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from matrix_target import get_target  # noqa: E402


def resolve_hex(root: Path, target_id: str, hex_arg: Path | None) -> Path:
    if hex_arg is not None:
        return hex_arg
    manifest = root / "artifacts" / "build-manifest.json"
    if manifest.is_file():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for t in data.get("targets", []):
            if t.get("id") == target_id and t.get("hex_files"):
                return root / t["hex_files"][0]["path"]
    return root / "artifacts" / target_id / "zephyr.hex"


def pick_serial(device_cfg: str, override: str | None) -> str:
    import glob

    if override:
        return override
    if device_cfg != "auto":
        return device_cfg
    for pattern in ("/dev/ttyACM*", "/dev/ttyUSB*"):
        for path in sorted(glob.glob(pattern)):
            if Path(path).exists():
                return path
    return ""


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Flash and UART-verify a matrix target")
    parser.add_argument("--target", required=True, help="Target id")
    parser.add_argument("--hex", type=Path, default=None)
    parser.add_argument("--serial", default=None, help="UART device path")
    parser.add_argument("--matrix", type=Path, default=REPO_ROOT / "tests" / "build-matrix.yaml")
    parser.add_argument("--build-if-missing", action="store_true")
    args = parser.parse_args()

    root = REPO_ROOT
    target = get_target(args.target, args.matrix)
    verify = target.get("verify")
    if not verify:
        print(f"Target {args.target!r} has no verify: block", file=sys.stderr)
        return 2

    hex_path = resolve_hex(root, args.target, args.hex)
    if not hex_path.is_file():
        if args.build_if_missing:
            run(["bash", str(root / "scripts" / "build-matrix.sh")])
        if not hex_path.is_file():
            print(f"Hex not found: {hex_path}", file=sys.stderr)
            return 1

    print(f"Using firmware: {hex_path}", flush=True)

    flash = verify.get("flash") or {}
    tool = flash.get("tool", "nrfutil")
    if tool == "nrfutil":
        run(["nrfutil", "device", "program", "--firmware", str(hex_path), "--verify"])
        run(["nrfutil", "device", "reset"])
    else:
        print(f"Unsupported flash tool: {tool}", file=sys.stderr)
        return 2

    serial_cfg = verify.get("serial") or {}
    baud = int(serial_cfg.get("baud", 115200))
    device = pick_serial(str(serial_cfg.get("device", "auto")), args.serial)
    if not device:
        print("Serial device not found; use --serial or NCS_SERIAL_DEVICE", file=sys.stderr)
        return 1

    print(f"UART: {device} @ {baud}", flush=True)

    expect = verify.get("expect") or []
    if not expect:
        print("No expect: patterns configured", file=sys.stderr)
        return 2

    uart_script = root / "scripts" / "lib" / "uart_expect.py"
    for item in expect:
        run(
            [
                sys.executable,
                str(uart_script),
                "--device",
                device,
                "--baud",
                str(baud),
                "--pattern",
                item["pattern"],
                "--timeout",
                str(float(item.get("timeout_s", 60))),
            ]
        )

    print("flash-and-verify: all UART expectations matched", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
