#!/usr/bin/env python3
"""
Install the supplied vectorized ASCII portrait as the README artwork.
"""
import os
import shutil
import sys
from html import escape
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


# Density ramp: dark (dense) -> bright (sparse)
# Leading space clears background to nothing
RAMP = " .`:-=+*cs#%@"

# Output dimensions (chars wide × rows tall)
TARGET_WIDTH = 100

# Animation timing
ROW_DELAY_MS = 80       # stagger between rows
CHAR_DURATION_MS = 15   # time per character in a row
CURSOR_WIDTH = 2        # cursor block width in chars
FONT_SIZE = 10
LINE_HEIGHT = 14
CHAR_WIDTH = 7.5

# Colors
FILL_COLOR = "#8b949e"   # GitHub light gray
BG_COLOR = "#0d1117"     # GitHub dark background


def image_to_ascii(image_path: str, width: int = TARGET_WIDTH) -> list[str]:
    """Convert image to ASCII art lines."""
    img = Image.open(image_path).convert("L")  # grayscale
    height = max(1, round(img.height / img.width * width * CHAR_WIDTH / LINE_HEIGHT))
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    arr = np.array(img)

    # Normalize to 0-1 and map to ramp
    normalized = arr / 255.0
    ramp_len = len(RAMP) - 1
    indices = ((1.0 - normalized) * ramp_len).astype(int)
    indices = np.clip(indices, 0, ramp_len)

    lines = []
    for row in indices:
        line = "".join(RAMP[i] for i in row)
        lines.append(line.rstrip())  # trim trailing spaces
    return lines


def make_typing_svg(lines: list[str], output_path: str) -> None:
    """Generate SVG with row-by-row typing animation."""
    # Font metrics (monospace)
    svg_width = int(TARGET_WIDTH * CHAR_WIDTH) + 20
    svg_height = int(len(lines) * LINE_HEIGHT) + 20

    # Build SVG
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}"',
        f'     width="{svg_width}" height="{svg_height}">',
        f'  <rect width="100%" height="100%" fill="{BG_COLOR}"/>',
        f'  <style>',
        f'    .char {{ font-family: "SF Mono", "Fira Code", "Monospace"; font-size: {FONT_SIZE}px; fill: {FILL_COLOR}; }}',
        f'    .cursor {{ font-family: "SF Mono", "Fira Code", "Monospace"; font-size: {FONT_SIZE}px; fill: {FILL_COLOR}; }}',
        f'  </style>',
    ]

    # Each row gets a clipPath that wipes left-to-right
    for row_idx, line in enumerate(lines):
        if not line:
            continue

        y = 10 + row_idx * LINE_HEIGHT
        row_delay = row_idx * ROW_DELAY_MS

        # Create a group for this row with clip animation
        svg_parts.append(f'  <g>')
        # Clip path that reveals left to right
        clip_id = f"clip-row-{row_idx}"
        svg_parts.append(f'    <clipPath id="{clip_id}">')
        # Animated rectangle that grows from left
        total_chars = len(line)
        anim_dur = total_chars * CHAR_DURATION_MS
        svg_parts.append(
            f'      <rect x="10" y="{y - FONT_SIZE}" width="0" height="{LINE_HEIGHT}">'
            f'        <animate attributeName="width" from="0" to="{total_chars * CHAR_WIDTH}" '
            f'begin="{row_delay}ms" dur="{anim_dur}ms" fill="freeze"/>'
            f'      </rect>'
        )
        svg_parts.append(f'    </clipPath>')

        # Text with clip-path
        clip_url = f"url(#{clip_id})"
        svg_parts.append(
            f'    <text x="10" y="{y + 2}" class="char" clip-path="{clip_url}">{escape_xml(line)}</text>'
        )

        # Cursor block that rides the edge
        cursor_x = 10
        cursor_y = y - FONT_SIZE
        cursor_w = CURSOR_WIDTH * CHAR_WIDTH
        svg_parts.append(
            f'    <rect x="{cursor_x}" y="{cursor_y}" width="{cursor_w}" height="{LINE_HEIGHT}" '
            f'fill="{FILL_COLOR}" opacity="0">'
            f'      <animate attributeName="x" from="10" to="{10 + total_chars * CHAR_WIDTH - cursor_w}" '
            f'begin="{row_delay}ms" dur="{anim_dur}ms" fill="freeze"/>'
            f'      <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.99;1" '
            f'begin="{row_delay}ms" dur="{anim_dur}ms" fill="freeze"/>'
            f'    </rect>'
        )
        svg_parts.append(f'  </g>')

    # Static version for STATIC=1 env (for previews)
    if os.environ.get("STATIC") == "1":
        # Rebuild without animations - just final state
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}"',
            f'     width="{svg_width}" height="{svg_height}">',
            f'  <rect width="100%" height="100%" fill="{BG_COLOR}"/>',
            f'  <style>',
            f'    .char {{ font-family: "SF Mono", "Fira Code", "Monospace"; font-size: {FONT_SIZE}px; fill: {FILL_COLOR}; }}',
            f'  </style>',
        ]
        for row_idx, line in enumerate(lines):
            if not line:
                continue
            y = 10 + row_idx * LINE_HEIGHT
            svg_parts.append(f'  <text x="10" y="{y + 2}" class="char">{escape_xml(line)}</text>')

    svg_parts.append('</svg>')

    Path(output_path).write_text("\n".join(svg_parts), encoding="utf-8")
    print(f"Wrote {output_path} ({len(lines)} rows)")


def escape_xml(text: str) -> str:
    return escape(text)


def main():
    input_path = Path("asciinator_11Oct_001.svg")
    output_path = Path("mohammed-ascii.svg")

    if not input_path.exists():
        print(f"Error: {input_path} not found.")
        sys.exit(1)

    shutil.copyfile(input_path, output_path)
    print(f"Copied {input_path} to {output_path}")


if __name__ == "__main__":
    main()