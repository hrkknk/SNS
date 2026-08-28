#!/usr/bin/env python3
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import writing_reminder as wr


def page(title, status, date=None, edited="2026-08-01T00:00:00.000Z", pid="id-a"):
    status_value = {"name": status} if status else None
    date_value = {"start": date} if date else None
    return {
        "id": pid,
        "last_edited_time": edited,
        "properties": {
            "タイトル": {"type": "title", "title": [{"plain_text": title}]},
            "ステータス": {"type": "select", "select": status_value},
            "公開予定日": {"type": "date", "date": date_value},
        },
    }


class TokenAndLogTests(unittest.TestCase):
    def test_ensure_codex_path_prepends_node(self):
        old = os.environ.get("PATH")
        os.environ["PATH"] = "/usr/bin:/bin"
        try:
            wr.ensure_codex_path()
            path = os.environ["PATH"]
            self.assertTrue(path.startswith("/opt/homebrew/opt/node@22/bin"))
            self.assertIn("/opt/homebrew/bin", path)
        finally:
            if old is None:
                del os.environ["PATH"]
            else:
                os.environ["PATH"] = old

    def test_read_notion_token_from_zshrc(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".zshrc"
            path.write_text('export FOO=1\nexport NOTION_TOKEN="ntn_secret"\n', encoding="utf-8")
            self.assertEqual(wr.read_notion_token(path), "ntn_secret")

    def test_append_log_writes_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "writing-reminder.log"
            wr.append_log("hello", log_path=path, now=datetime(2026, 8, 27, 21, 0, tzinfo=wr.JST))
            text = path.read_text(encoding="utf-8")
            self.assertIn("hello", text)
            self.assertIn("2026-08-27", text)


class SelectTargetTests(unittest.TestCase):
    def test_prefers_dated_writing(self):
        pages = [
            page("idea", "ネタ", "2026-08-10", pid="1"),
            page("soon", "執筆中", "2026-08-28", pid="2"),
            page("later", "執筆中", "2026-09-01", pid="3"),
        ]
        self.assertEqual(wr.select_target(pages)["id"], "2")

    def test_no_writing_falls_back_to_dated_idea(self):
        pages = [
            page("old", "ネタ", "2026-09-01", pid="1"),
            page("near", "ネタ", "2026-08-29", pid="2"),
            page("done", "公開済み", "2026-08-20", pid="3"),
        ]
        self.assertEqual(wr.select_target(pages)["id"], "2")

    def test_no_dates_picks_last_edited_among_writing_or_idea(self):
        pages = [
            page("older", "執筆中", None, edited="2026-08-01T00:00:00.000Z", pid="1"),
            page("newer", "ネタ", None, edited="2026-08-20T00:00:00.000Z", pid="2"),
            page("published", "公開済み", None, edited="2026-08-25T00:00:00.000Z", pid="3"),
        ]
        self.assertEqual(wr.select_target(pages)["id"], "2")

    def test_empty_returns_none(self):
        self.assertIsNone(wr.select_target([]))

    def test_only_published_returns_none(self):
        pages = [page("done", "公開済み", "2026-08-01", pid="1")]
        self.assertIsNone(wr.select_target(pages))


class ParseAndBlocksTests(unittest.TestCase):
    SAMPLE = """前置きは無視
## 問い
問1
問2

## 骨組み
見出しA
補足A

## 関連するネタ
- 別ネタ：理由

## 詰まりそうな点
ここが詰まりそう
"""

    def test_parse_sections(self):
        sections = wr.parse_sections(self.SAMPLE)
        self.assertEqual(sections["問い"], "問1\n問2")
        self.assertIn("見出しA", sections["骨組み"])
        self.assertIn("別ネタ", sections["関連するネタ"])
        self.assertEqual(sections["詰まりそうな点"], "ここが詰まりそう")

    def test_parse_missing_section_raises(self):
        with self.assertRaises(wr.ReminderError):
            wr.parse_sections("## 問い\nだけ\n")

    def test_extract_codex_result_from_stderr_style(self):
        stdout = (
            "codex\nfirst\ncodex\n## 問い\nA\n\n## 骨組み\nB\n"
            "tokens used\n6,384\n## 問い\nA\n"
        )
        self.assertIn("## 問い", wr.extract_codex_result(stdout))

    def test_sections_to_blocks_starts_with_dated_heading(self):
        sections = wr.parse_sections(self.SAMPLE)
        blocks = wr.sections_to_blocks(sections, "2026-08-27")
        self.assertEqual(blocks[0]["type"], "heading_2")
        heading = blocks[0]["heading_2"]["rich_text"][0]["text"]["content"]
        self.assertEqual(heading, "執筆メモ（2026-08-27）")
        types = [b["type"] for b in blocks]
        self.assertIn("heading_3", types)
        self.assertIn("bulleted_list_item", types)

    def test_find_same_day_stops_at_next_heading2(self):
        blocks = [
            {"id": "keep", "type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "本人"}]}},
            {
                "id": "h",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"plain_text": "執筆メモ（2026-08-27）"}]},
            },
            {"id": "a", "type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "旧"}]}},
            {
                "id": "next",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"plain_text": "本文"}]},
            },
            {"id": "body", "type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "残す"}]}},
        ]
        self.assertEqual(wr.find_same_day_block_ids(blocks, "2026-08-27"), ["h", "a"])

    def test_other_page_titles_excludes_self(self):
        pages = [page("A", "ネタ", pid="1"), page("B", "執筆中", pid="2")]
        self.assertEqual(wr.other_page_titles(pages, "1"), ["B"])


if __name__ == "__main__":
    unittest.main()
