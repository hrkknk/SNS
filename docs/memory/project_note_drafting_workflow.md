---
name: project-note-drafting-workflow
description: note記事の下書きを作る運用（1問1答ブレスト→ブリーフ→GPTに執筆委譲）
metadata: 
  node_type: memory
  type: project
  originSessionId: 375f3d8c-b90b-40d1-8f9c-0881298e8a01
  modified: 2026-08-28T05:50:00.000Z
---

2026-08-06 に本人の希望で開始した、note記事の下書き作成フロー。2本目「ドーパミン中毒と消費型コンテンツ」で初適用。

**フロー**
1. **1問1答ブレスト**（7問前後）。親 Agent（Cursor Auto）は質問を自分で作らない。ユーザーの返答を Cursor の GPT（Task / `gpt-5.6-sol-high`）に渡し、次の1問だけ出させる。まとめて複数問を投げず、1問ずつ出して回答を受けてから次へ。
2. 回答を `drafts/<NN>_<slug>/brief.md` に整理する。**本人の言葉をそのまま残す**こと（要約して言い換えない）。
3. brief.md ＋ 既存note記事全文（文体見本）を渡し、**下書き執筆は Cursor の GPT に委譲**する → [feedback_delegate_prose_work_to_gpt.md](feedback_delegate_prose_work_to_gpt.md) と同じ呼び出し方。
4. 親 Agent の担当は、進行・ブリーフ化・受け渡し・**捏造チェック**（本人が言っていない体験談を書いていないか）・Notion反映。**下書き本文は書かない。**

**GPTへの指示で毎回入れる要素**
- 本人の文体を可能な限り模倣（一般的な「上手いnote記事」に寄せない）
- 資料にないエピソード・数字・引用の創作を厳禁
- **書き出しとタイトルは本人が自分で考える** → 冒頭は仮置き1〜2文、タイトルは候補列挙のみ
- 末尾に「申し送り」（真似た文体の特徴／材料が足りない箇所／自信のない箇所）を書かせる。これが次の追加質問の種になる

**Notion反映**: 下書きはコンテンツDBの該当ネタページ本文に append し、ステータスを「執筆中」にする。ページ冒頭に「GPT下書き v◯／日付」のcalloutを置く。ID類は [project_sns_infra_ids.md](project_sns_infra_ids.md)。

**Why**: 本人は「書く・考える・決める」は手放さないが、文章化の初速をAIに出させたい。親 Agent が下書きを書くと文体を壊す（→[feedback_never_rewrite_users_prose.md](feedback_never_rewrite_users_prose.md)）ため、引き出す役と書く役を分けている。

**How to apply**: 新しい記事の依頼が来たら、いきなり構成案や文案を出さず、まず GPT に次の1問を出させる。`codex exec` は使わない。

関連: [project_sns_phase_status.md](project_sns_phase_status.md) [project_coffee_worldview_pivot.md](project_coffee_worldview_pivot.md)
