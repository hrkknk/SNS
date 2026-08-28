---
name: project-idea-capture-shortcut
description: ネタ高速登録のiOSショートカット構成と、Shortcutsで詰まったポイント
metadata: 
  node_type: memory
  type: project
  originSessionId: 3e7d69b3-9a97-4795-a196-02783d6fe569
  modified: 2026-08-02T19:53:34.485Z
---

ネタ登録は iOS ショートカットから Notion REST API を直接叩く構成（サーバー不要）。2026-08-03 に2本とも動作確認済み。

- **ネタ投稿** — テキスト用。入力がそのまま タイトル になる
- **ネタURL** — URL用。共有シートからURLを受け取り、「入力を要求」で書いたひとことが タイトル、URLは 参照URL プロパティへ。Arc等Safari以外のブラウザでも動く（「Safari Webページの詳細を取得」はSafari専用なので使わない）

ページタイトルの自動取得はしていない。ネタ箱には「なぜ保存したのか」が残る方が有用という判断。

**アクション構成（この順番でないと動かない）**
1. 受け取る — 「もし入力がない場合: テキスト を 入力を要求」に設定。これで共有シート経由でもホーム画面タップでも動く
2. （ネタURLのみ）入力を要求 — ひとこと入力用
3. テキスト — Notion APIのJSON本文。`"content":"` と `"` の間に変数を挟む
4. **URL** — `https://api.notion.com/v1/pages`
5. URLの内容を取得 — POST / ヘッダ3つ（Authorization: Bearer $NOTION_TOKEN, Notion-Version: 2025-09-03, Content-Type: application/json）/ 本文を要求=ファイル に「テキスト」の結果を明示指定
6. （デバッグ時）クイックルック — APIの応答が読める。Notion側に失敗リクエストのログは残らないので、切り分けはこれで行う

**ハマりどころ**
- Notion iOSアプリのShortcuts純正アクションに「データベースページを作成」は存在しない（AIに質問/検索/ページ作成のみ）。API直叩きが必要
- 「URLの内容を取得」にURL入力欄はない。直前に独立した **URLアクション** を置く必要がある（これを知らずに1行目がURL欄だと誤案内した）
- Shortcutsの「本文を要求: JSON」でNotionのプロパティを組むと6階層必要で非現実的。テキストアクションに生JSONを書く方式にした
- 「変数を選択」に候補が出ない場合、参照先アクションがショートカット内に存在していない
- ショートカットを複製すると「本文を要求」の変数指定が外れることがある。本文が空のまま送ると Notion は `Provide a parent.page_id or parent.database_id...` という紛らわしいエラーを返す（parentの書き方の問題ではない）
- 閉じ括弧の数を間違えると `invalid_json`。参照URL版の末尾は `"}}}`、メモ(rich_text)版の末尾は `"}}]}}}`

**既知の弱点**: 入力に半角 `"` が含まれるとJSONが壊れ、エラーも出ず静かに登録失敗する。Phase 2でVercelに `{"text": "..."}` を受ける口を作れば解消できる。

関連: [[project-sns-infra-ids]]
