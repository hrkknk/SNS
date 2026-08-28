# 執筆リマインダー（GPT版）tasks

1タスク2〜5分、1〜2ファイルに収まる粒度で分解する。親は Cursor。実装は Auto 直
（グローバル開発ハーネスは使わない）。レビューが必要なら `codex-review impl`。
本文・校正には関与しない。

## Phase 1: 材料を用意する

- [x] T1. `~/SNS/shippitsu_memo_prompt.md` を作る。gpt-5.6-terra に渡すプロンプト本体。
      4項目の指示と、本文を書かせない禁止事項を含む。（requirements R3, R5 / design「gpt-5.6-terra への入力」）
- [x] T2. `~/SNS/writing_reminder.py` に、`.zshrc` から `NOTION_TOKEN` を取り出す関数と、
      ログ追記の関数を書く。単体で実行して両方が動くことを確認。（R6 / design「ファイル配置」）

## Phase 2: Notion 読み取り

- [x] T3. コンテンツDB を全件クエリし、R2 の優先順で対象1件を選ぶ関数。
      「執筆中」なし・「ネタ」なし・公開予定日なしの各ケースをテストで固める。（R2）
- [x] T4. 対象ページの全ブロックを取得する関数（`has_more` の続きも取る）。（design「Notion アクセス」）
- [x] T5. 同DBの他ページのタイトル一覧を取り出す関数。（design「gpt-5.6-terra への入力」3）

## Phase 3: codex 連携

- [x] T6. 入力テキスト（タイトル・ステータス・公開予定日・本文・他タイトル一覧）を組み立てる関数。（R3）
- [x] T7. codex を subprocess で呼び、`tokens used` 以降を最終結果として取り出す関数。
      タイムアウト300秒、失敗時は例外。（design「codex 呼び出し」）
- [x] T8. 出力を4セクションにパースする関数。4つ揃わなければ例外。（R7 / design「出力の受け取り」）

## Phase 4: Notion 書き込み

- [x] T9. パース結果を Notion ブロック配列に変換する関数。（R4）
- [x] T10. 同日の「執筆メモ（YYYY-MM-DD）」見出しがあれば、その配下を削除する関数。
      削除は 0.4 秒間隔。（design「同日見出しの差し替え」）
- [x] T11. ページ末尾に追記する関数。書き込みは最後の1回だけ。（R4, R7）

## Phase 5: 組み立てと運用

- [x] T12. main を書く。各段階の失敗をログに落として終了する（R7）。
      `--dry-run` を付けたら Notion に書かず標準出力に出すだけにする。
- [x] T13. `--dry-run` で実行し、実際の Notion データに対して期待通りの出力になることを確認。
- [x] T14. `~/Library/LaunchAgents/com.hiroki.writing-reminder.plist` を作り、`launchctl load` する。
      火・木・土 21:00、`StartCalendarInterval` 3件。（R1 / design「スケジュール」）
- [x] T15. `launchctl kickstart` で即時実行し、Notion への追記とログ出力を確認する。
      2026-08-27「ファミレスでお祈り」末尾に `執筆メモ（2026-08-27）` を追記済み。
- [x] T16. クラウドルーチン `trig_01HZrSE1UXJHVsdUDfncxNiq` を `enabled: false` にする。（design 末尾）
      本人が claude.ai で無効化済み。
