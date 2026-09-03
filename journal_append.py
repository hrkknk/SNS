#!/usr/bin/env python3
"""日記を Notion に1件作る。空入力では何もしない。検索・追記はしない。"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

JOURNAL_DB = "0bf755f4-eadf-4a0f-84e7-d67744d4ec82"
NOTION_VERSION = "2025-09-03"
NOTION_API = "https://api.notion.com/v1"
ZSHRC_PATH = Path.home() / ".zshrc"
MAX_RICH_TEXT = 1900
MAX_TITLE = 100


class JournalError(Exception):
    pass


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


def title_from_body(text: str) -> str:
    first_line = text.splitlines()[0].strip() if text.strip() else text
    if len(first_line) <= MAX_TITLE:
        return first_line
    return first_line[: MAX_TITLE - 1] + "…"


def create_page(token: str, text: str, database_id: str = JOURNAL_DB) -> str:
    children = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": chunk}}]
            },
        }
        for chunk in chunk_text(text)
    ]
    body: dict[str, Any] = {
        "parent": {"database_id": database_id},
        "properties": {
            "名前": {"title": [{"text": {"content": title_from_body(text)}}]},
            "ネタ化済み": {"checkbox": False},
        },
        "children": children,
    }
    created = notion_request(token, "POST", "/pages", body)
    page_id = created.get("id")
    if not page_id:
        raise JournalError(f"ページ作成に失敗: {created}")
    return page_id


def append_journal(text: str, token: Optional[str] = None) -> dict:
    cleaned = text.strip()
    if not cleaned:
        raise JournalError("空の入力では日記を作らない")
    auth = token if token is not None else read_notion_token()
    page_id = create_page(auth, cleaned)
    return {"action": "create", "page_id": page_id}


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="日記を Notion に1件作成")
    parser.add_argument("text", nargs="?", help="本文。省略時は stdin")
    args = parser.parse_args(argv)

    body = args.text if args.text is not None else sys.stdin.read()
    try:
        result = append_journal(body)
    except JournalError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
