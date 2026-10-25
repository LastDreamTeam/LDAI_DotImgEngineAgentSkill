"""Layer invariants and alpha-over behavior using synthetic pixels only."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, PngImagePlugin

SCRIPT = Path(__file__).resolve().parents[1] / "skills/ld-dotimgengine-online/scripts/rgba_layers.py"
sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location("rgba_layers", SCRIPT)
layers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layers)


class LayerFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.back = self.root / "01-back.png"
        self.front = self.root / "02-front.png"
        self.output = self.root / "preview.png"
        back = Image.new("RGBA", (8, 6), (0, 0, 0, 0))
        back.putpixel((2, 2), (255, 0, 0, 255))
        back.putpixel((5, 3), (0, 255, 0, 255))
        back.save(self.back)
        front = Image.new("RGBA", back.size, (0, 0, 0, 0))
        front.putpixel((2, 2), (0, 0, 255, 128))
        front.putpixel((4, 1), (240, 240, 240, 64))
        front.save(self.front)

    def test_soft_alpha_and_full_canvas_composite_round_trip(self):
        source_bytes = [p.read_bytes() for p in (self.back, self.front)]
        report = layers.check_layers([self.back, self.front], (8, 6), self.output)
        self.assertEqual(report["layers"][1]["alpha_max"], 128)
        self.assertEqual(report["layers"][1]["soft_alpha_pixels"], 2)
        with Image.open(self.output) as preview:
            self.assertEqual(preview.size, (8, 6))
            self.assertEqual(preview.getpixel((2, 2)), (127, 0, 128, 255))
            self.assertEqual(preview.getpixel((5, 3)), (0, 255, 0, 255))
            self.assertEqual(preview.getpixel((4, 1)), (240, 240, 240, 64))
            self.assertEqual(preview.getpixel((0, 0)), (0, 0, 0, 0))
        self.assertEqual(source_bytes, [p.read_bytes() for p in (self.back, self.front)])

    def test_reversed_order_changes_overlap(self):
        layers.check_layers([self.front, self.back], (8, 6), self.output)
        with Image.open(self.output) as preview:
            self.assertEqual(preview.getpixel((2, 2)), (255, 0, 0, 255))

    def test_rejects_empty_opaque_rgb_and_wrong_canvas(self):
        invalid = self.root / "invalid.png"
        for mode, color, size in [("RGBA", (0, 0, 0, 0), (8, 6)),
                                   ("RGBA", (1, 2, 3, 255), (8, 6)),
                                   ("RGB", (1, 2, 3), (8, 6)),
                                   ("RGBA", (1, 2, 3, 128), (7, 6))]:
            with self.subTest(mode=mode, color=color, size=size):
                Image.new(mode, size, color).save(invalid)
                with self.assertRaises(ValueError):
                    layers.check_layers([self.back, invalid], (8, 6), self.output)
                self.assertFalse(self.output.exists())

    def test_rejects_duplicates_missing_layers_and_bad_size(self):
        for paths, size in [([], (8, 6)), ([self.back, self.back], (8, 6)),
                            ([self.back], (0, 6)), ([self.back], (8, 5))]:
            with self.subTest(paths=paths, size=size):
                with self.assertRaises(ValueError):
                    layers.check_layers(paths, size)

    def test_existing_output_and_input_are_not_overwritten(self):
        self.output.write_bytes(b"keep-existing")
        for output in [self.output, self.back]:
            previous = output.read_bytes()
            with self.assertRaises(FileExistsError):
                layers.check_layers([self.back, self.front], (8, 6), output)
            self.assertEqual(output.read_bytes(), previous)

    def test_mismatched_color_context_rejected(self):
        with Image.open(self.front) as image:
            tagged = image.copy()
        chunks = PngImagePlugin.PngInfo()
        chunks.add(b"sRGB", bytes([0]))
        tagged.save(self.front, pnginfo=chunks)
        with self.assertRaises(ValueError):
            layers.check_layers([self.back, self.front], (8, 6), self.output)
        self.assertFalse(self.output.exists())

    def test_cli_read_only_and_composite(self):
        for extra in [[], ["--output", str(self.output)]]:
            run = subprocess.run([sys.executable, "-B", str(SCRIPT), "--expect-size",
                                  "8", "6", *extra, str(self.back), str(self.front)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["layer_count"], 2)
            if not extra:
                self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
