---
name: project-journal-workflow
description: 日記DBでネタ断片と文体材料を蓄積する運用（確定後のみページ作成）
metadata:
  node_type: memory
  type: project
  modified: 2026-09-03T20:50:00.000Z
---

毎日のジャーナリングで投稿ネタの断片と文体の材料を積む。1日記＝1ネタではない。加工せず生ログを残し、使える断片だけ既存のネタ箱へ落とす。

**原則**
- 置き場は Notion「日記DB」一本（スマホもPCも同じ）
- 単位は **日付1ページ**（タイトル `YYYY-MM-DD`）。同日は追記
- **入力を確定するまでページを作らない**（誤タップ・途中離脱で空ページを残さない）
- ネタ化は手動。既存の「ネタ投稿」ショートカットでコンテンツDBへ
- note執筆時は、必要に応じて直近の日記を文体見本として Terra に渡す

**DB**（発信管理の下）
- database: `0bf755f4-eadf-4a0f-84e7-d67744d4ec82`
- data source: `9affd3bf-a3b7-474c-baf8-25c83ba3ef47`
- プロパティ: 名前（title）/ 日付（date）/ ネタ化済み（checkbox）
- URL: https://app.notion.com/p/0bf755f4eadf4a0f84e7d67744d4ec82

**PC**
```bash
source ~/.zshrc
python3 journal_append.py "本文"
# または
echo "本文" | python3 journal_append.py
```
空入力はエラーにして Notion を触らない。既存ページがあれば末尾に `HH:MM` 見出し＋本文を追記する。

**スマホ（Shortcuts「日記」）— 確定後のみ作成/追記**

アクション順:
1. **入力を要求**（テキスト）。キャンセルしたらここで終了。ページは作らない
2. **現在の日付** → フォーマット `yyyy-MM-dd`（デバイスのローカル＝JST想定）
3. **テキスト**（クエリ用JSON）。`equals` の値に日付変数を挟む:
   `{"filter":{"property":"名前","title":{"equals":"DATE"}},"page_size":1}`
4. **URL** `https://api.notion.com/v1/data_sources/9affd3bf-a3b7-474c-baf8-25c83ba3ef47/query`
5. **URLの内容を取得** — POST / ヘッダ3つ（Authorization: Bearer $NOTION_TOKEN, Notion-Version: 2025-09-03, Content-Type: application/json）/ 本文=手順3のテキスト
6. **辞書** / JSONとして取得結果を取り、`results` の件数で分岐
7. **もし results が空:**
   - テキスト（作成用JSON）: parent は `"database_id":"0bf755f4-eadf-4a0f-84e7-d67744d4ec82"`。名前=日付、日付プロパティ=同じ日、children に入力本文
   - URL `https://api.notion.com/v1/pages` で POST
8. **もし results がある:**
   - 先頭の `id` を取り、URL `https://api.notion.com/v1/blocks/{id}/children` に PATCH で paragraph を追記

入力欄は1つ。キーボード入力でもマイク音声でもよい（別モードにしない）。

ネタ投稿ショートカットと同じ注意: 本文に半角 `"` が含まれると JSON が壊れる。本格解消は Phase 2 の受け口。

**リマインダー（毎日 3:00 JST）**
- iOS ショートカットのオートメーション「時刻 3:00」
- すぐ入力を出さず、**通知だけ**（「日記」）→ 通知タップで上記ショートカットを開く
- 通知時点では Notion にページを作らない

**既存ネタ箱との分担**
- 日記: 思ったこと・感じたこと・出来事の生ログ
- コンテンツDB（ネタ）: 日記から拾った「出せそう」な断片だけ

関連: [project_sns_infra_ids.md](project_sns_infra_ids.md) [project_idea_capture_shortcut.md](project_idea_capture_shortcut.md) [project_note_drafting_workflow.md](project_note_drafting_workflow.md)
