---
name: note-draft
description: note下書きを1問1答ブレストで材料出しし、ブリーフ化して Cursor の GPT（Task / gpt-5.6-luna-high）に執筆委譲する。親 Agent（Cursor）は記事本文を書かない。下書き作成・note記事・ブレスト開始時に使う。
---

# note下書き作成ワークフロー（note-draft）

`drafts/02_dopamine/` の構成（input.txt → brief.md → gpt_draft_raw.txt → draft_v1〜）を踏襲する。
**親 Agent（Cursor Auto）が記事本文を執筆してはいけない。** 執筆も次の1問も Cursor の GPT に委譲する。
OpenAI の Codex CLI は使わない。

## GPT 呼び出し（共通）

Cursor の Task ツール:

- `subagent_type`: `generalPurpose`
- `model`: `gpt-5.6-luna-high`
- 必要な `input.txt` / `brief.md` / 文体見本はプロンプトに本文ごと渡す
- 返ってきた文章は要約・言い換えしない

## 手順

1. **1問1答ブレスト**: Auto は質問を自分で作らない。これまでの `drafts/<topic>/input.txt`（と直前のユーザー返答）を GPT に渡し、**次の1問だけ**出させる。一度に複数問を並べない。ユーザーの回答はそのまま `input.txt` に蓄積する。
2. **ブリーフ化**: 材料が揃ったら `drafts/<topic>/brief.md` を作る。本人の言葉をそのまま残す（要約して言い換えない）。最低限含めるもの:
   - この記事で言いたいこと（結論）
   - 想定読者
   - 使う具体例・エピソード
   - 構成の骨組み（見出し案）
3. **執筆委譲**: ブリーフと文体見本を GPT に渡し、`gpt_draft_raw.txt` として保存する。Auto は本文を書かない。
4. **校正**: `/kousei` スキルに渡す（本文の書き換えは行わない）。捏造チェック（本人が言っていない体験談）は Auto の担当。

## GPT への指示で毎回入れる要素

- 本人の文体を可能な限り模倣（一般的な「上手いnote記事」に寄せない）
- 資料にないエピソード・数字・引用の創作を厳禁
- 書き出しとタイトルは本人が自分で考える → 冒頭は仮置き1〜2文、タイトルは候補列挙のみ
- 末尾に「申し送り」（真似た文体の特徴／材料が足りない箇所／自信のない箇所）

## 注意

- ブリーフ段階でも Auto が「代わりに書く」動きをしない。
- `draft_v*.md` / `body_v*.md` は直接書き換えない。
