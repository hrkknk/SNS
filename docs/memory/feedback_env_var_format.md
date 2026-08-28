---
name: feedback-env-var-format
description: 環境変数を設定してもらうよう案内する際の、ユーザーへの提示コマンド形式
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3e7d69b3-9a97-4795-a196-02783d6fe569
  modified: 2026-08-01T19:23:03.447Z
---

環境変数の設定をユーザーに依頼する際は、`read -s` などの非表示プロンプト形式ではなく、シンプルな `echo 'export VAR="value"' >> ~/.zshrc && source ~/.zshrc` 形式のワンライナーを提示すること。

**Why:** Buffer APIキーの設定案内で、最初にセキュリティ配慮から `read -s -p ... && echo ... >> ~/.zshrc` という非表示入力プロンプト形式を提示したところ、ユーザーは「さっきのexport文をパイプとかでzshrcに書けるコマンドにして」と、シンプルな `echo >> ~/.zshrc` 形式を明示的に求め直した。ユーザーは値を自分でコマンド内に埋め込んで実行する運用を好む。

**How to apply:** 今後、APIキーやトークンなどの環境変数をユーザーのシェル設定ファイル（`~/.zshrc`等）に追加する案内をする場面では、`echo 'export KEY="値をここに"' >> ~/.zshrc && source ~/.zshrc` の形式をデフォルトで提示する。hidden-input方式は提案しない（ユーザーから明示的に要望があれば別）。
