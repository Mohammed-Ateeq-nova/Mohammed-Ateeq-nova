#!/usr/bin/env python3
"""
Fetch GitHub contribution data from public contributions page.
No token needed - scrapes the public HTML.
"""
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Mohammed-Ateeq-nova"
CONTRIB_URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT_PATH = Path("data/contributions.json")


def fetch_contributions() -> dict:
    """Scrape contribution calendar from GitHub."""
    print(f"Fetching contributions from {CONTRIB_URL}...")
    resp = requests.get(CONTRIB_URL, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Find all contribution day cells - new GitHub format uses td.ContributionCalendar-day
    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        date_str = td.get("data-date")
        level = int(td.get("data-level", 0))
        if not date_str or level == 0:
            continue

        # Extract count from tooltip
        tooltip = td.find_next("tool-tip")
        count = 0
        if tooltip:
            tooltip_text = tooltip.get_text()
            match = re.search(r"(\d+)\s+contribution", tooltip_text)
            if match:
                count = int(match.group(1))
            else:
                # Fallback: estimate from level
                count = level

        if count > 0:
            days.append({"date": date_str, "count": count, "level": level})

    # Also check the summary for total
    total_match = re.search(r"(\d+)\s+contributions?\s+in the last year", resp.text)
    total_from_summary = int(total_match.group(1)) if total_match else None

    print(f"Found {len(days)} contribution days")

    # Compute stats
    stats = compute_stats(days, total_from_summary)

    return {
        "username": USERNAME,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }


def compute_stats(days: list[dict], total_from_summary: int | None = None) -> dict:
    """Compute streak and summary stats from contribution days."""
    if not days:
        return {
            "total_contributions": total_from_summary or 0,
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": {"date": None, "count": 0},
            "monthly_totals": {},
        }

    # Sort by date
    days_sorted = sorted(days, key=lambda d: d["date"])
    dates = [datetime.fromisoformat(d["date"]).date() for d in days_sorted]

    # Total contributions - use summary if available, otherwise sum
    total = total_from_summary if total_from_summary is not None else sum(d["count"] for d in days)

    # Best day
    best = max(days, key=lambda d: d["count"])

    # Monthly totals
    monthly = {}
    for d in days:
        dt = datetime.fromisoformat(d["date"])
        key = dt.strftime("%Y-%m")
        monthly[key] = monthly.get(key, 0) + d["count"]

    # Current streak (from today backwards)
    today = datetime.utcnow().date()
    current_streak = 0
    check_date = today
    date_set = set(dates)

    while check_date in date_set:
        current_streak += 1
        check_date -= timedelta(days=1)

    # Longest streak
    longest_streak = 0
    streak = 0
    prev_date = None

    for dt in dates:
        if prev_date and (dt - prev_date).days == 1:
            streak += 1
        else:
            streak = 1
        longest_streak = max(longest_streak, streak)
        prev_date = dt

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly_totals": monthly,
    }


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        data = fetch_contributions()
        OUTPUT_PATH.write_text(json.dumps(data, indent=2))
        print(f"Wrote {OUTPUT_PATH}")
        print(f"Total contributions: {data['stats']['total_contributions']}")
        print(f"Current streak: {data['stats']['current_streak']} days")
        print(f"Longest streak: {data['stats']['longest_streak']} days")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()