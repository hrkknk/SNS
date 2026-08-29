---
name: feedback-delegate-prose-work-to-gpt
description: 文章の校正・アドバイスは自分でやらず、Cursor の GPT（Task / gpt-5.6-sol-high）に委譲する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9fcd7fe9-ba31-4336-9e9c-26e090665021
  modified: 2026-08-28T05:50:00.000Z
---

記事など本人の文章に関する**校正・言い回しの助言・講評は、親 Agent（Cursor Auto）が自分でやらない**。Cursor の Task で gpt-5.6-sol-high に投げ、結果をそのまま本人に渡す。親の担当は、原稿の取得（Notion API / MCP）、GPT への受け渡し、本人が採用すると決めた分だけの反映、検証。

**Why:** 2026-08-05、note1本目の校正で書き口を勝手に書き換えて叱責され（→[feedback_never_rewrite_users_prose.md](feedback_never_rewrite_users_prose.md)）、本人から「たぶん君よりGPTの方が自然言語に強い。今後は文章に関するアドバイスや校正はGPTに委譲して」と指示された。実際に同じ原稿を GPT に投げたところ、本文に手を付けず指摘だけで返し、こちらが見落としていた点（「自らの工夫でもって」の「自ら」が誰を指すか／「最大の価値がそれ」の「それ」の曖昧さ）も拾った。断定を弱めろとは言わなかった。

当初の呼び出しは OpenAI の Codex CLI（`codex exec` / gpt-5.6-terra）だった。2026-08-28、本人が GPT を直接使うのをやめたため、**Cursor が用意する GPT**（Task / `gpt-5.6-sol-high`）に切り替えた。委譲する理由（親が本文を書かない）は変わらない。チャネルだけが変わった。

**How to apply:**

Cursor の Task ツールで切る。

- `subagent_type`: `generalPurpose`
- `model`: `gpt-5.6-sol-high`
- プロンプトのテンプレートはリポ直下の `kousei_prompt.md`。原稿全文とプロンプト本文を Task に渡す
- 返ってきた文章は要約・改変しない
- `codex exec` は使わない。API キーも不要

**執筆リマインダー:** ツール実装（Python + Notion API）は Cursor Auto 直。材料の文章生成は Cursor の GPT。Mac の launchd 経路は Codex CLI 前提のままなので、Codex を捨てたあとは動かない。クラウドルーチン（claude.ai）の是非を蒸し返して再提案しない。

関連: [feedback_never_rewrite_users_prose.md](feedback_never_rewrite_users_prose.md) / [project_sns_phase_status.md](project_sns_phase_status.md)
