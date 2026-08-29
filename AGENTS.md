# SNS（発信・執筆）

対話窓口は **Cursor Auto**。本文・校正・講評は親 Agent が自分でやらない。
このリポに `CLAUDE.md` は置かない。

## グローバル開発ハーネスは適用しない

マシン既定の SDD / TDD / `implementer` / `sol-reviewer` / `.cursor/design-approved` は、このリポでは無効。
例外は `specs/writing-reminder/` のような **ツール実装** だけ。その場合も設計承認マーカーや implementer は使わず、Cursor Auto が直実装する。このリポは git ではない。

## 役割

| 工程 | 担当 |
|---|---|
| 対話窓口、進行、ファイル受け渡し、Notion 反映、捏造チェック | Cursor Auto |
| 1問1答のブレスト相手 | Cursor の GPT（Task / `gpt-5.6-luna-high`） |
| 下書き本文 | 同上 |
| 校正・講評 | 同上（`kousei_prompt.md`） |
| writing-reminder などのツール実装 | Auto 直 |

親の Auto は質問の発明・本文・校正を自分でやらない。ブレストはユーザーの返答を GPT に渡し、次の1問だけ出させる。
OpenAI の Codex CLI（`codex exec`）と API キーは使わない。文章は Cursor が用意する GPT に委譲する。

## フロー

1問1答 → `brief.md` → GPT に執筆委譲 → `/kousei`

直してよいのは誤字・表記のみ。言い回し・断定の強さ・語尾は触らない。
`drafts/**/draft_v*.md` と `drafts/**/body_v*.md` は直接書き換えない（指摘のみ。校正は kousei）。

## GPT の呼び出し

Cursor の **Task** ツールで切る。親の会話モデルが GPT でも、本文・校正・次の1問は Task 側に渡す（窓口役が本文を混ぜないため）。

- `subagent_type`: `generalPurpose`
- `model`: `gpt-5.6-luna-high`（Task の GPT は luna-high / sol-high / sol-xhigh 系のみ。terra と medium は無い）
- 必要な原稿・ブリーフ・`kousei_prompt.md` はプロンプトに本文ごと渡す
- 返ってきた文章は要約・言い換えせず、そのまま本人に見せる
- Task にも `draft_v*.md` / `body_v*.md` を書き換えさせない

スキルの正本は `.cursor/skills/`（`note-draft` / `kousei`）。`.claude/skills/` はポインタのみ。
Notion はプロジェクトのプラグイン（`.cursor/settings.json` の `notion-workspace`）を使う。
アカウント全体の MCP には足さない。未接続なら API 直叩き（Cloud Agent では `$NOTION_TOKEN`）。
スマホのネタ投稿ショートカットは Notion REST API 直叩きなので、Cursor / Claude の有無に依存しない。
`~/.claude/` は残してよい。並行で足しただけ。

## Cursor Cloud

リモートの Cloud Agent で動かすとき:

- Install Script は空でよい（codex を入れない）
- Secrets は `NOTION_TOKEN`（任意で `BUFFER_ACCESS_TOKEN`）。Codex / OpenAI の API キーは不要
- 文章作業は上と同じ Task（`gpt-5.6-luna-high`）
- Mac の launchd 執筆リマインダーは Codex 前提のままなので、Cloud Agent では動かない

## 教訓・世界観

Cursor は `~/.claude/projects/.../memory/` を読まない。リポ内の索引は [docs/memory/MEMORY.md](docs/memory/MEMORY.md)。
少なくとも次を前提にする。

- 本文を書き換えない → `docs/memory/feedback_never_rewrite_users_prose.md`
- 校正・講評は Cursor の GPT → `docs/memory/feedback_delegate_prose_work_to_gpt.md`
- 1問1答→ブリーフ→委譲 → `docs/memory/project_note_drafting_workflow.md`
- Notion / Buffer の ID → `docs/memory/project_sns_infra_ids.md`
- 思想発信が起点。布教アカウント化は禁止 → `docs/memory/project_coffee_worldview_pivot.md`
