#!/usr/bin/env python3
"""今日の日記ページへ追記する。無ければ作成。入力確定後のみ Notion を更新する。"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

SNS_ROOT = Path(__file__).resolve().parent
JOURNAL_DS = "9affd3bf-a3b7-474c-baf8-25c83ba3ef47"
JOURNAL_DB = "0bf755f4-eadf-4a0f-84e7-d67744d4ec82"
NOTION_VERSION = "2025-09-03"
NOTION_API = "https://api.notion.com/v1"
ZSHRC_PATH = Path.home() / ".zshrc"
JST = timezone(timedelta(hours=9))
MAX_RICH_TEXT = 1900


class JournalError(Exception):
    pass


def today_jst(now: Optional[datetime] = None) -> str:
    stamp = now if now is not None else datetime.now(JST)
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=JST)
    return stamp.astimezone(JST).strftime("%Y-%m-%d")


def read_notion_token(
    env: Optional[dict] = None,
    zshrc_path: Path = ZSHRC_PATH,
) -> str:
    environ = env if env is not None else os.environ
    token = environ.get("NOTION_TOKEN", "").strip()
    if token:
        return token
    if not zshrc_path.exists():
        raise JournalError("NOTION_TOKEN が環境にも ~/.zshrc にも無い")
    text = zshrc_path.read_text(encoding="utf-8")
    match = re.search(r'export\s+NOTION_TOKEN=["\']?([^"\'\s]+)', text)
    if not match:
        raise JournalError(f"NOTION_TOKEN が {zshrc_path} に無い")
    return match.group(1)


def notion_request(
    token: str,
    method: str,
    path: str,
    body: Optional[dict] = None,
) -> dict:
    url = f"{NOTION_API}{path}"
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise JournalError(f"Notion {method} {path} failed: {exc.code} {detail}") from exc
    return json.loads(raw) if raw else {}


def chunk_text(text: str, size: int = MAX_RICH_TEXT) -> list[str]:
    if not text:
        return [""]
    return [text[i : i + size] for i in range(0, len(text), size)]


def paragraph_blocks(text: str, heading: Optional[str] = None) -> list[dict]:
    blocks: list[dict] = []
    if heading:
        blocks.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": heading},
                            "annotations": {"bold": True},
                        }
                    ]
                },
            }
        )
    for chunk in chunk_text(text):
        blocks.append(
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": chunk}}]
                },
            }
        )
    return blocks


def find_page_by_title(token: str, title: str, data_source_id: str = JOURNAL_DS) -> Optional[str]:
    payload = {
        "filter": {"property": "名前", "title": {"equals": title}},
        "page_size": 1,
    }
    data = notion_request(token, "POST", f"/data_sources/{data_source_id}/query", payload)
    results = data.get("results") or []
    if not results:
        return None
    return results[0]["id"]


def create_today_page(
    token: str,
    day: str,
    text: str,
    database_id: str = JOURNAL_DB,
    now: Optional[datetime] = None,
) -> str:
    stamp = (now if now is not None else datetime.now(JST)).astimezone(JST)
    heading = stamp.strftime("%H:%M")
    body: dict[str, Any] = {
        "parent": {"database_id": database_id},
        "properties": {
            "名前": {"title": [{"text": {"content": day}}]},
            "日付": {"date": {"start": day}},
            "ネタ化済み": {"checkbox": False},
        },
        "children": paragraph_blocks(text, heading=heading),
    }
    created = notion_request(token, "POST", "/pages", body)
    page_id = created.get("id")
    if not page_id:
        raise JournalError(f"ページ作成に失敗: {created}")
    return page_id


def append_entry(
    token: str,
    page_id: str,
    text: str,
    now: Optional[datetime] = None,
) -> None:
    stamp = (now if now is not None else datetime.now(JST)).astimezone(JST)
    heading = stamp.strftime("%H:%M")
    notion_request(
        token,
        "PATCH",
        f"/blocks/{page_id}/children",
        {"children": paragraph_blocks(text, heading=heading)},
    )


def append_journal(
    text: str,
    token: Optional[str] = None,
    day: Optional[str] = None,
    now: Optional[datetime] = None,
) -> dict:
    cleaned = text.strip()
    if not cleaned:
        raise JournalError("空の入力では日記を作らない")
    auth = token if token is not None else read_notion_token()
    stamp = now if now is not None else datetime.now(JST)
    target_day = day if day is not None else today_jst(stamp)
    existing = find_page_by_title(auth, target_day)
    if existing:
        append_entry(auth, existing, cleaned, now=stamp)
        return {"action": "append", "page_id": existing, "day": target_day}
    page_id = create_today_page(auth, target_day, cleaned, now=stamp)
    return {"action": "create", "page_id": page_id, "day": target_day}


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="今日の日記へ追記（確定後のみ作成）")
    parser.add_argument("text", nargs="?", help="追記する本文。省略時は stdin")
    parser.add_argument("--date", help="対象日 YYYY-MM-DD（省略時は JST の今日）")
    args = parser.parse_args(argv)

    if args.text is not None:
        body = args.text
    else:
        body = sys.stdin.read()

    try:
        result = append_journal(body, day=args.date)
    except JournalError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
