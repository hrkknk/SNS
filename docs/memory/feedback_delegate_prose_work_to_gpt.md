---
name: feedback-delegate-prose-work-to-gpt
description: 文章の校正・アドバイスは自分でやらず、Cursor の Task で GPT 5.6 sol をモデル指定して委譲する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9fcd7fe9-ba31-4336-9e9c-26e090665021
  modified: 2026-08-29T10:02:00.000Z
---

記事など本人の文章に関する**校正・言い回しの助言・講評は、親 Agent（Cursor Auto）が自分でやらない**。Cursor の Task に GPT 5.6 sol をモデル指定して投げ、結果をそのまま本人に渡す。親の担当は、原稿の取得（Notion API / MCP）、GPT への受け渡し、本人が採用すると決めた分だけの反映、検証。

**Why:** 2026-08-05、note1本目の校正で書き口を勝手に書き換えて叱責され（→[feedback_never_rewrite_users_prose.md](feedback_never_rewrite_users_prose.md)）、本人から「たぶん君よりGPTの方が自然言語に強い。今後は文章に関するアドバイスや校正はGPTに委譲して」と指示された。実際に同じ原稿を GPT に投げたところ、本文に手を付けず指摘だけで返し、こちらが見落としていた点（「自らの工夫でもって」の「自ら」が誰を指すか／「最大の価値がそれ」の「それ」の曖昧さ）も拾った。断定を弱めろとは言わなかった。

2026-08-29、Cloud Agent で `codex exec` 直叩き＋`OPENAI_API_KEY` を要求したところ、本人から「GPTは直接使うのではなく、Cursorのモデル指定で呼び出す」と訂正された。Cloud / Cursor Auto の文章作業は Cursor 側の認証で呼ぶ。OpenAI API を直叩きしない。

**How to apply:**

- Cloud / Cursor Auto: Task に GPT 5.6 sol をモデル指定し、`kousei_prompt.md` と原稿全文を渡す。
- プロンプトのテンプレートは `kousei_prompt.md`。
- `codex exec` や `OPENAI_API_KEY` は使わない。
- 例外: ローカル Mac の `writing_reminder.py`（launchd）は別系統で、当面 `codex exec` のまま。Cloud Agent の文章作業には使わない。

**執筆リマインダー:** ツール実装（launchd + Python + Notion API）は Cursor Auto 直。材料の文章生成は GPT。クラウドルーチンの是非を蒸し返して再提案しない。

関連: [feedback_never_rewrite_users_prose.md](feedback_never_rewrite_users_prose.md) / [project_sns_phase_status.md](project_sns_phase_status.md)
