# プロジェクト固有の設定

<!-- このファイルをプロジェクトごとに編集する。CLAUDE.md は触らない。 -->

## プロジェクト概要

**claude-settings** — Claude Code と Codex CLI をどちらもメインハーネスとして使うための
エージェント設定テンプレート。このリポジトリ自身が **Claude Code マーケットプレイス**
（`my-marketplace`）であり、配布物 `my-plugin`（道具箱: コマンド / スキル / フック / codegraph MCP）を
任意のプロジェクトへ `/plugin install` 一発で導入できる。ルール類・Codex 連携機械は
`/setup-project` で各プロジェクトに展開する。

ECC（[affaan-m/ECC](https://github.com/affaan-m/ECC)）のアイデアを最小構成で運用可能にしたもの。

### 技術スタック

- **Markdown** — ルール・スキル（`SKILL.md`）・テンプレート文書の本体
- **JSON マニフェスト** — `.claude-plugin/marketplace.json`（マーケットプレイス定義）/
  `plugins/my-plugin/.claude-plugin/plugin.json`（プラグイン定義 + codegraph MCP 宣言）/
  `plugins/my-plugin/hooks/hooks.json`（フック登録）
- **Python 3（標準ライブラリのみ）** — `hooks/*.py` の安全・整形・セッション系フック、
  `templates/codex/tools/codex/run.py` の Codex 実行スクリプト
- **just（justfile）** — Codex 連携レシピ（`templates/codex/justfile` → 展開先で `.claude/justfile`）
- **codegraph MCP** — `npx -y @colbymchenry/codegraph`（外部 npm、プラグインが宣言）
- **Node.js** — Codex companion 実行に必要（`/codex:setup`）

## 規約・注意事項

- **このリポジトリはマーケットプレイスそのもの。** 配布対象はすべて `plugins/my-plugin/` 配下に置く。
  リポジトリ直下には設定ファイル（commands / skills / hooks など）を**置かない**。
- **正典は1か所。** 汎用ルール（git-workflow / security / codex-workflow）と Codex 機械は
  `plugins/my-plugin/templates/` が正典で、`/setup-project` の REFRESH 対象。各プロジェクト側で
  編集しても次回展開で上書きされる。プロジェクト固有の編集は KEEP 対象（project / architecture /
  commands / ルート4文書）に対して行う。
- **このリポジトリ直下の `.claude/`・ルート文書（CLAUDE/AGENTS/RULES/SOUL）は `/setup-project` を
  このリポ自身に対して実行した産物**であり、`plugins/my-plugin/templates/` 配下の正典とは別物。
  配布内容を変えるときは必ず `plugins/my-plugin/` 側を編集すること。
- フックは `${CLAUDE_PLUGIN_ROOT}` を参照するため、パスをハードコードしない。
- Python フックは標準ライブラリのみに依存させる（追加依存を入れない）。

## 関連ドキュメント

- 開発コマンドは [`commands.md`](commands.md) に書く
- アーキテクチャと設計判断は [`architecture.md`](architecture.md) に書く
