import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from encryptor import embed_text, extract_text


class SteganographyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.cover = self.root / 'cover.png'
        self.output = self.root / 'encoded.png'
        Image.new('RGB', (20, 20), (120, 160, 200)).save(self.cover)

    def tearDown(self):
        self.temp.cleanup()

    def test_unicode_and_null(self):
        message = 'مرحبا Haneen 🌷\0tail'
        embed_text(message, self.cover, self.output)
        self.assertEqual(extract_text(self.output), message)

    def test_empty_and_exact_capacity(self):
        for index, message in enumerate(('', 'x' * 138)):
            output = self.root / f'{index}.png'
            embed_text(message, self.cover, output)
            self.assertEqual(extract_text(output), message)
        with self.assertRaises(ValueError):
            embed_text('x' * 139, self.cover, self.output)

    def test_small_image(self):
        Image.new('RGB', (1, 1)).save(self.cover)
        with self.assertRaises(ValueError):
            embed_text('', self.cover, self.output)
        with self.assertRaises(ValueError):
            extract_text(self.cover)

    def test_alpha_preserved(self):
        Image.new('RGBA', (20, 20), (120, 160, 200, 71)).save(self.cover)
        embed_text('example', self.cover, self.output)
        with Image.open(self.output) as image:
            self.assertEqual(image.mode, 'RGBA')
            self.assertEqual(set(image.getchannel('A').tobytes()), {71})
        self.assertEqual(extract_text(self.output), 'example')

    def test_no_payload(self):
        with self.assertRaisesRegex(ValueError, 'No supported'):
            extract_text(self.cover)

    def test_corruption(self):
        embed_text('example', self.cover, self.output)
        with Image.open(self.output) as image:
            # Header occupies 96 channel bits; flip the first payload bit.
            pixels = image.load()
            x, y = 32 % image.width, 32 // image.width
            r, g, b = pixels[x, y]
            pixels[x, y] = (r ^ 1, g, b)
            image.save(self.output)
        with self.assertRaisesRegex(ValueError, 'checksum'):
            extract_text(self.output)

    def test_output_protection_and_png(self):
        with self.assertRaises(ValueError):
            embed_text('example', self.cover, self.cover)
        with self.assertRaises(ValueError):
            embed_text('example', self.cover, self.root / 'encoded.jpg')
        embed_text('example', self.cover, self.output)
        with self.assertRaises(ValueError):
            embed_text('example', self.cover, self.output)

    def test_import_has_no_io(self):
        result = subprocess.run([sys.executable, '-c', 'import encryptor'], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
