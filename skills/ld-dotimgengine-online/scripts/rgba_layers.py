#!/usr/bin/env python3
"""Validate full-canvas transparent RGBA layers, optionally compose back to front.

Requires an existing Pillow installation. No generation, alignment or input edits.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import sys

from png_tools import Image, color_context, png_metadata, read_png, sha256


def check_layers(paths, expected_size, output=None):
    paths = [Path(path) for path in paths]
    if not paths:
        raise ValueError("At least one layer is required")
    size = tuple(expected_size)
    if len(size) != 2 or any(not isinstance(n, int) or n <= 0 for n in size):
        raise ValueError("Expected canvas must contain two positive integers")
    if len({path.resolve() for path in paths}) != len(paths):
        raise ValueError("Duplicate input layer")
    output = Path(output) if output is not None else None
    if output is not None and output.suffix.lower() != ".png":
        raise ValueError("Output must have a .png suffix")

    composite = Image.new("RGBA", size, (0, 0, 0, 0)) if output is not None else None
    context = None
    metadata = None
    reports = []
    for path in paths:
        pixels, info, depth, color_type = read_png(path)
        if pixels.mode != "RGBA" or depth != 8 or color_type != 6:
            raise ValueError(f"Layer requires 8-bit RGBA PNG: {path}")
        if pixels.size != size:
            raise ValueError(f"Layer dimensions differ from expected canvas: {path}")
        current_context = color_context(info)
        if context is not None and current_context != context:
            raise ValueError(f"Layer color contexts differ: {path}")
        if metadata is None:
            context, metadata = current_context, info
        histogram = pixels.getchannel("A").histogram()
        zero = histogram[0]
        nonzero = sum(histogram[1:])
        if not zero or not nonzero:
            raise ValueError(f"Layer must contain both zero and nonzero alpha: {path}")
        reports.append({
            "file": str(path), "size": list(size), "mode": "RGBA",
            "alpha_min": 0,
            "alpha_max": max(i for i, count in enumerate(histogram) if count),
            "transparent_pixels": zero, "nonzero_alpha_pixels": nonzero,
            "soft_alpha_pixels": sum(histogram[1:255]), "sha256": sha256(path),
        })
        if composite is not None:
            composite = Image.alpha_composite(composite, pixels)
    report = {"passed": True, "operation": "transparent_rgba_layers",
              "order": "back_to_front", "canvas": list(size),
              "layer_count": len(reports), "layers": reports,
              "color_context": context}
    if output is not None:
        created = False
        try:
            with output.open("xb") as stream:
                created = True
                composite.save(stream, format="PNG", **png_metadata(metadata))
            decoded, saved_info, depth, color_type = read_png(output)
            if (decoded.mode != "RGBA" or decoded.size != size or depth != 8
                    or color_type != 6 or decoded.tobytes() != composite.tobytes()
                    or color_context(saved_info) != context):
                raise ValueError("Saved composite failed round-trip verification")
        except Exception:
            if created:
                output.unlink(missing_ok=True)
            raise
        report.update(output=str(output), output_sha256=sha256(output))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect-size", required=True, nargs=2, type=int,
                        metavar=("WIDTH", "HEIGHT"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("layers", nargs="+", type=Path, help="Back to front")
    args = parser.parse_args(argv)
    try:
        report = check_layers(args.layers, args.expect_size, args.output)
        print(json.dumps(report, ensure_ascii=True, sort_keys=True))
        return 0
    except (OSError, ValueError, SyntaxError, struct.error,
            Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        print(json.dumps({"passed": False, "error": str(error)}, ensure_ascii=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
