#!/usr/bin/env python3
"""List Uma Musume birthdays in calendar order."""

from __future__ import annotations

import csv
import datetime as dt
import re
import sys
from pathlib import Path

BIRTHDAY_PATTERN = re.compile(r"(\d+)\s*月\s*(\d+)\s*日")


def parse_birthday(raw: str) -> tuple[int, int] | None:
    match = BIRTHDAY_PATTERN.search(raw.strip())
    if not match:
        return None
    month, day = match.groups()
    return int(month), int(day)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    csv_path = repo_root / "resources" / "docs" / "umamusume_character_baseinfo.csv"

    if not csv_path.exists():
        print(f"CSV not found: {csv_path}", file=sys.stderr)
        return 1

    entries: list[tuple[int, int, str, str]] = []
    skipped = 0

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            name = (row.get("赛马娘中文名") or "").strip()
            birthday_raw = (row.get("赛马娘生日") or "").strip()
            if not name or not birthday_raw:
                skipped += 1
                continue
            parsed = parse_birthday(birthday_raw)
            if not parsed:
                skipped += 1
                continue
            month, day = parsed
            entries.append((month, day, name, birthday_raw))

    entries.sort(key=lambda item: (item[0], item[1], item[2]))

    today = dt.date.today()
    today_md = (today.month, today.day)
    today_birthday = f"{today.month}月{today.day}日"
    print(f"Today: {today.isoformat()} ({today_birthday})", file=sys.stderr)
    use_color = sys.stdout.isatty()

    for month, day, name, birthday_raw in entries:
        line = f"{birthday_raw}\t{name}"
        if (month, day) == today_md:
            if use_color:
                line = f"\033[1;33m{line}\033[0m"
            else:
                line = f"[TODAY] {line}"
        print(line)

    if skipped:
        print(f"Skipped {skipped} rows without valid birthday.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
