# スキルの使いどころ

> `my-plugin` が提供するスキルを「いつ呼ぶか」の正典。スキルは description に基づいて
> 自動で起動しうるが、取りこぼしを防ぐためここに状況→スキルの対応を明示する。
> スキルの中身（手順）は各 `SKILL.md` が持つ。ここは**トリガー判断だけ**を書く。

## 使う前に

- 何かを始める前に「この作業に効くスキルはないか」を一度考える。特に
  **テスト・セキュリティ・API 設計・E2E・ドキュメント調査・ファイル変換**は対応スキルがある。
- 該当が思い当たらないときは `find-skills` に「こういうことをしたい」と投げて探させる。

## 状況 → スキル 早見表

| こういう時 | 使うスキル |
|---|---|
| 新機能を書く / バグ修正 / リファクタする | `tdd-workflow`（テスト先行・カバレッジ80%+を強制） |
| 認証・ユーザー入力・秘密情報・決済・新規エンドポイントを扱う | `security-review`（セキュリティチェックリスト） |
| REST API を設計する（命名・ステータス・ページング・エラー形・バージョニング） | `api-design` |
| 命名・可読性・不変性など言語横断の基本規約を確認したい | `coding-standards` |
| ブラウザ越しの E2E テストを書く / Playwright・Page Object・CI 連携 | `e2e-testing` |
| MCP サーバを作る（tools / resources / prompts / Zod / stdio・HTTP） | `mcp-server-patterns` |
| ライブラリ/フレームワークの最新の使い方・API・サンプルを知りたい | `documentation-lookup`（Context7 経由で最新ドキュメント） |
| あるトピックを根拠付き・引用付きで深く調べたい | `deep-research`（firecrawl / exa で多源調査） |
| PDF・docx・xlsx・pptx・画像・音声・HTML 等を Markdown 化／中身を取り出す | `markitdown`（※PDFを精読/ページ要約するなら `/read-pdf` を優先） |
| エージェント（自分）の失敗を構造的に自己デバッグしたい | `agent-introspection-debugging` |
| エージェントの挙動を評価駆動（EDD）で形式的に測りたい | `eval-harness` |
| 長い作業の区切りで文脈を意図的に圧縮して保持したい | `strategic-compact` |
| 「〜できるスキルある？」「どうやって X する？」と機能を探している | `find-skills` |

## 迷いやすい境界

- **`tdd-workflow` と `e2e-testing`** … 実装サイクル全体（unit〜）の進め方なら `tdd-workflow`、
  ブラウザ越しのシナリオテスト実装テクニックなら `e2e-testing`。新機能なら前者で始め、
  E2E が要る段で後者を併用。
- **`documentation-lookup` と `deep-research`** … 特定ライブラリの「正しい使い方/API」は
  `documentation-lookup`（公式ドキュメント直引き）。トピックを横断して根拠を集めるなら
  `deep-research`（Web 多源 + 引用）。
- **`markitdown` と `/read-pdf`** … 単に中身をテキスト/Markdown 化したいだけなら `markitdown`。
  ページごとに知識点を抽出して要約・学習したいなら `/read-pdf` コマンド。
- **`security-review` は事後ではなく着手時に** … 認証・入力処理・秘密情報・決済の実装を
  「書き始める前」に呼ぶ。書き終えてからのレビューよりチェックリストが効く。

## 関連する道具（スキル以外）

- `/read-pdf` — PDF をページ単位で精読し知識点を Markdown 要約（コマンド）
- `/setup-project` — ルール一式・Codex 機械を展開（コマンド）
- codegraph MCP — コード構造を調べる（コードを書く前に `codegraph_explore` で当たりを付ける）
- Codex 連携 — 実装の委譲は [`codex-workflow.md`](codex-workflow.md) を参照
