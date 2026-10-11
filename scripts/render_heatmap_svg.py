#!/usr/bin/env python3
"""
Render contribution heatmap as animated SVG.
Diagonal slide-in reveal, then freeze.
"""
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# ─── CONFIG ──────────────────────────────────────────────────────────────
USERNAME = "Mohammed-Ateeq-nova"
DATA_PATH = Path("data/contributions.json")
OUTPUT_PATH = Path("contrib-heatmap.svg")

# GitHub-like green palette (level 0-5)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

# Grid dimensions
WEEKS = 53
DAYS_PER_WEEK = 7
BOX_SIZE = 13
BOX_GAP = 3
BOX_RADIUS = 2

# Layout
MARGIN_LEFT = 40   # space for month labels
MARGIN_TOP = 30    # space for year label
MARGIN_BOTTOM = 50 # space for legend + stats
MARGIN_RIGHT = 20

# Colors
BG_COLOR = "#0d1117"
TEXT_COLOR = "#8b949e"
TEXT_PRIMARY = "#e6edf3"
BORDER_COLOR = "#30363d"

# Animation
STAGGER_MS = 30        # delay between each box
DIAGONAL_DELAY = 15    # extra delay per week (diagonal effect)
ANIM_DUR_MS = 500      # slide duration

FONT_FAMILY = '"SF Mono", "Fira Code", "Monospace"'


def load_data() -> dict:
    with open(DATA_PATH) as f:
        return json.load(f)


def build_grid(data: dict) -> list[list[int]]:
    """Build 53x7 grid of levels (0-5)."""
    # Initialize empty grid
    grid = [[0 for _ in range(DAYS_PER_WEEK)] for _ in range(WEEKS)]

    # Fill from data
    for day in data["days"]:
        dt = datetime.fromisoformat(day["date"]).date()
        # Calculate week index (0-52) and day of week (0-6, Sun=0)
        # GitHub weeks start from the Sunday of the first week of the year
        # Approximate: find the Sunday of the week containing Jan 1
        jan1 = date(dt.year, 1, 1)
        # Day of week: Monday=0 ... Sunday=6 in Python, but GitHub uses Sun=0
        jan1_dow = (jan1.weekday() + 1) % 7  # Sun=0
        first_sunday = jan1 - timedelta(days=jan1_dow)
        days_diff = (dt - first_sunday).days
        week = days_diff // 7
        dow = days_diff % 7  # 0=Sun

        if 0 <= week < WEEKS and 0 <= dow < DAYS_PER_WEEK:
            grid[week][dow] = day["level"]

    return grid


def make_heatmap_svg(grid: list[list[int]], stats: dict) -> str:
    svg_width = MARGIN_LEFT + WEEKS * (BOX_SIZE + BOX_GAP) + MARGIN_RIGHT
    svg_height = MARGIN_TOP + DAYS_PER_WEEK * (BOX_SIZE + BOX_GAP) + MARGIN_BOTTOM

    # Month label positions (approximate)
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_positions = []
    for m in range(1, 13):
        # First day of month
        try:
            first = date(2024, m, 1)  # use leap year for Feb 29
        except ValueError:
            first = date(2024, m, 1)
        jan1 = date(2024, 1, 1)
        jan1_dow = (jan1.weekday() + 1) % 7
        first_sunday = jan1 - timedelta(days=jan1_dow)
        days_diff = (first - first_sunday).days
        week = days_diff // 7
        if 0 <= week < WEEKS:
            x = MARGIN_LEFT + week * (BOX_SIZE + BOX_GAP) + BOX_SIZE // 2
            month_positions.append((x, month_names[m - 1]))

    # Day labels (Sun, Mon, ... Sat)
    day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" ')
    svg.append(f'     width="{svg_width}" height="{svg_height}">')
    svg.append(f'  <rect width="100%" height="100%" fill="{BG_COLOR}"/>')
    svg.append(f'  <style>')
    svg.append(f'    .label {{ font-family: {FONT_FAMILY}; font-size: 9px; fill: {TEXT_COLOR}; }}')
    svg.append(f'    .label-bold {{ font-family: {FONT_FAMILY}; font-size: 9px; fill: {TEXT_PRIMARY}; font-weight: 600; }}')
    svg.append(f'    .stat {{ font-family: {FONT_FAMILY}; font-size: 11px; fill: {TEXT_PRIMARY}; }}')
    svg.append(f'    .stat-label {{ font-family: {FONT_FAMILY}; font-size: 11px; fill: {TEXT_COLOR}; }}')
    svg.append(f'  </style>')

    # Month labels (top)
    for x, label in month_positions:
        svg.append(f'  <text x="{x}" y="{MARGIN_TOP - 6}" text-anchor="middle" class="label">{label}</text>')

    # Day labels (left)
    for i, label in enumerate(day_labels):
        y = MARGIN_TOP + i * (BOX_SIZE + BOX_GAP) + BOX_SIZE - 2
        svg.append(f'  <text x="{MARGIN_LEFT - 8}" y="{y}" text-anchor="end" class="label">{label}</text>')

    # Contribution boxes with diagonal animation
    for week in range(WEEKS):
        for dow in range(DAYS_PER_WEEK):
            level = grid[week][dow]
            color = PALETTE[min(level, len(PALETTE) - 1)]

            x = MARGIN_LEFT + week * (BOX_SIZE + BOX_GAP)
            y = MARGIN_TOP + dow * (BOX_SIZE + BOX_GAP)

            # Diagonal delay: week * DIAGONAL_DELAY + dow * STAGGER_MS
            delay = week * DIAGONAL_DELAY + dow * STAGGER_MS

            # Slide in from top-left
            svg.append(
                f'  <rect x="{x}" y="{y}" width="{BOX_SIZE}" height="{BOX_SIZE}" '
                f'rx="{BOX_RADIUS}" fill="{color}" opacity="0" '
                f'transform="translate(-10, -10)">'
                f'    <animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay}ms" dur="{ANIM_DUR_MS}ms" fill="freeze"/>'
                f'    <animate attributeName="transform" from="translate(-10, -10)" to="translate(0, 0)" '
                f'begin="{delay}ms" dur="{ANIM_DUR_MS}ms" fill="freeze" '
                f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
                f'  </rect>'
            )

    # Legend
    legend_y = MARGIN_TOP + DAYS_PER_WEEK * (BOX_SIZE + BOX_GAP) + 20
    legend_x = MARGIN_LEFT
    svg.append(f'  <text x="{legend_x}" y="{legend_y - 4}" class="label">Less</text>')
    for i, color in enumerate(PALETTE):
        lx = legend_x + 40 + i * (BOX_SIZE + 4)
        svg.append(f'  <rect x="{lx}" y="{legend_y - BOX_SIZE}" width="{BOX_SIZE}" height="{BOX_SIZE}" rx="{BOX_RADIUS}" fill="{color}"/>')
    svg.append(f'  <text x="{legend_x + 40 + len(PALETTE) * (BOX_SIZE + 4) + 8}" y="{legend_y - 4}" class="label">More</text>')

    # Stats footer
    stats_y = legend_y + 28
    total = stats["total_contributions"]
    current_streak = stats["current_streak"]
    longest_streak = stats["longest_streak"]
    best_day = stats["best_day"]

    svg.append(f'  <text x="{MARGIN_LEFT}" y="{stats_y}" class="stat">')
    svg.append(f'    {total:,} contributions in the last year')
    svg.append(f'  </text>')

    stats_y += 20
    svg.append(f'  <text x="{MARGIN_LEFT}" y="{stats_y}" class="stat-label">Current streak: </text>')
    svg.append(f'  <text x="{MARGIN_LEFT + 110}" y="{stats_y}" class="stat">{current_streak} days</text>')

    stats_y += 18
    svg.append(f'  <text x="{MARGIN_LEFT}" y="{stats_y}" class="stat-label">Longest streak: </text>')
    svg.append(f'  <text x="{MARGIN_LEFT + 110}" y="{stats_y}" class="stat">{longest_streak} days</text>')

    stats_y += 18
    if best_day["date"]:
        svg.append(f'  <text x="{MARGIN_LEFT}" y="{stats_y}" class="stat-label">Best day: </text>')
        svg.append(f'  <text x="{MARGIN_LEFT + 110}" y="{stats_y}" class="stat">{best_day["date"]} ({best_day["count"]} contributions)</text>')

    # Static version for previews
    if os.environ.get("STATIC") == "1":
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" ',
            f'     width="{svg_width}" height="{svg_height}">',
            f'  <rect width="100%" height="100%" fill="{BG_COLOR}"/>',
            f'  <style>',
            f'    .label {{ font-family: {FONT_FAMILY}; font-size: 9px; fill: {TEXT_COLOR}; }}',
            f'    .label-bold {{ font-family: {FONT_FAMILY}; font-size: 9px; fill: {TEXT_PRIMARY}; font-weight: 600; }}',
            f'    .stat {{ font-family: {FONT_FAMILY}; font-size: 11px; fill: {TEXT_PRIMARY}; }}',
            f'    .stat-label {{ font-family: {FONT_FAMILY}; font-size: 11px; fill: {TEXT_COLOR}; }}',
            f'  </style>',
        ]
        # Month labels
        for x, label in month_positions:
            svg.append(f'  <text x="{x}" y="{MARGIN_TOP - 6}" text-anchor="middle" class="label">{label}</text>')
        # Day labels
        for i, label in enumerate(day_labels):
            y = MARGIN_TOP + i * (BOX_SIZE + BOX_GAP) + BOX_SIZE - 2
            svg.append(f'  <text x="{MARGIN_LEFT - 8}" y="{y}" text-anchor="end" class="label">{label}</text>')
        # Boxes (static)
        for week in range(WEEKS):
            for dow in range(DAYS_PER_WEEK):
                level = grid[week][dow]
                color = PALETTE[min(level, len(PALETTE) - 1)]
                x = MARGIN_LEFT + week * (BOX_SIZE + BOX_GAP)
                y = MARGIN_TOP + dow * (BOX_SIZE + BOX_GAP)
                svg.append(f'  <rect x="{x}" y="{y}" width="{BOX_SIZE}" height="{BOX_SIZE}" rx="{BOX_RADIUS}" fill="{color}"/>')
        # Legend
        legend_y = MARGIN_TOP + DAYS_PER_WEEK * (BOX_SIZE + BOX_GAP) + 20
        legend_x = MARGIN_LEFT
        svg.append(f'  <text x="{legend_x}" y="{legend_y - 4}" class="label">Less</text>')
        for i, color in enumerate(PALETTE):
            lx = legend_x + 40 + i * (BOX_SIZE + 4)
            svg.append(f'  <rect x="{lx}" y="{legend_y - BOX_SIZE}" width="{BOX_SIZE}" height="{BOX_SIZE}" rx="{BOX_RADIUS}" fill="{color}"/>')
        svg.append(f'  <text x="{legend_x + 40 + len(PALETTE) * (BOX_SIZE + 4) + 8}" y="{legend_y - 4}" class="label">More</text>')
        # Stats
        stats_y = legend_y + 28
        svg.append(f'  <text x="{MARGIN_LEFT}" y="{stats_y}" class="stat">{total:,} contributions in the last year</text>')
        stats_y += 20
        svg.append(f'  <text x="{MARGIN_LEFT}" y="{stats_y}" class="stat-label">Current streak: </text>')
        svg.append(f'  <text x="{MARGIN_LEFT + 110}" y="{stats_y}" class="stat">{current_streak} days</text>')
        stats_y += 18
        svg.append(f'  <text x="{MARGIN_LEFT}" y="{stats_y}" class="stat-label">Longest streak: </text>')
        svg.append(f'  <text x="{MARGIN_LEFT + 110}" y="{stats_y}" class="stat">{longest_streak} days</text>')
        stats_y += 18
        if best_day["date"]:
            svg.append(f'  <text x="{MARGIN_LEFT}" y="{stats_y}" class="stat-label">Best day: </text>')
            svg.append(f'  <text x="{MARGIN_LEFT + 110}" y="{stats_y}" class="stat">{best_day["date"]} ({best_day["count"]} contributions)</text>')

    svg.append('</svg>')
    return "\n".join(svg)


def main():
    if not DATA_PATH.exists():
        print(f"Error: {DATA_PATH} not found. Run fetch_contributions.py first.")
        sys.exit(1)

    print("Loading contribution data...")
    data = load_data()

    print("Building grid...")
    grid = build_grid(data)

    print("Generating heatmap SVG...")
    svg_content = make_heatmap_svg(grid, data["stats"])

    OUTPUT_PATH.write_text(svg_content)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()