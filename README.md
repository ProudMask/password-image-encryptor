# LSB Image Text Hiding

An educational steganography example: embed UTF-8 text in the least significant bits of RGB channels, then extract it from a lossless PNG. The repository keeps its historical name, but this is **text hiding, not encryption**. Anyone with the image and format knowledge can recover the text; do not use this as a password vault.

## Run a reproducible example

Python 3.10 or later:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python encryptor.py demo --output outputs/cover.png
python -c "from pathlib import Path; Path('outputs/message.txt').write_text('Hello Haneen — مرحبا', encoding='utf-8')"
python encryptor.py embed --input outputs/cover.png --text-file outputs/message.txt --output outputs/encoded.png
python encryptor.py extract --input outputs/encoded.png --output outputs/recovered.txt
python -m unittest discover -s tests -v
```

New output paths are required; existing files are not overwritten. The demonstration image is generated locally, and the message is synthetic. Extraction writes to a text file instead of printing its contents.

## Python API

```python
from encryptor import embed_text, extract_text

embed_text('Example text', 'cover.png', 'encoded.png')
assert extract_text('encoded.png') == 'Example text'
```

The legacy function names `encrypt_password_to_image` and `decrypt_password_from_image` remain as wrappers for callers. They do not perform cryptographic encryption. Importing the module does not read or write files.

## Format and validation

The versioned packet contains a four-byte `LSB1` marker, a four-byte unsigned UTF-8 payload length, a four-byte CRC32, and the payload. Fields use big-endian byte order. Bits are embedded most-significant first in row-major RGB channel order. Alpha is not modified. RGB/RGBA images are supported; other Pillow modes are normalized to RGB or RGBA, preserving alpha where available.

Capacity in UTF-8 bytes is `floor(width * height * 3 / 8) - 12`, with at least 12 bytes required for the header. A 100×100 image has room for 3738 payload bytes. Arabic, emoji, embedded nulls, and empty text are handled using explicit byte lengths rather than a null terminator. Oversized messages, unsupported headers, impossible lengths, and checksum mismatches fail explicitly.

CRC32 detects accidental corruption; it does not authenticate a message. Recompression, resizing, filtering, or conversion to JPEG can destroy the payload. Output/extraction use PNG. Source metadata, animation frames, and color profiles are not preserved. The new packet format is not compatible with images produced by the old unframed prototype.

## Verification and scope

Tests cover Unicode/null round trips, exact capacity boundaries, too-small images, alpha preservation, missing payloads, corruption detection, output protection, and import behavior. These are functional checks, not claims of secrecy or resistance to steganalysis. This is a deterministic image-processing example, not an ML model.
