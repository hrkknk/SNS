#!/usr/bin/env python3
"""journal_append の単体テスト（Notion には繋がない）。"""

from __future__ import annotations

import unittest
from unittest import mock

import journal_append as ja


class JournalAppendTests(unittest.TestCase):
    def test_empty_text_does_not_touch_notion(self) -> None:
        with mock.patch.object(ja, "notion_request") as req:
            with self.assertRaises(ja.JournalError):
                ja.append_journal("   ", token="tok")
            req.assert_not_called()

    def test_create_only(self) -> None:
        with mock.patch.object(ja, "create_page", return_value="page-new") as create:
            result = ja.append_journal("今日のメモ", token="tok")
        self.assertEqual(result, {"action": "create", "page_id": "page-new"})
        create.assert_called_once_with("tok", "今日のメモ")

    def test_title_from_body_truncates(self) -> None:
        long_line = "あ" * 120
        title = ja.title_from_body(long_line + "\n続き")
        self.assertEqual(len(title), ja.MAX_TITLE)
        self.assertTrue(title.endswith("…"))


if __name__ == "__main__":
    unittest.main()
