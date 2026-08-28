#!/usr/bin/env python3
"""Block Write/StrReplace on drafts/**/draft_v*.md and body_v*.md."""
from __future__ import annotations

import json
import os
import re
import sys

PROTECTED_NAME = re.compile(r"^(draft_v|body_v).+\.md$", re.IGNORECASE)


def extract_path(payload: dict) -> str:
    tool_input = payload.get("tool_input") or payload.get("input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}
    raw = (
        tool_input.get("path")
        or tool_input.get("file_path")
        or payload.get("path")
        or payload.get("file_path")
        or ""
    )
    return str(raw).replace("\\", "/")


def is_protected(path: str) -> bool:
    if not path:
        return False
    normalized = path if path.startswith("/") else f"/{path}"
    if "/drafts/" not in normalized and not path.startswith("drafts/"):
        return False
    return bool(PROTECTED_NAME.match(os.path.basename(path)))


def main() -> None:
    payload = json.load(sys.stdin)
    path = extract_path(payload)
    if is_protected(path):
        json.dump(
            {
                "permission": "deny",
                "user_message": "本人の原稿です。直接書き換えず、指摘のみ行ってください。校正は kousei スキルで。",
                "agent_message": "drafts 配下の draft_v*.md / body_v*.md は直接編集できません。指摘のみ。校正は kousei。",
            },
            sys.stdout,
        )
        return
    json.dump({"permission": "allow"}, sys.stdout)


if __name__ == "__main__":
    main()
