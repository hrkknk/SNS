# 執筆リマインダー（GPT版）design

## 全体構成

```
launchd (com.hiroki.writing-reminder)
   └─ 火・木・土 21:00 に起動
        └─ ~/SNS/writing_reminder.py
             ├─ 1. Notion: 対象記事を1件選ぶ            (R2)
             ├─ 2. Notion: 対象ページの本文＋他ページのタイトル一覧を取得
             ├─ 3. codex exec -m gpt-5.6-terra に投げる  (R3)
             ├─ 4. 出力をパースして Notion に追記        (R4)
             └─ 5. ログ追記                              (R6)
```

Claude はこの経路に一切登場しない。

## ファイル配置

| パス | 役割 |
|---|---|
| `~/SNS/writing_reminder.py` | 本体 |
| `~/SNS/shippitsu_memo_prompt.md` | gpt-5.6-terra に渡すプロンプト |
| `~/SNS/logs/writing-reminder.log` | 実行ログ |
| `~/Library/LaunchAgents/com.hiroki.writing-reminder.plist` | スケジュール定義 |

## スケジュール（launchd）

`StartCalendarInterval` に3件（Weekday 2/4/6 = 火・木・土、Hour 21, Minute 0）を配列で指定する。
cron ではなく launchd を使う理由は、**実行時刻を逃した場合に次回起動時に走る**ため（R1）。

環境変数 `NOTION_TOKEN` は launchd に継承されないので、plist の `EnvironmentVariables` には書かず、
スクリプト側で `~/.zshrc` から読む（`zsh -lc 'echo $NOTION_TOKEN'` ではなく、
`.zshrc` を正規表現で走査してトークンだけ取り出す。oh-my-zsh の読み込みエラーを踏まないため）。

## Notion アクセス

- 対象選択: `POST /v1/data_sources/{ds}/query`（Notion-Version: `2025-09-03`）
  - ステータスは `select` 型、公開予定日は `date` 型、タイトルは `title` 型。
  - フィルタは API 側で書かず、全件取得してスクリプト内で選ぶ（件数が20件未満のため）。
- 本文取得: `GET /v1/blocks/{page_id}/children?page_size=100`（`has_more` の続きも取る）
- 追記: `PATCH /v1/blocks/{page_id}/children`
- 同日見出しの差し替え: 「執筆メモ（YYYY-MM-DD）」の heading_2 を探し、
  見つかったらその見出しから次の heading_2 直前までを `DELETE /v1/blocks/{id}` してから追記する。
  削除は 0.4 秒間隔で行う（連続削除で `Invalid ancestor path` 400 を踏んだ実績あり）。

## codex 呼び出し

```bash
codex exec --skip-git-repo-check --sandbox read-only \
  -c approval_policy="never" -m gpt-5.6-terra \
  -c model_reasoning_effort="medium" "$(cat ~/SNS/shippitsu_memo_prompt.md)"
```

- 原稿は **stdin** で渡す（ファイルを読ませると承認待ちで固まる）。
- `--sandbox read-only` と `approval_policy="never"` は必須。付けないと 5 分待っても返らない。
- `--ephemeral` と `-o`（最終メッセージのファイル出力）を併用する。read-only だとセッション書き込みで落ちることがある。
- 標準エラーに `tokens used` が出る。`-o` が空のときは結合出力の `tokens used` 行より後ろを最終結果として採用する。
- タイムアウトは 300 秒。超えたら失敗扱い（R7）。

## gpt-5.6-terra への入力

1. 対象記事のタイトル・ステータス・公開予定日
2. 対象ページの本文全文
3. 同DBの他ページのタイトル一覧（関連ネタを選ばせるため）

## 出力の受け取り

gpt-5.6-terra には見出し付きの決まった書式で返させ、スクリプト側は
`## 問い` `## 骨組み` `## 関連するネタ` `## 詰まりそうな点` の4セクションに分割して
Notion のブロック（heading_2 + paragraph + bulleted_list_item）に変換する。
4セクションが揃わなかった場合は失敗扱いとし、Notion には書かない（R7）。

## エラー処理（R7）

Notion への書き込みは処理の最後に1回だけ行う。それ以前の段階（対象選択・本文取得・codex 実行・
出力パース）で失敗した場合は、ログに理由を残して終了する。書き込み自体が途中で失敗した場合は、
その旨をログに明記する（ロールバックはしない）。

## 既存クラウドルーチンの扱い

`trig_01HZrSE1UXJHVsdUDfncxNiq` を `enabled: false` に更新する。
削除は API では不可なので、不要なら claude.ai/code/routines から本人が消す。
