#!/usr/bin/env python3
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/consola.ttf",
]

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def load_font(size):
    for candidate in FONT_CANDIDATES:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def clean_line(line):
    line = ANSI_RE.sub("", line.replace("\r", ""))
    line = CONTROL_RE.sub("", line)
    return line.rstrip()


def wrap_line(draw, line, font, max_width):
    if not line:
        return [""]

    chunks = []
    current = ""
    for ch in line:
        candidate = current + ch
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = ch
    if current:
        chunks.append(current)
    return chunks


def main():
    if len(sys.argv) != 3:
        print("usage: text_to_png.py input.log output.png", file=sys.stderr)
        return 2

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])

    title_font = load_font(24)
    body_font = load_font(18)
    meta_font = load_font(15)

    raw_lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
    content_lines = [clean_line(line) for line in raw_lines]
    content_lines = [line for line in content_lines if line or len(content_lines) <= 1]

    width = 1400
    margin_x = 36
    margin_y = 28
    line_gap = 8

    probe = Image.new("RGB", (width, 100), "white")
    draw = ImageDraw.Draw(probe)
    max_text_width = width - margin_x * 2

    rendered = []
    for line in content_lines[:120]:
        rendered.extend(wrap_line(draw, line, body_font, max_text_width))

    if not rendered:
        rendered = ["No QEMU output captured."]

    title = "Southbound Homework QEMU Output"
    meta = f"source: {src}"
    title_h = title_font.getbbox(title)[3] - title_font.getbbox(title)[1]
    meta_h = meta_font.getbbox(meta)[3] - meta_font.getbbox(meta)[1]
    line_h = body_font.getbbox("Ag")[3] - body_font.getbbox("Ag")[1] + line_gap
    height = max(320, margin_y * 2 + title_h + 14 + meta_h + 24 + line_h * len(rendered))

    image = Image.new("RGB", (width, height), (247, 249, 252))
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, width, 86), fill=(31, 41, 55))
    draw.text((margin_x, 22), title, font=title_font, fill=(255, 255, 255))
    draw.text((margin_x, 58), meta, font=meta_font, fill=(209, 213, 219))

    y = 112
    for line in rendered:
        draw.text((margin_x, y), line, font=body_font, fill=(17, 24, 39))
        y += line_h

    dst.parent.mkdir(parents=True, exist_ok=True)
    image.save(dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
