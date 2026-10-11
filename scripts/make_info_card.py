#!/usr/bin/env python3
"""
Generate a neofetch-style info card SVG.
Each line fades/slides in on a stagger.
"""
import os
from pathlib import Path

# ─── CONFIG ──────────────────────────────────────────────────────────────
# Edit these to match your profile
USERNAME = "Mohammed-Ateeq-nova"
DISPLAY_NAME = "Mohammed Ateeq"
TITLE = "Software Engineer"
LOCATION = "Earth"

NOW = "Building things that matter"
PREV = "Full-stack development • Cloud infrastructure • Open source"

STACK = "Python, TypeScript, Go, Rust, C++, Docker, Kubernetes, AWS, PostgreSQL, Redis"
HIGHLIGHTS = "100+ GitHub stars • 50+ repos • Open source contributor • Mentor"

# Visual
CARD_WIDTH = 490
CARD_HEIGHT = 320
BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"
TITLE_BG = "#161b22"
TEXT_PRIMARY = "#e6edf3"
TEXT_MUTED = "#8b949e"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
ORANGE = "#d29922"
PURPLE = "#a371f7"

FONT_FAMILY = '"SF Mono", "Fira Code", "Monospace"'
FONT_SIZE = 11
LINE_HEIGHT = 20
PADDING = 16

# Animation
STAGGER_MS = 120
FADE_DUR_MS = 400
SLIDE_DX = 8


def make_info_card(output_path: str = "info-card.svg") -> None:
    lines = [
        # (label, value, color, bold)
        ("", f"{DISPLAY_NAME} @ {USERNAME}", TEXT_PRIMARY, True),
        ("", TITLE, ACCENT, True),
        ("", LOCATION, TEXT_MUTED, False),
        ("", "", TEXT_MUTED, False),  # spacer
        ("Now", NOW, GREEN, False),
        ("Prev", PREV, TEXT_MUTED, False),
        ("", "", TEXT_MUTED, False),
        ("Stack", STACK, TEXT_PRIMARY, False),
        ("", "", TEXT_MUTED, False),
        ("Highlights", HIGHLIGHTS, ORANGE, False),
    ]

    # Calculate actual height needed
    content_lines = [l for l in lines if l[1] or l[0]]
    actual_height = PADDING * 2 + len(content_lines) * LINE_HEIGHT + 40  # title bar

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CARD_WIDTH} {actual_height}" ',
        f'     width="{CARD_WIDTH}" height="{actual_height}">',
        f'  <defs>',
        f'    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">',
        f'      <feGaussianBlur stdDeviation="2" result="blur"/>',
        f'      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
        f'    </filter>',
        f'  </defs>',
        f'  <!-- Background -->',
        f'  <rect x="0" y="0" width="{CARD_WIDTH}" height="{actual_height}" ',
        f'        rx="8" fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1"/>',
        f'  <!-- Title bar -->',
        f'  <rect x="0" y="0" width="{CARD_WIDTH}" height="36" ',
        f'        rx="8" ry="0" fill="{TITLE_BG}"/>',
        f'  <rect x="0" y="36" width="{CARD_WIDTH}" height="{actual_height - 36}" ',
        f'        fill="{TITLE_BG}" />',
        f'  <!-- Traffic lights -->',
        f'  <circle cx="14" cy="18" r="6" fill="#ff5f57"/>',
        f'  <circle cx="32" cy="18" r="6" fill="#ffbd2e"/>',
        f'  <circle cx="50" cy="18" r="6" fill="#28ca42"/>',
        f'  <text x="70" y="24" font-family={FONT_FAMILY} font-size="11" fill="{TEXT_MUTED}">',
        f'    {DISPLAY_NAME}@github',
        f'  </text>',
        f'  <style>',
        f'    .label {{ font-family: {FONT_FAMILY}; font-size: {FONT_SIZE}px; fill: {TEXT_MUTED}; font-weight: 600; }}',
        f'    .value {{ font-family: {FONT_FAMILY}; font-size: {FONT_SIZE}px; }}',
        f'    .bold {{ font-weight: 600; }}',
        f'  </style>',
    ]

    y = PADDING + 36  # start below title bar

    for i, (label, value, color, bold) in enumerate(lines):
        if not label and not value:
            y += LINE_HEIGHT // 2
            continue

        delay = i * STAGGER_MS
        cls = "value bold" if bold else "value"
        style = f'fill="{color};"'

        # Label
        if label:
            svg_parts.append(
                f'  <text x="{PADDING}" y="{y}" class="label" '
                f'style="opacity:0" '
                f'transform="translate({SLIDE_DX}, 0)">'
                f'{escape_xml(label)}'
                f'  <animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay}ms" dur="{FADE_DUR_MS}ms" fill="freeze"/>'
                f'  <animate attributeName="transform" from="translate({SLIDE_DX}, 0)" to="translate(0, 0)" '
                f'begin="{delay}ms" dur="{FADE_DUR_MS}ms" fill="freeze"/>'
                f'</text>'
            )
            label_w = len(label) * 6.5
            val_x = PADDING + label_w + 8
        else:
            val_x = PADDING

        # Value
        if value:
            svg_parts.append(
                f'  <text x="{val_x}" y="{y}" class="{cls}" style="{style} opacity:0" '
                f'transform="translate({SLIDE_DX}, 0)">'
                f'{escape_xml(value)}'
                f'  <animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay}ms" dur="{FADE_DUR_MS}ms" fill="freeze"/>'
                f'  <animate attributeName="transform" from="translate({SLIDE_DX}, 0)" to="translate(0, 0)" '
                f'begin="{delay}ms" dur="{FADE_DUR_MS}ms" fill="freeze"/>'
                f'</text>'
            )

        y += LINE_HEIGHT

    # Static version for previews
    if os.environ.get("STATIC") == "1":
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CARD_WIDTH} {actual_height}" ',
            f'     width="{CARD_WIDTH}" height="{actual_height}">',
            f'  <rect x="0" y="0" width="{CARD_WIDTH}" height="{actual_height}" ',
            f'        rx="8" fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1"/>',
            f'  <rect x="0" y="0" width="{CARD_WIDTH}" height="36" rx="8" ry="0" fill="{TITLE_BG}"/>',
            f'  <circle cx="14" cy="18" r="6" fill="#ff5f57"/>',
            f'  <circle cx="32" cy="18" r="6" fill="#ffbd2e"/>',
            f'  <circle cx="50" cy="18" r="6" fill="#28ca42"/>',
            f'  <text x="70" y="24" font-family={FONT_FAMILY} font-size="11" fill="{TEXT_MUTED}">',
            f'    {DISPLAY_NAME}@github',
            f'  </text>',
            f'  <style>',
            f'    .label {{ font-family: {FONT_FAMILY}; font-size: {FONT_SIZE}px; fill: {TEXT_MUTED}; font-weight: 600; }}',
            f'    .value {{ font-family: {FONT_FAMILY}; font-size: {FONT_SIZE}px; }}',
            f'    .bold {{ font-weight: 600; }}',
            f'  </style>',
        ]
        y = PADDING + 36
        for label, value, color, bold in lines:
            if not label and not value:
                y += LINE_HEIGHT // 2
                continue
            cls = "value bold" if bold else "value"
            style = f'fill="{color};"'
            if label:
                svg_parts.append(f'  <text x="{PADDING}" y="{y}" class="label">{escape_xml(label)}</text>')
                label_w = len(label) * 6.5
                val_x = PADDING + label_w + 8
            else:
                val_x = PADDING
            if value:
                svg_parts.append(f'  <text x="{val_x}" y="{y}" class="{cls}" style="{style}">{escape_xml(value)}</text>')
            y += LINE_HEIGHT

    svg_parts.append('</svg>')

    Path(output_path).write_text("\n".join(svg_parts))
    print(f"Wrote {output_path}")


def escape_xml(text: str) -> str:
    return text.replace("&", "&").replace("<", "<").replace(">", ">")


if __name__ == "__main__":
    make_info_card()