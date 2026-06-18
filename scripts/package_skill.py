#!/usr/bin/env python3
"""Package expert-review-panel as a Claude .skill archive.

The release asset is a zip file with a .skill extension. Keep the archive
layout stable so users can install it directly from GitHub Releases.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = "expert-review-panel"

INCLUDE_PATHS = [
    Path("SKILL.md"),
    Path("assets"),
    Path("evals"),
    Path("references"),
    Path("scripts/check_four_piece.py"),
    Path("scripts/README.md"),
]


def iter_package_files() -> list[Path]:
    files: list[Path] = []
    for relative in INCLUDE_PATHS:
        absolute = ROOT / relative
        if not absolute.exists():
            raise FileNotFoundError(f"Missing package input: {relative}")
        if absolute.is_dir():
            files.extend(path for path in absolute.rglob("*") if path.is_file())
        else:
            files.append(absolute)
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def write_archive(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in iter_package_files():
            relative = path.relative_to(ROOT).as_posix()
            archive.write(path, f"{PACKAGE_ROOT}/{relative}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dist-dir",
        default="dist",
        help="Directory for generated .skill archives. Defaults to dist/.",
    )
    parser.add_argument(
        "--version",
        help="Optional version label such as v1.2.0. Also writes a versioned archive.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dist_dir = (ROOT / args.dist_dir).resolve()

    latest = dist_dir / "expert-review-panel.skill"
    write_archive(latest)
    outputs = [latest]

    if args.version:
        version = args.version.strip()
        if not version:
            raise ValueError("--version cannot be empty")
        versioned = dist_dir / f"expert-review-panel-{version}.skill"
        write_archive(versioned)
        outputs.append(versioned)

    for output in outputs:
        print(output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"package_skill.py: {exc}", file=sys.stderr)
        raise SystemExit(1)
