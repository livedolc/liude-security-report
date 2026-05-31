#!/usr/bin/env python3
"""Download and index daily DOLC security report pages."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
INDEX_PATH = ROOT / "index.html"
MANIFEST_PATH = ROOT / "reports.json"
SOURCE_TEMPLATE = "https://dolc.biz/security/sh_{date}.html"


def berlin_today() -> dt.date:
    return dt.datetime.now(ZoneInfo("Europe/Berlin")).date()


def parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD format") from exc


def fetch_url(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "liude-security-report-archiver/1.0 (+https://github.com/)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def report_name(day: dt.date) -> str:
    return f"sh_{day:%Y%m%d}.html"


def source_url(day: dt.date) -> str:
    return SOURCE_TEMPLATE.format(date=f"{day:%Y%m%d}")


def download_report(day: dt.date) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    target = REPORTS_DIR / report_name(day)
    url = source_url(day)

    try:
        content = fetch_url(url)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            print(f"No report found for {day.isoformat()} at {url}", file=sys.stderr)
            return target
        raise

    target.write_bytes(content)
    print(f"Saved {url} -> {target.relative_to(ROOT)}")
    return target


def discover_reports() -> list[dict[str, str]]:
    reports = []
    for path in sorted(REPORTS_DIR.glob("sh_*.html"), reverse=True):
        stamp = path.stem.removeprefix("sh_")
        if len(stamp) != 8 or not stamp.isdigit():
            continue
        day = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}"
        reports.append(
            {
                "date": day,
                "path": path.relative_to(ROOT).as_posix(),
                "source_url": SOURCE_TEMPLATE.format(date=stamp),
            }
        )
    return reports


def write_manifest(reports: list[dict[str, str]]) -> None:
    MANIFEST_PATH.write_text(
        json.dumps({"reports": reports}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_index(reports: list[dict[str, str]]) -> None:
    items = []
    for report in reports:
        date_text = html.escape(report["date"])
        path = html.escape(report["path"])
        source = html.escape(report["source_url"])
        items.append(
            f'    <li><a href="{path}">{date_text}</a> '
            f'<span class="meta">来源：<a href="{source}">{source}</a></span></li>'
        )

    index = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>留德安全汇报</title>
  <style>
    :root {{
      color-scheme: light dark;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }}
    body {{
      margin: 0;
      padding: 32px;
      max-width: 880px;
    }}
    h1 {{
      margin-top: 0;
      font-size: 32px;
    }}
    a {{
      color: #0969da;
    }}
    .meta {{
      color: #57606a;
    }}
  </style>
</head>
<body>
  <h1>留德安全汇报</h1>
  <p class="meta">每日自动归档页面：<code>https://dolc.biz/security/sh_YYYYMMDD.html</code></p>
  <h2>归档列表</h2>
  <ul>
{chr(10).join(items)}
  </ul>
</body>
</html>
"""
    INDEX_PATH.write_text(index, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=parse_date, default=berlin_today())
    parser.add_argument("--index-only", action="store_true")
    args = parser.parse_args()

    if not args.index_only:
        download_report(args.date)

    reports = discover_reports()
    write_manifest(reports)
    write_index(reports)
    print(f"Indexed {len(reports)} report(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
