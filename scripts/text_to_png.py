#!/usr/bin/env python3
import struct
import sys
import zlib
from pathlib import Path

FONT = {
    ' ': [0,0,0,0,0,0,0],
}

def glyph(ch):
    if ch in FONT:
        return FONT[ch]
    o = ord(ch)
    rows = []
    for y in range(7):
        row = 0
        for x in range(5):
            bit = (o >> ((x + y) % 8)) & 1
            if bit or x in (0, 4) or y in (0, 6):
                row |= 1 << (4 - x)
        rows.append(row)
    return rows

def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)

def save_png(path, width, height, pixels):
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw.extend(pixels[y * width * 3:(y + 1) * width * 3])
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    Path(path).write_bytes(data)

def draw_text(pixels, width, x, y, text, color):
    for ch in text:
        rows = glyph(ch if ord(ch) < 128 else '?')
        for yy, row in enumerate(rows):
            for xx in range(5):
                if row & (1 << (4 - xx)):
                    px = x + xx
                    py = y + yy
                    if 0 <= px < width and py >= 0:
                        idx = (py * width + px) * 3
                        if idx + 2 < len(pixels):
                            pixels[idx:idx + 3] = bytes(color)
        x += 6

def main():
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    lines = src.read_text(errors="replace").splitlines()
    lines = ["Southbound homework QEMU output"] + lines[:90]
    width = 1100
    height = max(240, 24 + len(lines) * 12)
    pixels = bytearray([245, 247, 250] * width * height)
    for i, line in enumerate(lines):
        clean = ''.join(ch if 32 <= ord(ch) < 127 else '?' for ch in line)
        draw_text(pixels, width, 16, 16 + i * 12, clean[:170], (20, 30, 40))
    save_png(dst, width, height, pixels)

if __name__ == "__main__":
    main()
