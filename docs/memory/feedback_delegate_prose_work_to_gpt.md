---
name: feedback-delegate-prose-work-to-gpt
description: 文章の校正・アドバイスは自分でやらず、codex CLI（gpt-5.6-terra）に委譲する
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9fcd7fe9-ba31-4336-9e9c-26e090665021
  modified: 2026-08-04T20:28:50.969Z
---

記事など本人の文章に関する**校正・言い回しの助言・講評は、親 Agent（Cursor Auto）が自分でやらない**。codex CLI 経由で gpt-5.6-terra（reasoning medium）に投げ、結果をそのまま本人に渡す。親の担当は、原稿の取得（Notion API / MCP）、codex への受け渡し、本人が採用すると決めた分だけの反映、検証。

**Why:** 2026-08-05、note1本目の校正で書き口を勝手に書き換えて叱責され（→[feedback_never_rewrite_users_prose.md](feedback_never_rewrite_users_prose.md)）、本人から「たぶん君よりGPTの方が自然言語に強い。今後は文章に関するアドバイスや校正はGPTに委譲して」と指示された。実際に同じ原稿を GPT に投げたところ、本文に手を付けず指摘だけで返し、こちらが見落としていた点（「自らの工夫でもって」の「自ら」が誰を指すか／「最大の価値がそれ」の「それ」の曖昧さ）も拾った。断定を弱めろとは言わなかった。

**How to apply:**

```bash
cat 原稿.txt | codex exec --skip-git-repo-check --sandbox read-only \
  -c approval_policy="never" -m gpt-5.6-terra \
  -c model_reasoning_effort="medium" "$(cat ~/SNS/kousei_prompt.md)"
```

- プロンプトのテンプレートは `~/SNS/kousei_prompt.md`。
- `--sandbox read-only` と `approval_policy="never"` は必須。外すと承認待ちで固まる。原稿はファイル読み取りをさせず stdin で渡す。
- 文章まわりは Cursor の Task サブエージェントではなく、codex CLI 固定（Terra が Task に無いため）。

**執筆リマインダー:** ツール実装（launchd + Python + Notion API）は Cursor Auto 直。材料の文章生成は Terra。クラウドルーチンの是非を蒸し返して再提案しない。

関連: [feedback_never_rewrite_users_prose.md](feedback_never_rewrite_users_prose.md) / [project_sns_phase_status.md](project_sns_phase_status.md)
