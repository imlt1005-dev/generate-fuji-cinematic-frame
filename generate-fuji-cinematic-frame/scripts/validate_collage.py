#!/usr/bin/env python3
"""Validate basic technical properties of a cinematic collage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit("This script requires Pillow: python -m pip install pillow") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("--expected-aspect", type=float, default=9 / 16)
    parser.add_argument("--tolerance", type=float, default=0.01)
    parser.add_argument("--min-width", type=int, default=1080)
    parser.add_argument("--min-height", type=int, default=1920)
    args = parser.parse_args()

    path = Path(args.image)
    problems: list[str] = []
    if not path.exists():
        raise SystemExit(f"File not found: {path}")
    with Image.open(path) as image:
        width, height = image.size
        mode = image.mode
    aspect = width / height
    if abs(aspect - args.expected_aspect) > args.tolerance:
        problems.append(f"aspect {aspect:.4f} differs from expected {args.expected_aspect:.4f}")
    if width < args.min_width or height < args.min_height:
        problems.append(f"dimensions {width}x{height} are below {args.min_width}x{args.min_height}")
    if mode not in ("RGB", "RGBA"):
        problems.append(f"unexpected image mode: {mode}")

    result = {
        "file": str(path.resolve()),
        "size": [width, height],
        "aspect": round(aspect, 6),
        "mode": mode,
        "passed": not problems,
        "problems": problems,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not problems else 1)


if __name__ == "__main__":
    main()
