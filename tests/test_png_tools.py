"""Behavior tests using only generated geometry in temporary directories."""

import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/ld-dotimgengine-online/scripts/png_tools.py"
spec = importlib.util.spec_from_file_location("png_tools", SCRIPT)
png = importlib.util.module_from_spec(spec)
spec.loader.exec_module(png)


class GeometryFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.original = self.root / "original.png"
        self.candidate = self.root / "candidate.png"
        self.mask = self.root / "protect.png"
        source = Image.new("RGBA", (32, 48), (240, 240, 240, 255))
        draw = ImageDraw.Draw(source)
        draw.ellipse((8, 4, 23, 19), fill=(20, 80, 180, 255))
        draw.rectangle((12, 20, 19, 42), fill=(90, 150, 210, 255))
        source.save(self.original)
        candidate = source.copy()
        candidate.putpixel((10, 10), (200, 0, 0, 255))
        candidate.putpixel((1, 1), (0, 0, 0, 0))
        candidate.save(self.candidate)
        mask = Image.new("L", source.size, 0)
        ImageDraw.Draw(mask).ellipse((6, 2, 25, 21), fill=255)
        mask.save(self.mask)

    def cli(self, *args):
        run = subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args)], capture_output=True, text=True)
        return run.returncode, json.loads(run.stdout)

    def test_inspect_dimensions_and_file_hash(self):
        report = png.inspect_png(self.original, (32, 48), hashlib.sha256(self.original.read_bytes()).hexdigest())
        self.assertTrue(report["passed"])
        self.assertEqual(report["mode"], "RGBA")
        self.assertEqual(report["bit_depth"], 8)
        self.assertFalse(png.inspect_png(self.original, (1, 2))["passed"])
        self.assertFalse(png.inspect_png(self.original, expected_sha256="0" * 64)["passed"])
        with self.assertRaises(ValueError):
            png.inspect_png(self.original, expected_sha256="incomplete")

    def test_mask_detects_only_protected_change(self):
        report = png.compare_png(self.original, self.candidate, self.mask)
        self.assertFalse(report["passed"])
        self.assertEqual(report["changed_pixels"], 1)
        self.assertGreater(report["selected_pixels"], 0)
        self.assertLess(report["selected_pixels"], 32 * 48)
        self.assertEqual(png.compare_png(self.original, self.candidate)["changed_pixels"], 2)

    def test_composite_preserves_source_and_unprotected_candidate(self):
        before = {p: png.sha256(p) for p in (self.original, self.candidate, self.mask)}
        output = self.root / "composite.png"
        report = png.composite_png(self.original, self.candidate, self.mask, output)
        self.assertTrue(report["passed"])
        self.assertEqual(report["changed_pixels"], 0)
        with Image.open(output) as image:
            self.assertEqual(image.getpixel((10, 10)), (20, 80, 180, 255))
            self.assertEqual(image.getpixel((1, 1)), (0, 0, 0, 0))
        self.assertEqual(before, {p: png.sha256(p) for p in before})

    def test_existing_output_and_source_cannot_be_overwritten(self):
        for target in (self.original, self.candidate, self.mask):
            before = target.read_bytes()
            with self.assertRaises(FileExistsError):
                png.composite_png(self.original, self.candidate, self.mask, target)
            self.assertEqual(target.read_bytes(), before)

    def test_mismatched_native_size_rejected(self):
        other = self.root / "other.png"
        Image.new("RGB", (16, 24)).save(other)
        with self.assertRaisesRegex(ValueError, "Native dimensions"):
            png.compare_png(self.original, other, self.mask)
        Image.new("L", (16, 24), 255).save(other)
        with self.assertRaisesRegex(ValueError, "Mask dimensions"):
            png.compare_png(self.original, self.candidate, other)

    def test_empty_gray_and_wrong_mode_masks_rejected(self):
        cases = [("L", 0, "empty"), ("L", 128, "binary"), ("RGB", (255, 255, 255), "L-mode")]
        for mode, value, error in cases:
            with self.subTest(mode=mode, value=value):
                bad = self.root / "bad-mask.png"
                Image.new(mode, (32, 48), value).save(bad)
                with self.assertRaisesRegex(ValueError, error):
                    png.compare_png(self.original, self.candidate, bad)

    def test_palette_and_high_bit_depth_not_silently_converted(self):
        for mode in ("P", "I;16"):
            with self.subTest(mode=mode):
                path = self.root / "precision.png"
                Image.new(mode, (32, 48)).save(path)
                self.assertTrue(png.inspect_png(path)["passed"])
                with self.assertRaisesRegex(ValueError, "8-bit RGB or RGBA"):
                    png.compare_png(path, path)

    def test_alpha_and_invisible_rgb_changes_are_detected(self):
        a, b = self.root / "a.png", self.root / "b.png"
        Image.new("RGBA", (2, 1), (10, 20, 30, 0)).save(a)
        im = Image.new("RGBA", (2, 1), (11, 20, 30, 0))
        im.putpixel((1, 0), (10, 20, 30, 1))
        im.save(b)
        self.assertEqual(png.compare_png(a, b)["changed_pixels"], 2)
        self.assertFalse(png.compare_png(a, b)["passed"])
        loose = png.compare_png(a, b, tolerance=1)
        self.assertTrue(loose["passed"])
        self.assertFalse(loose["exact_pixels_equal"])
        with self.assertRaises(ValueError):
            png.compare_png(a, b, tolerance=256)

    def test_reencoding_hash_differs_but_pixels_match(self):
        other = self.root / "metadata.png"
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("SyntheticFixture", "metadata only")
        with Image.open(self.original) as im:
            im.save(other, pnginfo=metadata)
        self.assertNotEqual(png.sha256(self.original), png.sha256(other))
        self.assertTrue(png.compare_png(self.original, other)["exact_pixels_equal"])

    def test_color_context_mismatch_rejected_and_preserved(self):
        first, second = self.root / "gamma-a.png", self.root / "gamma-b.png"
        for path, value in ((first, 45455), (second, 100000)):
            info = PngImagePlugin.PngInfo()
            info.add(b"gAMA", struct.pack(">I", value))
            with Image.open(self.original) as im:
                im.save(path, pnginfo=info)
        report = png.compare_png(first, second)
        self.assertTrue(report["exact_pixels_equal"])
        self.assertFalse(report["passed"])
        with self.assertRaisesRegex(ValueError, "Color contexts"):
            png.composite_png(first, second, self.mask, self.root / "rejected.png")
        result = self.root / "gamma-output.png"
        self.assertTrue(png.composite_png(first, first, self.mask, result)["passed"])
        self.assertEqual(png.inspect_png(first)["color_context"], png.inspect_png(result)["color_context"])

    def test_corrupt_non_png_and_animated_input_rejected(self):
        corrupt = self.root / "corrupt.png"
        corrupt.write_bytes(self.original.read_bytes()[:40])
        with self.assertRaises((OSError, SyntaxError)):
            png.inspect_png(corrupt)
        impostor = self.root / "impostor.png"
        Image.new("RGB", (2, 2)).save(impostor, format="JPEG")
        with self.assertRaisesRegex(ValueError, "real PNG"):
            png.inspect_png(impostor)
        animated = self.root / "animated.png"
        Image.new("RGBA", (2, 2), "red").save(animated, save_all=True, append_images=[Image.new("RGBA", (2, 2), "blue")], duration=100)
        with self.assertRaisesRegex(ValueError, "Animated"):
            png.inspect_png(animated)

    def test_cli_exit_codes_are_meaningful(self):
        code, report = self.cli("inspect", self.original)
        self.assertEqual(code, 0)
        self.assertTrue(report["passed"])
        code, report = self.cli("compare", self.original, self.candidate, "--mask", self.mask)
        self.assertEqual(code, 2)
        self.assertFalse(report["passed"])
        code, report = self.cli("inspect", self.root / "missing.png")
        self.assertEqual(code, 2)
        self.assertFalse(report["passed"])


if __name__ == "__main__":
    unittest.main()
