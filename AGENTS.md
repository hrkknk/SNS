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
| 1問1答のブレスト相手 | gpt-5.6-terra medium（codex exec） |
| 下書き本文 | gpt-5.6-terra medium |
| 校正・講評 | gpt-5.6-terra medium（`kousei_prompt.md`） |
| writing-reminder などのツール実装 | Auto 直 |

親の Auto は質問の発明・本文・校正を自分でやらない。ブレストはユーザーの返答を Terra に渡し、次の1問だけ出させる。

## フロー

1問1答 → `brief.md` → Terra に執筆委譲 → `/kousei`

直してよいのは誤字・表記のみ。言い回し・断定の強さ・語尾は触らない。
`drafts/**/draft_v*.md` と `drafts/**/body_v*.md` は直接書き換えない（指摘のみ。校正は kousei）。

## Terra の呼び出し

```bash
codex exec --skip-git-repo-check --sandbox read-only \
  -c approval_policy="never" -m gpt-5.6-terra \
  -c model_reasoning_effort="medium" "..."
```

`--sandbox read-only` と `approval_policy="never"` は必須。原稿は stdin で渡す。
Cursor の Task サブエージェントに Terra は無い。文章まわりは codex CLI 固定。

スキルの正本は `.cursor/skills/`（`note-draft` / `kousei`）。`.claude/skills/` はポインタのみ。
Notion はプロジェクトのプラグイン（`.cursor/settings.json` の `notion-workspace`）を使う。
アカウント全体の MCP には足さない。未接続なら API 直叩き。
スマホのネタ投稿ショートカットは Notion REST API 直叩きなので、Cursor / Claude の有無に依存しない。
`~/.claude/` は残してよい。並行で足しただけ。

## 教訓・世界観

Cursor は `~/.claude/projects/.../memory/` を読まない。リポ内の索引は [docs/memory/MEMORY.md](docs/memory/MEMORY.md)。
少なくとも次を前提にする。

- 本文を書き換えない → `docs/memory/feedback_never_rewrite_users_prose.md`
- 校正・講評は Terra → `docs/memory/feedback_delegate_prose_work_to_gpt.md`
- 1問1答→ブリーフ→委譲 → `docs/memory/project_note_drafting_workflow.md`
- Notion / Buffer の ID → `docs/memory/project_sns_infra_ids.md`
- 思想発信が起点。布教アカウント化は禁止 → `docs/memory/project_coffee_worldview_pivot.md`
