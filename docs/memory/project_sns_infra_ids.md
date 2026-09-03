---
name: project-sns-infra-ids
description: 自己発信プロジェクトのNotion DB / Buffer の各種ID（自動化コードで参照する）
metadata: 
  node_type: memory
  type: project
  originSessionId: 3e7d69b3-9a97-4795-a196-02783d6fe569
  modified: 2026-08-02T19:53:40.950Z
---

自己発信・運用自動化プロジェクト（2026-08-03開始）で使う外部サービスのID。

**Notion**（アカウント: hrkknk0605@gmail.com）
- 親ページ「発信管理」: `3b0e6b98-d34f-8164-8d92-f19948b14e80`
- コンテンツDB data source: `fe59df72-de82-4c4a-add7-be01a0fc64cc`（noteの記事＋ネタ箱。ステータス: ネタ/執筆中/レビュー/公開予定/公開済み。他に カテゴリ / 公開予定日 / 公開URL / 参照URL / メモ）
- SNS投稿DB data source: `711e5dac-ebee-490c-a042-ca9a57656b38`（ステータス: 下書き/承認済み/予約済み/投稿済み/却下。「元記事」でコンテンツDBにリレーション）
- 日記DB: database `0bf755f4-eadf-4a0f-84e7-d67744d4ec82` / data source `9affd3bf-a3b7-474c-baf8-25c83ba3ef47`（日付1ページ。プロパティ: 名前 / 日付 / ネタ化済み。運用は [project_journal_workflow.md](project_journal_workflow.md)）

**Buffer**
- GraphQL API エンドポイント: `https://api.buffer.com`（POST、Bearer認証）
- organization id: `6a6e45c6c2ebdd6f6305f031`
- トークンは `~/.zshrc` の `$BUFFER_ACCESS_TOKEN`。**非対話シェルは .zshrc を自動読込しないので、Bashツールでは `source ~/.zshrc && ...` を前置する必要がある**（パイプで繋ぐとサブシェル化して変数が消えるので注意）
- 無料プランは 100 リクエスト/24時間

**採用しなかった選択肢**: n8n / Make は導入せず、自動化レイヤーは Vercel Cron + 軽量コードで代替する方針。note と X/Instagram 本体への直接API連携も行わない（noteは手動公開、SNSはBuffer経由）。

関連: [feedback_env_var_format.md](feedback_env_var_format.md)
