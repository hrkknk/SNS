---
name: project-sns-phase-status
description: 自己発信プロジェクトの進捗と、次にやること
metadata: 
  node_type: memory
  type: project
  originSessionId: 3e7d69b3-9a97-4795-a196-02783d6fe569
  modified: 2026-08-07T05:11:41.315Z
---

自己発信・運用自動化プロジェクト（引き継ぎ資料は ChatGPT からの handoff md）の状況。2026-08-02 時点。

**Phase 1（発信を止めない最低限の仕組み）— ほぼ完了**
- NotionコンテンツDB / SNS投稿DB 構築済み → [[project-sns-infra-ids]]
- ネタ高速登録ショートカット2本 稼働 → [[project-idea-capture-shortcut]]
- 執筆スケジュール（10本）投入済み
- 残: **Bufferのチャンネル接続確認**（X/Instagramのアカウントが実際にBufferに繋がっているか未確認。API疎通のみ済み）

**公開スケジュール**: 当初 8/3 開始 → 一度 8/10 に後ろ倒ししたが、**2026-08-05 に1本目を前倒しで公開して発信開始済み**（以降2日おきに 8/28 までの予定）。

**note アカウント**: https://note.com/hrkknk2 （表示名「ししゃもくんママ」）。記事一覧は `https://note.com/api/v2/creators/hrkknk2/contents?kind=note&page=1`、本文は `https://note.com/api/v3/notes/<noteKey>` で取れる（プロフィールページのHTMLはJSレンダリングで記事一覧が読めない）。
- 1本目（2026-08-05）「AIが容赦なく奪っていくもの」 https://note.com/hrkknk2/n/n39b832c978fe — 自己紹介＋AI観＋「今後はクリスチャンとしての視点で書く」というカミングアウト。[[project-coffee-worldview-pivot]] の方針どおりの立ち上がり。
- 2本目（2026-08-07）「ドーパミンと能動性」 https://note.com/hrkknk2/n/ncebac8e9c09c — 消費型コンテンツ批判。中心概念は「価値の持続性」。[[project-note-drafting-workflow]] を初適用して制作。

**次のフェーズ**: Phase 2 = 記事完成後のAI編集チェック / note→X投稿候補生成 / Approve-Edit-Rejectフロー / Buffer自動投入。自動化レイヤーは n8n・Make ではなく **Vercel Cron + 軽量コード**で作る方針。ここでショートカットの `"` 問題も解消する。

**役割分担の原則**: 書く・考える・決めるのは本人。AIは編集者であって代筆者ではない。記事本文をAI文体に書き換えない。

**執筆リマインダー（2026-08-05 設定）**: claude.ai の scheduled routine `trig_01HZrSE1UXJHVsdUDfncxNiq`（火・木・土 21:00 JST / cron `0 12 * * 2,4,6` UTC、Opus 5、Notionコネクタ、リポジトリなし）。コンテンツDBから「執筆中」で公開予定日が最も近い1件を選び、ページ末尾に「執筆メモ（日付）」として ①答えるべき問い ②見出しの骨組み ③関連ネタ ④詰まりそうな点 を追記する。本文の代筆とプロパティ変更はプロンプトで禁止済み。
