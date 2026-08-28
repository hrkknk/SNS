---
name: kousei
description: note原稿を gpt-5.6-terra（codex CLI）に渡して校正チェックする。誤字・表記のみ。文体・言い回し・断定の強さは変更しない。校正・kousei・講評の依頼で使う。
---

# 校正チェック（kousei）

指定された原稿ファイル（`$ARGUMENTS`）を、`~/SNS/kousei_prompt.md` とともに gpt-5.6-terra に渡し、結果を表示する。

## 実行手順

1. 引数のファイルパスが存在することを確認する。無ければユーザーに確認する。
2. 以下を実行する（`--sandbox read-only` と `approval_policy="never"` は必須）:

   ```bash
   cat "<draft-file-path>" | codex exec --skip-git-repo-check --sandbox read-only \
     -c approval_policy="never" -m gpt-5.6-terra \
     -c model_reasoning_effort="medium" "$(cat ~/SNS/kousei_prompt.md)"
   ```

3. 出力をそのままユーザーに提示する。**親 Agent が原稿を書き換えたり、校正結果を要約・改変してはいけない。**
4. 「【読みにくいと感じた箇所】」があってもファイルは編集しない。指摘の提示のみ。

## 注意

- 対象は note 原稿（`drafts/**/*.md` や `.txt`）。
- 代筆・リライトはしない。`draft_v*.md` / `body_v*.md` は直接書き換えない。
