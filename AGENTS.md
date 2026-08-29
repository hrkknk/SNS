# SNS（発信・執筆）

対話窓口は **Cursor**。本文・校正・講評は親 Agent が自分でやらない。
このリポに `CLAUDE.md` は置かない。

## グローバル開発ハーネスは適用しない

マシン既定の SDD / TDD / `implementer` / `sol-reviewer` / `.cursor/design-approved` は、このリポでは無効。
例外は `specs/writing-reminder/` のような **ツール実装** だけ。その場合も設計承認マーカーや implementer は使わず、Cursor Auto が直実装する。このリポは git ではない。

## 役割

| 工程 | 担当 |
|---|---|
| 対話窓口、進行、ファイル受け渡し、Notion 反映、捏造チェック | Cursor Auto |
| 1問1答のブレスト相手 | GPT 5.6 sol（Cursor の Task でモデル指定） |
| 下書き本文 | GPT 5.6 sol（同上） |
| 校正・講評 | GPT 5.6 sol（`kousei_prompt.md`） |
| writing-reminder などのツール実装 | Auto 直 |

親の Auto は質問の発明・本文・校正を自分でやらない。ブレストはユーザーの返答を GPT に渡し、次の1問だけ出させる。

## フロー

1問1答 → `brief.md` → GPT に執筆委譲 → `/kousei`

直してよいのは誤字・表記のみ。言い回し・断定の強さ・語尾は触らない。
`drafts/**/draft_v*.md` と `drafts/**/body_v*.md` は直接書き換えない（指摘のみ。校正は kousei）。

## GPT の呼び出し（Cloud / Cursor Auto）

文章まわりは **Cursor の Task に GPT 5.6 sol をモデル指定して**呼ぶ。`codex exec` や `OPENAI_API_KEY` で OpenAI を直叩きしない。Cursor 側の認証で呼ぶ。

- ブレスト: 材料（`input.txt` と直前の返答）を Task に渡し、次の1問だけ返させる
- 執筆: `brief.md` と文体見本を Task に渡し、結果を `gpt_draft_raw.txt` に保存する
- 校正: `kousei_prompt.md` と原稿を Task に渡し、出力をそのまま本人に見せる

例外: ローカル Mac の `writing_reminder.py`（launchd）は別系統で、当面 `codex exec` のまま。Cloud Agent の文章作業には使わない。

スキルの正本は `.cursor/skills/`（`note-draft` / `kousei`）。`.claude/skills/` はポインタのみ。
Notion はプロジェクトのプラグイン（`.cursor/settings.json` の `notion-workspace`）を使う。
アカウント全体の MCP には足さない。未接続なら API 直叩き。
スマホのネタ投稿ショートカットは Notion REST API 直叩きなので、Cursor / Claude の有無に依存しない。
`~/.claude/` は残してよい。並行で足しただけ。

## 教訓・世界観

Cursor は `~/.claude/projects/.../memory/` を読まない。リポ内の索引は [docs/memory/MEMORY.md](docs/memory/MEMORY.md)。
少なくとも次を前提にする。

- 本文を書き換えない → `docs/memory/feedback_never_rewrite_users_prose.md`
- 校正・講評は GPT → `docs/memory/feedback_delegate_prose_work_to_gpt.md`
- 1問1答→ブリーフ→委譲 → `docs/memory/project_note_drafting_workflow.md`
- Notion / Buffer の ID → `docs/memory/project_sns_infra_ids.md`
- 思想発信が起点。布教アカウント化は禁止 → `docs/memory/project_coffee_worldview_pivot.md`
