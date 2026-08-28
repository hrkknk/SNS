#!/usr/bin/env python3
"""執筆リマインダー。Notion から対象1件を選び、Terra に材料出しさせ、末尾に追記する。"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

SNS_ROOT = Path(__file__).resolve().parent
CONTENT_DS = "fe59df72-de82-4c4a-add7-be01a0fc64cc"
NOTION_VERSION = "2025-09-03"
NOTION_API = "https://api.notion.com/v1"
PROMPT_PATH = SNS_ROOT / "shippitsu_memo_prompt.md"
LOG_PATH = SNS_ROOT / "logs" / "writing-reminder.log"
ZSHRC_PATH = Path.home() / ".zshrc"
CODEX_BIN = "/opt/homebrew/bin/codex"
CODEX_TIMEOUT_SEC = 300
DELETE_INTERVAL_SEC = 0.4
JST = timezone(timedelta(hours=9))
PATH_EXTRAS = (
    "/opt/homebrew/opt/node@22/bin",
    "/opt/homebrew/bin",
    "/usr/local/bin",
)

SECTION_KEYS = ("問い", "骨組み", "関連するネタ", "詰まりそうな点")
WRITING_STATUSES = ("執筆中", "ネタ")


class ReminderError(Exception):
    pass


def today_jst(now: Optional[datetime] = None) -> str:
    stamp = now if now is not None else datetime.now(JST)
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=JST)
    return stamp.astimezone(JST).strftime("%Y-%m-%d")


def read_notion_token(zshrc_path: Path = ZSHRC_PATH) -> str:
    text = zshrc_path.read_text(encoding="utf-8")
    match = re.search(r'export\s+NOTION_TOKEN=["\']?([^"\'\s]+)', text)
    if not match:
        raise ReminderError(f"NOTION_TOKEN が {zshrc_path} に無い")
    return match.group(1)


def append_log(message: str, log_path: Path = LOG_PATH, now: Optional[datetime] = None) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = (now if now is not None else datetime.now(JST)).astimezone(JST).strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(f"{stamp} {message}\n")


def notion_request(
    token: str,
    method: str,
    path: str,
    body: Optional[dict] = None,
    query: Optional[dict] = None,
) -> dict:
    url = f"{NOTION_API}{path}"
    if query:
        url += "?" + urllib.parse.urlencode(query)
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
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ReminderError(f"Notion {method} {path} {exc.code}: {detail[:500]}") from exc
    except urllib.error.URLError as exc:
        raise ReminderError(f"Notion {method} {path} 接続失敗: {exc}") from exc
    return json.loads(raw) if raw else {}


def query_all_pages(token: str) -> List[dict]:
    pages: List[dict] = []
    cursor: Optional[str] = None
    while True:
        body: Dict[str, Any] = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        payload = notion_request(token, "POST", f"/data_sources/{CONTENT_DS}/query", body=body)
        pages.extend(payload.get("results") or [])
        if not payload.get("has_more"):
            break
        cursor = payload.get("next_cursor")
        if not cursor:
            break
    return pages


def _plain_title(prop: dict) -> str:
    chunks = prop.get("title") or []
    return "".join(part.get("plain_text") or "" for part in chunks).strip()


def page_title(page: dict) -> str:
    props = page.get("properties") or {}
    title_prop = props.get("タイトル")
    if title_prop and title_prop.get("type") == "title":
        return _plain_title(title_prop)
    for prop in props.values():
        if prop.get("type") == "title":
            return _plain_title(prop)
    return ""


def page_status(page: dict) -> Optional[str]:
    select = (page.get("properties") or {}).get("ステータス") or {}
    value = select.get("select")
    if not value:
        return None
    return value.get("name")


def page_publish_date(page: dict) -> Optional[str]:
    date_prop = (page.get("properties") or {}).get("公開予定日") or {}
    value = date_prop.get("date")
    if not value:
        return None
    start = value.get("start")
    if not start:
        return None
    return start[:10]


def select_target(pages: Iterable[dict]) -> Optional[dict]:
    items = list(pages)

    def dated(status: str) -> List[dict]:
        found = []
        for page in items:
            if page_status(page) != status:
                continue
            if page_publish_date(page):
                found.append(page)
        found.sort(key=lambda p: (page_publish_date(p) or "", p.get("last_edited_time") or ""))
        return found

    writing = dated("執筆中")
    if writing:
        return writing[0]
    ideas = dated("ネタ")
    if ideas:
        return ideas[0]

    undated = [p for p in items if page_status(p) in WRITING_STATUSES]
    if not undated:
        return None
    undated.sort(key=lambda p: p.get("last_edited_time") or "", reverse=True)
    return undated[0]


def other_page_titles(pages: Iterable[dict], exclude_id: str) -> List[str]:
    titles = []
    for page in pages:
        if page.get("id") == exclude_id:
            continue
        title = page_title(page)
        if title:
            titles.append(title)
    return titles


def fetch_block_children(token: str, block_id: str) -> List[dict]:
    blocks: List[dict] = []
    cursor: Optional[str] = None
    while True:
        query = {"page_size": "100"}
        if cursor:
            query["start_cursor"] = cursor
        payload = notion_request(token, "GET", f"/blocks/{block_id}/children", query=query)
        blocks.extend(payload.get("results") or [])
        if not payload.get("has_more"):
            break
        cursor = payload.get("next_cursor")
        if not cursor:
            break
    return blocks


def fetch_all_blocks(token: str, block_id: str) -> List[dict]:
    blocks: List[dict] = []
    for block in fetch_block_children(token, block_id):
        blocks.append(block)
        if block.get("has_children"):
            blocks.extend(fetch_all_blocks(token, block["id"]))
    return blocks


def _rich_text(block: dict) -> str:
    btype = block.get("type")
    payload = block.get(btype) or {}
    chunks = payload.get("rich_text") or payload.get("text") or []
    return "".join(part.get("plain_text") or "" for part in chunks)


def blocks_to_text(blocks: Iterable[dict]) -> str:
    lines = []
    for block in blocks:
        btype = block.get("type")
        text = _rich_text(block).strip()
        if not text:
            continue
        if btype in ("heading_1", "heading_2", "heading_3"):
            hashes = {"heading_1": "#", "heading_2": "##", "heading_3": "###"}[btype]
            lines.append(f"{hashes} {text}")
        elif btype in ("bulleted_list_item", "numbered_list_item", "to_do"):
            lines.append(f"- {text}")
        else:
            lines.append(text)
    return "\n".join(lines)


def build_codex_input(
    title: str,
    status: Optional[str],
    publish_date: Optional[str],
    body: str,
    other_titles: List[str],
) -> str:
    others = "\n".join(f"- {name}" for name in other_titles) or "（なし）"
    return (
        f"タイトル: {title}\n"
        f"ステータス: {status or '（なし）'}\n"
        f"公開予定日: {publish_date or '（なし）'}\n\n"
        f"## 本文\n{body or '（本文なし）'}\n\n"
        f"## 他ページのタイトル\n{others}\n"
    )


def ensure_codex_path() -> None:
    parts = [p for p in os.environ.get("PATH", "").split(":") if p]
    for extra in reversed(PATH_EXTRAS):
        if extra not in parts:
            parts.insert(0, extra)
    os.environ["PATH"] = ":".join(parts)


def extract_codex_result(stdout: str) -> str:
    marker = "tokens used"
    idx = stdout.find(marker)
    if idx == -1:
        raise ReminderError("codex 出力に tokens used が無い")
    rest = stdout[idx + len(marker) :].lstrip("\n")
    lines = rest.splitlines()
    if lines and re.match(r"^[0-9,]+$", lines[0].strip()):
        lines = lines[1:]
    text = "\n".join(lines).strip()
    if not text:
        raise ReminderError("codex 出力の tokens used 以降が空")
    return text


def run_codex(prompt: str, stdin_text: str, codex_bin: str = CODEX_BIN) -> str:
    ensure_codex_path()
    binary = codex_bin if Path(codex_bin).exists() else "codex"
    with tempfile.NamedTemporaryFile(prefix="writing-reminder-", suffix=".txt", delete=False) as tmp:
        out_path = Path(tmp.name)
    cmd = [
        binary,
        "exec",
        "--skip-git-repo-check",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "-c",
        'approval_policy="never"',
        "-m",
        "gpt-5.6-terra",
        "-c",
        'model_reasoning_effort="medium"',
        "-o",
        str(out_path),
        prompt,
    ]
    try:
        proc = subprocess.run(
            cmd,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=CODEX_TIMEOUT_SEC,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ReminderError(f"codex が {CODEX_TIMEOUT_SEC} 秒でタイムアウト") from exc
    combined = f"{proc.stdout or ''}\n{proc.stderr or ''}"
    if proc.returncode != 0:
        err = combined.strip()[:800]
        raise ReminderError(f"codex が失敗 (exit {proc.returncode}): {err}")
    last = out_path.read_text(encoding="utf-8").strip() if out_path.exists() else ""
    if last and "サンドボックス制約" not in last:
        return last
    try:
        return extract_codex_result(combined)
    except ReminderError as exc:
        snippet = combined.strip()[-800:]
        raise ReminderError(f"{exc} / last={last[:200]!r} / tail={snippet}") from exc


def parse_sections(output: str) -> Dict[str, str]:
    positions = []
    for key in SECTION_KEYS:
        pattern = rf"^##\s*{re.escape(key)}\s*$"
        match = re.search(pattern, output, flags=re.MULTILINE)
        if not match:
            raise ReminderError(f"codex 出力に ## {key} が無い")
        positions.append((match.start(), match.end(), key))
    positions.sort()
    sections: Dict[str, str] = {}
    for i, (_, end, key) in enumerate(positions):
        stop = positions[i + 1][0] if i + 1 < len(positions) else len(output)
        sections[key] = output[end:stop].strip()
    missing = [key for key in SECTION_KEYS if key not in sections]
    if missing:
        raise ReminderError(f"セクション不足: {missing}")
    return sections


def _rich_text_item(content: str) -> dict:
    return {"type": "text", "text": {"content": content[:2000]}}


def _paragraph(content: str) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [_rich_text_item(content)]},
    }


def _bullet(content: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [_rich_text_item(content)]},
    }


def _heading3(content: str) -> dict:
    return {
        "object": "block",
        "type": "heading_3",
        "heading_3": {"rich_text": [_rich_text_item(content)]},
    }


def _heading2(content: str) -> dict:
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": [_rich_text_item(content)]},
    }


def _lines_to_blocks(text: str) -> List[dict]:
    blocks = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(("- ", "* ", "・")):
            blocks.append(_bullet(re.sub(r"^[-*・]\s*", "", line)))
        else:
            blocks.append(_paragraph(line))
    if not blocks:
        blocks.append(_paragraph("（なし）"))
    return blocks


def sections_to_blocks(sections: Dict[str, str], date_str: str) -> List[dict]:
    children: List[dict] = [_heading2(f"執筆メモ（{date_str}）")]
    for key in SECTION_KEYS:
        children.append(_heading3(key))
        children.extend(_lines_to_blocks(sections.get(key) or ""))
    return children


def heading2_text(block: dict) -> str:
    if block.get("type") != "heading_2":
        return ""
    return _rich_text(block).strip()


def find_same_day_block_ids(blocks: Iterable[dict], date_str: str) -> List[str]:
    heading = f"執筆メモ（{date_str}）"
    collecting = False
    ids: List[str] = []
    for block in blocks:
        if not collecting:
            if heading2_text(block) == heading:
                collecting = True
                ids.append(block["id"])
            continue
        if block.get("type") == "heading_2":
            break
        ids.append(block["id"])
    return ids


def delete_blocks(token: str, block_ids: List[str], sleep_sec: float = DELETE_INTERVAL_SEC) -> None:
    for block_id in block_ids:
        notion_request(token, "DELETE", f"/blocks/{block_id}")
        time.sleep(sleep_sec)


def append_blocks(token: str, page_id: str, children: List[dict]) -> None:
    notion_request(token, "PATCH", f"/blocks/{page_id}/children", body={"children": children})


def format_preview(title: str, page_id: str, sections: Dict[str, str], date_str: str) -> str:
    parts = [f"対象: {title} ({page_id})", f"見出し: 執筆メモ（{date_str}）", ""]
    for key in SECTION_KEYS:
        parts.append(f"## {key}")
        parts.append(sections.get(key) or "")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def run(dry_run: bool = False) -> int:
    date_str = today_jst()
    title = ""
    try:
        token = read_notion_token()
        pages = query_all_pages(token)
        target = select_target(pages)
        if target is None:
            append_log("対象なし。Notion には書かず終了")
            print("対象なし", file=sys.stderr)
            return 0
        title = page_title(target)
        page_id = target["id"]
        top_level = fetch_block_children(token, page_id)
        nested: List[dict] = []
        for block in top_level:
            if block.get("has_children"):
                nested.extend(fetch_all_blocks(token, block["id"]))
        body = blocks_to_text(top_level + nested)
        payload = build_codex_input(
            title=title,
            status=page_status(target),
            publish_date=page_publish_date(target),
            body=body,
            other_titles=other_page_titles(pages, page_id),
        )
        prompt = PROMPT_PATH.read_text(encoding="utf-8")
        raw = run_codex(prompt, payload)
        sections = parse_sections(raw)
        preview = format_preview(title, page_id, sections, date_str)
        if dry_run:
            print(preview)
            append_log(f"dry-run 成功: {title}")
            return 0
        stale = find_same_day_block_ids(top_level, date_str)
        if stale:
            delete_blocks(token, stale)
        append_blocks(token, page_id, sections_to_blocks(sections, date_str))
        append_log(f"成功: {title}")
        print(preview)
        return 0
    except Exception as exc:
        append_log(f"失敗: {title or '-'} {exc}")
        print(f"失敗: {exc}", file=sys.stderr)
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="執筆リマインダー")
    parser.add_argument("--dry-run", action="store_true", help="Notion に書かず標準出力へ出す")
    args = parser.parse_args(argv)
    return run(dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
