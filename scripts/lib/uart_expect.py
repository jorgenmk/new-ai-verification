#!/usr/bin/env python3
"""Read a serial port until a regex matches or timeout."""

from __future__ import annotations

import argparse
import re
import sys
import time

import serial


def main() -> int:
    parser = argparse.ArgumentParser(description="Wait for UART pattern")
    parser.add_argument("--device", required=True, help="Serial device path")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--pattern", required=True, help="Regex to match in output")
    parser.add_argument("--timeout", type=float, default=60.0, help="Seconds")
    args = parser.parse_args()

    pattern = re.compile(args.pattern)
    deadline = time.monotonic() + args.timeout
    captured = bytearray()

    with serial.Serial(args.device, args.baud, timeout=0.25) as ser:
        while time.monotonic() < deadline:
            chunk = ser.read(4096)
            if chunk:
                captured.extend(chunk)
                sys.stdout.buffer.write(chunk)
                sys.stdout.buffer.flush()
                text = captured.decode("utf-8", errors="replace")
                if pattern.search(text):
                    return 0

    print(
        f"\nuart_expect: pattern {args.pattern!r} not seen within {args.timeout}s",
        file=sys.stderr,
    )
    if captured:
        print("--- captured (last 4 KiB) ---", file=sys.stderr)
        tail = captured[-4096:].decode("utf-8", errors="replace")
        print(tail, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
