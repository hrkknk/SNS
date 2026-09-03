#!/usr/bin/env python3
"""journal_append の単体テスト（Notion には繋がない）。"""

from __future__ import annotations

import unittest
from datetime import datetime
from unittest import mock

import journal_append as ja


class JournalAppendTests(unittest.TestCase):
    def test_today_jst(self) -> None:
        stamp = datetime(2026, 9, 3, 20, 0, tzinfo=ja.JST)
        self.assertEqual(ja.today_jst(stamp), "2026-09-03")

    def test_empty_text_does_not_touch_notion(self) -> None:
        with mock.patch.object(ja, "notion_request") as req:
            with self.assertRaises(ja.JournalError):
                ja.append_journal("   ", token="tok")
            req.assert_not_called()

    def test_create_when_missing(self) -> None:
        with mock.patch.object(ja, "find_page_by_title", return_value=None):
            with mock.patch.object(ja, "create_today_page", return_value="page-new") as create:
                with mock.patch.object(ja, "append_entry") as append:
                    result = ja.append_journal(
                        "今日のメモ",
                        token="tok",
                        day="2026-09-03",
                        now=datetime(2026, 9, 3, 21, 0, tzinfo=ja.JST),
                    )
        self.assertEqual(result["action"], "create")
        self.assertEqual(result["page_id"], "page-new")
        create.assert_called_once()
        append.assert_not_called()

    def test_append_when_exists(self) -> None:
        with mock.patch.object(ja, "find_page_by_title", return_value="page-old"):
            with mock.patch.object(ja, "create_today_page") as create:
                with mock.patch.object(ja, "append_entry") as append:
                    result = ja.append_journal(
                        "追記",
                        token="tok",
                        day="2026-09-03",
                        now=datetime(2026, 9, 3, 22, 0, tzinfo=ja.JST),
                    )
        self.assertEqual(result["action"], "append")
        self.assertEqual(result["page_id"], "page-old")
        create.assert_not_called()
        append.assert_called_once()

    def test_paragraph_blocks_chunk(self) -> None:
        blocks = ja.paragraph_blocks("a" * 2005, heading="21:00")
        self.assertEqual(blocks[0]["paragraph"]["rich_text"][0]["text"]["content"], "21:00")
        self.assertEqual(len(blocks), 3)


if __name__ == "__main__":
    unittest.main()
