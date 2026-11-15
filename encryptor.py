"""Educational LSB text hiding, not cryptographic encryption."""
import argparse
from pathlib import Path
import struct
import zlib
from PIL import Image, UnidentifiedImageError

MAGIC = b'LSB1'
HEADER = struct.Struct('>4sII')  # Format marker, UTF-8 byte count, CRC32.


def new_output(path):
    path = Path(path)
    if path.exists():
        raise ValueError('Output already exists; choose a new path')
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def embed_text(text, image_path, output_path):
    if not isinstance(text, str):
        raise ValueError('Text must be a string')
    image_path, output_path = Path(image_path), Path(output_path)
    if output_path.suffix.lower() != '.png':
        raise ValueError('Output must be a lossless .png file')
    if image_path.resolve() == output_path.resolve() or output_path.exists():
        raise ValueError('Output must be a new file, distinct from the input')
    payload = text.encode('utf-8')
    with Image.open(image_path) as source:
        mode = 'RGBA' if source.mode in {'RGBA', 'LA'} or 'transparency' in source.info else 'RGB'
        image = source.convert(mode)
    capacity = image.width * image.height * 3 // 8
    if len(payload) + HEADER.size > capacity:
        raise ValueError(f'Text exceeds image capacity: {max(0, capacity - HEADER.size)} UTF-8 bytes available')
    packet = HEADER.pack(MAGIC, len(payload), zlib.crc32(payload)) + payload
    channels = len(image.getbands())
    data = bytearray(image.tobytes())
    bit_index = 0
    for byte in packet:
        for shift in range(7, -1, -1):
            index = (bit_index // 3) * channels + bit_index % 3
            data[index] = (data[index] & 254) | ((byte >> shift) & 1)
            bit_index += 1
    output = Image.frombytes(image.mode, image.size, bytes(data))
    output.save(new_output(output_path), format='PNG')
    output.close()
    image.close()


def extract_text(image_path):
    with Image.open(image_path) as source:
        if source.format != 'PNG':
            raise ValueError('Encoded images must be PNG')
        image = source.convert('RGB')
    capacity = image.width * image.height * 3 // 8
    if capacity < HEADER.size:
        raise ValueError('Image is too small to contain a supported payload')
    data = image.tobytes()
    image.close()

    def read_bytes(count):
        result = bytearray()
        for offset in range(0, count * 8, 8):
            byte = 0
            for channel in data[offset:offset + 8]:
                byte = (byte << 1) | (channel & 1)
            result.append(byte)
        return bytes(result)

    magic, length, checksum = HEADER.unpack(read_bytes(HEADER.size))
    if magic != MAGIC:
        raise ValueError('No supported LSB1 text payload found')
    if length > capacity - HEADER.size:
        raise ValueError('Invalid payload length: image may be truncated or modified')
    payload = read_bytes(HEADER.size + length)[HEADER.size:]
    if zlib.crc32(payload) != checksum:
        raise ValueError('Payload checksum mismatch: image may have been modified')
    try:
        return payload.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise ValueError('Payload is not valid UTF-8 text') from exc


# Compatibility names; these hide/extract text and do not encrypt/decrypt it.
def encrypt_password_to_image(password, image_path, output_path):
    return embed_text(password, image_path, output_path)


def decrypt_password_from_image(image_path):
    return extract_text(image_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    demo = commands.add_parser('demo', help='Create a synthetic PNG cover image')
    demo.add_argument('--output', type=Path, required=True)
    embed = commands.add_parser('embed')
    embed.add_argument('--input', type=Path, required=True)
    embed.add_argument('--text-file', type=Path, required=True)
    embed.add_argument('--output', type=Path, required=True)
    extract = commands.add_parser('extract')
    extract.add_argument('--input', type=Path, required=True)
    extract.add_argument('--output', type=Path, required=True, help='New UTF-8 text file')
    args = parser.parse_args()
    try:
        if args.command == 'demo':
            if args.output.suffix.lower() != '.png':
                raise ValueError('Demo output must use .png')
            image = Image.new('RGB', (100, 100), (120, 160, 200))
            image.save(new_output(args.output), format='PNG')
            image.close()
        elif args.command == 'embed':
            if args.output.resolve() == args.text_file.resolve():
                raise ValueError('Output must differ from the text input')
            embed_text(args.text_file.read_text(encoding='utf-8'), args.input, args.output)
        else:
            text = extract_text(args.input)
            new_output(args.output).write_text(text, encoding='utf-8')
    except (ValueError, OSError, UnidentifiedImageError) as exc:
        parser.exit(1, f'Error: {exc}\n')
    print(f'Created {args.output}')


if __name__ == '__main__':
    main()
