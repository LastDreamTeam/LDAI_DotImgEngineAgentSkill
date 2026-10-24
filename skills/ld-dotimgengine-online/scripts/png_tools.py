#!/usr/bin/env python3
"""Inspect PNGs, compare native aligned pixels, and copy protected source pixels.

Requires an existing Pillow installation. No network calls or image generation.
White (255) in a binary L mask protects the source; black (0) uses the candidate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import warnings

try:
    from PIL import Image, ImageChops, PngImagePlugin
except ImportError:
    print(json.dumps({"error": "Pillow is required; no dependency was installed."}))
    raise SystemExit(3)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_png(path: Path):
    path = Path(path)
    with path.open("rb") as stream:
        header = stream.read(33)
    if len(header) != 33 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("Input must be a real PNG with an IHDR header")
    bit_depth, color_type = header[24], header[25]
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(path) as check:
            if check.format != "PNG":
                raise ValueError("Input is not PNG")
            check.verify()
        with Image.open(path) as source:
            source.load()
            if getattr(source, "n_frames", 1) != 1:
                raise ValueError("Animated PNG is not supported; use independent still PNGs")
            pixels = source.copy()
            info = source.info.copy()
    return pixels, info, bit_depth, color_type


def color_context(info: dict) -> dict:
    icc = info.get("icc_profile")
    return {
        "icc_sha256": hashlib.sha256(icc).hexdigest() if icc else None,
        "gamma": info.get("gamma"),
        "srgb_intent": info.get("srgb"),
        "chromaticity": info.get("chromaticity"),
    }


def inspect_png(path: Path, expected_size=None, expected_sha256=None) -> dict:
    pixels, info, depth, color_type = read_png(path)
    digest = sha256(path)
    problems = []
    if expected_size is not None and tuple(expected_size) != pixels.size:
        problems.append("Dimensions differ from expected_size")
    if expected_sha256 is not None:
        if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256):
            raise ValueError("Expected SHA-256 must contain 64 hexadecimal characters")
        if digest != expected_sha256.lower():
            problems.append("File SHA-256 differs from expected_sha256")
    return {
        "format": "PNG", "size": list(pixels.size), "mode": pixels.mode,
        "bit_depth": depth, "color_type": color_type,
        "has_alpha_or_transparency": "A" in pixels.getbands() or "transparency" in info,
        "sha256": digest, "color_context": color_context(info),
        "passed": not problems, "problems": problems,
    }


def read_color(path: Path):
    pixels, info, depth, _ = read_png(path)
    if pixels.mode not in {"RGB", "RGBA"} or depth != 8:
        raise ValueError("Comparison/compositing requires 8-bit RGB or RGBA PNG; no implicit precision conversion")
    return pixels.convert("RGBA"), info


def read_mask(path: Path, size):
    mask, _, depth, _ = read_png(path)
    if mask.mode != "L" or depth != 8:
        raise ValueError("Mask must be an 8-bit L-mode PNG")
    if mask.size != size:
        raise ValueError("Mask dimensions must match the native image canvas")
    histogram = mask.histogram()
    if any(histogram[1:255]):
        raise ValueError("Mask must be binary: 0 or 255 only")
    if histogram[255] == 0:
        raise ValueError("Protection mask is empty; cannot validate zero pixels")
    return mask


def read_pair(original: Path, candidate: Path):
    source, source_info = read_color(original)
    edited, edited_info = read_color(candidate)
    if source.size != edited.size:
        raise ValueError("Native dimensions differ; no automatic crop, alignment, or resampling")
    return source, source_info, edited, edited_info


def compare_png(original: Path, candidate: Path, mask_path=None, tolerance=0) -> dict:
    if not isinstance(tolerance, int) or not 0 <= tolerance <= 255:
        raise ValueError("Tolerance must be an integer from 0 to 255")
    source, source_info, edited, edited_info = read_pair(original, candidate)
    mask = read_mask(mask_path, source.size) if mask_path is not None else None
    bands = ImageChops.difference(source, edited).split()
    peak_image = ImageChops.lighter(ImageChops.lighter(bands[0], bands[1]), ImageChops.lighter(bands[2], bands[3]))
    histogram = peak_image.histogram(mask=mask)
    count = sum(histogram)
    changed = sum(histogram[1:])
    violating = sum(histogram[tolerance + 1:])
    maximum = max(index for index, frequency in enumerate(histogram) if frequency)
    total = sum(index * frequency for band in bands for index, frequency in enumerate(band.histogram(mask=mask)))
    equal_context = color_context(source_info) == color_context(edited_info)
    return {
        "size": list(source.size), "comparison_space": "decoded_8bit_RGBA_no_color_conversion",
        "selected_pixels": count, "changed_pixels": changed,
        "violating_pixels": violating, "max_channel_difference": maximum,
        "mean_absolute_channel_difference": total / (count * 4),
        "tolerance": tolerance, "color_context_equal": equal_context,
        "exact_pixels_equal": changed == 0,
        "passed": violating == 0 and equal_context,
        "original_sha256": sha256(original), "candidate_sha256": sha256(candidate),
    }


def png_metadata(info: dict) -> dict:
    chunks = PngImagePlugin.PngInfo()
    if "gamma" in info:
        chunks.add(b"gAMA", struct.pack(">I", round(info["gamma"] * 100000)))
    if "srgb" in info:
        chunks.add(b"sRGB", bytes([info["srgb"]]))
    if "chromaticity" in info:
        chunks.add(b"cHRM", struct.pack(">8I", *(round(v * 100000) for v in info["chromaticity"])))
    settings = {"pnginfo": chunks}
    if info.get("icc_profile"):
        settings["icc_profile"] = info["icc_profile"]
    return settings


def composite_png(original: Path, candidate: Path, mask_path: Path, output: Path) -> dict:
    output = Path(output)
    if output.suffix.lower() != ".png":
        raise ValueError("Output must have a .png suffix")
    source, source_info, edited, edited_info = read_pair(original, candidate)
    if color_context(source_info) != color_context(edited_info):
        raise ValueError("Color contexts differ; explicitly convert copies before compositing")
    mask = read_mask(mask_path, source.size)
    result = Image.composite(source, edited, mask)
    created = False
    try:
        # Exclusive creation also rejects source paths, aliases and existing outputs.
        with output.open("xb") as stream:
            created = True
            result.save(stream, format="PNG", **png_metadata(source_info))
        report = compare_png(original, output, mask_path)
        if not report["passed"]:
            raise ValueError("Saved composite failed protected-pixel verification")
    except Exception:
        if created:
            output.unlink(missing_ok=True)
        raise
    report["operation"] = "binary_original_pixel_composite"
    report["output_sha256"] = sha256(output)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="Decode PNG and report dimensions/hash")
    inspect.add_argument("image", type=Path)
    inspect.add_argument("--expect-size", nargs=2, type=int, metavar=("WIDTH", "HEIGHT"))
    inspect.add_argument("--expect-sha256")
    compare = commands.add_parser("compare", help="Compare aligned native RGBA pixels")
    compare.add_argument("original", type=Path)
    compare.add_argument("candidate", type=Path)
    compare.add_argument("--mask", type=Path)
    compare.add_argument("--tolerance", type=int, default=0)
    composite = commands.add_parser("composite", help="Copy white-mask source pixels to a new PNG")
    for name in ("original", "candidate", "mask", "output"):
        composite.add_argument(name, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            report = inspect_png(args.image, args.expect_size, args.expect_sha256)
        elif args.command == "compare":
            report = compare_png(args.original, args.candidate, args.mask, args.tolerance)
        else:
            report = composite_png(args.original, args.candidate, args.mask, args.output)
        print(json.dumps(report, ensure_ascii=True, sort_keys=True))
        return 0 if report["passed"] else 2
    except (OSError, ValueError, SyntaxError, struct.error, Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        print(json.dumps({"passed": False, "error": str(error)}, ensure_ascii=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
