---
name: project-journal-workflow
description: 日記DBでネタ断片と文体材料を蓄積する運用（確定後のみページ作成）
metadata:
  node_type: memory
  type: project
  modified: 2026-09-03T21:00:00.000Z
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

---

## スマホ: Shortcuts「日記」の具体手順

ネタ投稿と同じく **テキストに生JSON → URL → URLの内容を取得**。変数は `"..."` の間に挟む（Shortcutsの「本文を要求: JSON」は使わない）。

共通ヘッダ（すべての「URLの内容を取得」で同じ）:
- `Authorization`: `Bearer ` + あなたの `NOTION_TOKEN`（ネタ投稿と同じトークン）
- `Notion-Version`: `2025-09-03`
- `Content-Type`: `application/json`
- メソッド: 下に書くとおり
- **本文を要求 = ファイル** に、直前の「テキスト」アクションを明示指定

### A. ショートカット本体（名前: 日記）

1. **入力を要求**
   - プロンプト: `日記`
   - 入力の種類: テキスト
   - キャンセルしたらここで終了（この時点では Notion を呼ばない）
   - 結果を変数 `本文` に保存（「変数を設定」）

2. **もし** `本文` が 空 なら → **何もしない** で終了（空ページ防止）

3. **現在の日付**
4. **日付をフォーマット**
   - 日付の形式: カスタム `yyyy-MM-dd`
   - 結果を変数 `日付` に保存
5. **現在の日付**（もう一度）→ **日付をフォーマット** カスタム `HH:mm` → 変数 `時刻`

6. **テキスト**（クエリ用。下をコピーし、`DATE` の位置だけ変数 `日付` に差し替え）

```text
{"filter":{"property":"名前","title":{"equals":"DATE"}},"page_size":1}
```

Shortcutsではこう組む:  
`{"filter":{"property":"名前","title":{"equals":"` + 【日付】 + `"}},"page_size":1}`

7. **URL**  
   `https://api.notion.com/v1/data_sources/9affd3bf-a3b7-474c-baf8-25c83ba3ef47/query`

8. **URLの内容を取得**
   - 方法: POST
   - ヘッダ3つ（上記）
   - 本文 = 手順6のテキスト
   - 結果を変数 `検索結果` に保存

9. **辞書を取得**（入力: `検索結果`）→ **辞書の値を取得** キー `results` → 変数 `results`
10. **リストから項目をカウント**（入力: `results`）→ 変数 `件数`

11. **もし** `件数` `等しい` `0` （今日のページが無い → 作成）

    11a. **テキスト**（作成用JSON。`DATE` と `BODY` を変数に差し替え）

```text
{"parent":{"database_id":"0bf755f4-eadf-4a0f-84e7-d67744d4ec82"},"properties":{"名前":{"title":[{"text":{"content":"DATE"}}]},"日付":{"date":{"start":"DATE"}},"ネタ化済み":{"checkbox":false}},"children":[{"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":"TIME"},"annotations":{"bold":true}}]}},{"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":"BODY"}}]}}]}
```

差し替え:
- `DATE` → 変数 `日付`（名前と日付プロパティの2箇所）
- `TIME` → 変数 `時刻`
- `BODY` → 変数 `本文`

末尾の閉じは `"}}]}}}`（ネタ投稿の rich_text 版と同じ感覚で数える）

    11b. **URL** `https://api.notion.com/v1/pages`  
    11c. **URLの内容を取得** — POST / ヘッダ3つ / 本文=11a

12. **否则**（今日のページがある → 追記）

    12a. **リストの最初の項目を取得**（入力: `results`）→ **辞書の値を取得** キー `id` → 変数 `ページID`  
    12b. **テキスト**（追記用JSON）

```text
{"children":[{"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":"TIME"},"annotations":{"bold":true}}]}},{"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":"BODY"}}]}}]}
```

差し替え: `TIME`→`時刻`、`BODY`→`本文`

    12c. **テキスト**（URL組み立て）  
        `https://api.notion.com/v1/blocks/` + 【ページID】 + `/children`  
        → これを **URL** アクションに渡すか、URLアクションの文字列に変数を埋め込む  
    12d. **URLの内容を取得** — **PATCH** / ヘッダ3つ / 本文=12b

13. （初回だけ）**クイックルック** で応答を確認。動いたら外してよい

14. ショートカットの詳細 → **ホーム画面に追加**

### B. リマインダー（毎日 3:00、ページは作らない）

1. Shortcuts → **オートメーション** → 個人用オートメーションを作成
2. **時刻** → 3:00 / 毎日
3. アクションは **通知を表示** だけ
   - 本文: `日記を書く`
   - （可能なら）通知タップでショートカット「日記」を開く設定にする
4. 「実行の前に尋ねる」はオフでよいが、**このオートメーション自体では入力も Notion も呼ばない**

---

**注意（ネタ投稿と同じ）**
- 「URLの内容を取得」の直前に独立した **URL** アクションが必要
- 本文に半角 `"` が含まれると JSON が壊れて静かに失敗する
- トークンはネタ投稿ショートカットからコピーしてよい

**既存ネタ箱との分担**
- 日記: 思ったこと・感じたこと・出来事の生ログ
- コンテンツDB（ネタ）: 日記から拾った「出せそう」な断片だけ

関連: [project_sns_infra_ids.md](project_sns_infra_ids.md) [project_idea_capture_shortcut.md](project_idea_capture_shortcut.md) [project_note_drafting_workflow.md](project_note_drafting_workflow.md)
