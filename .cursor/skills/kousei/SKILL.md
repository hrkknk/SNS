---
name: kousei
description: note原稿を Cursor の GPT（Task / gpt-5.6-luna-high）に渡して校正チェックする。誤字・表記のみ。文体・言い回し・断定の強さは変更しない。校正・kousei・講評の依頼で使う。
---

# 校正チェック（kousei）

指定された原稿ファイル（`$ARGUMENTS`）を、`kousei_prompt.md` とともに Cursor の GPT に渡し、結果を表示する。
親 Agent は校正文を自分で書かない。OpenAI の Codex CLI は使わない。

## 実行手順

1. 引数のファイルパスが存在することを確認する。無ければユーザーに確認する。
2. `kousei_prompt.md` と原稿ファイルの本文を読み、Task に渡す。

   - `subagent_type`: `generalPurpose`
   - `model`: `gpt-5.6-luna-high`
   - プロンプトに `kousei_prompt.md` の本文と原稿全文を含める
   - ファイルは編集しないこと、校正結果だけを返すことを明示する

3. Task の出力をそのままユーザーに提示する。**親 Agent が原稿を書き換えたり、校正結果を要約・改変してはいけない。**
4. 「【読みにくいと感じた箇所】」があってもファイルは編集しない。指摘の提示のみ。

## 注意

- 対象は note 原稿（`drafts/**/*.md` や `.txt`）。
- 代筆・リライトはしない。`draft_v*.md` / `body_v*.md` は直接書き換えない。
