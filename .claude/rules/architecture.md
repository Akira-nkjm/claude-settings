# アーキテクチャ・ファイル構成

> プロジェクトごとに編集するテンプレート。コードから読み取れない「なぜ」を中心に書く。

## システム概要

Claude Code マーケットプレイス（`my-marketplace`）として `my-plugin` を配布する設定リポジトリ。
利用者は `/plugin install` で道具箱を取得し、`/setup-project` で各プロジェクトにルール・Codex 機械を
展開する。ランタイム・アプリは存在せず、成果物は Markdown / JSON / Python フック / justfile。

## データフロー / 処理パイプライン

```
このリポジトリ（marketplace.json + plugins/my-plugin/）
   ↓  /plugin marketplace add → /plugin install my-plugin@my-marketplace
プラグインキャッシュ（~/.claude/plugins/cache/.../my-plugin/）
   ↓  道具箱（commands / skills / hooks / codegraph MCP）はキャッシュから常時有効
   ↓  /setup-project が templates/ を対象プロジェクトへ cp 展開
対象プロジェクト
   ├── REFRESH: 汎用ルール3本 + Codex 機械（毎回最新へ上書き）
   └── KEEP   : 固有ルール3本 + ルート4文書（既存は保護、--force で上書き）
```

## コアモジュール

<!-- 主要ディレクトリ/ファイルと役割。実装詳細ではなく責務を書く -->

- **`.claude-plugin/marketplace.json`** — マーケットプレイス定義（`name: my-marketplace`、収録プラグイン一覧）
- **`plugins/my-plugin/.claude-plugin/plugin.json`** — プラグイン定義。hooks 参照 + codegraph MCP サーバ宣言
- **`plugins/my-plugin/commands/`** — スラッシュコマンド（`setup-project`）
- **`plugins/my-plugin/skills/`** — 13 スキル（各 `SKILL.md`）。find-skills / markitdown + ECC 由来
- **`plugins/my-plugin/hooks/`** — `hooks.json` + Python フック群。安全（dangerous_cmd / protect_settings /
  _redact）・整形（autoformat）・セッション（session_start / session_end / pre_compact）
- **`plugins/my-plugin/templates/`** — `/setup-project` が展開する雛形（**配布の正典**）。
  ルート4文書 / `rules/`（汎用3 + 固有プレースホルダ3）/ `codex/`（justfile・run.py・README）

## レイヤー構成と依存方向

<!-- どの層がどの層に依存してよいか。循環禁止の境界 -->

```
marketplace.json  →  plugins/my-plugin/（plugin.json）  →  commands / skills / hooks / templates
（リポ直下の .claude/ ・ルート文書は templates の「展開先サンプル」であり、配布元ではない）
```

## 設計判断（なぜこうなっているか）

- **道具箱はプロジェクトにコピーせず、プラグインキャッシュから効かせる。** commands / skills / hooks /
  codegraph MCP を各プロジェクトに物理配置すると更新が分散するため。`/setup-project` が置くのは
  「プロジェクト側に物理配置が必要なもの（ルール・Codex 機械）」だけ。
- **REFRESH / KEEP の二分。** 汎用ルールと Codex 機械は正典が1か所であるべきなので毎回上書き（REFRESH）。
  プロジェクト固有文書は人が書くので保護（KEEP）。`--force` で初めて KEEP も上書き。
- **justfile は `.claude/justfile` に置く。** プロジェクト自身の `justfile` と衝突させないため。
  呼び出しは `just -f .claude/justfile <recipe>`。
- **Python フックは標準ライブラリのみ。** 利用側に追加依存を要求しないため。
- **ルートに設定を置かずすべて `plugins/my-plugin/` 配下に集約。** リポジトリを「ピュアな
  マーケットプレイス」に保つため（refactor #2 で確立）。

## ファイルツリー

```
claude-settings/
├── .claude-plugin/marketplace.json     # マーケットプレイス定義（my-marketplace）
├── plugins/my-plugin/                   # 配布物（正典）
│   ├── .claude-plugin/plugin.json       #   プラグイン定義 + codegraph MCP
│   ├── commands/                        #   /setup-project
│   ├── skills/                          #   13 スキル（*/SKILL.md）
│   ├── hooks/                           #   hooks.json + Python フック群
│   └── templates/                       #   /setup-project が展開する雛形
│       ├── CLAUDE.md / AGENTS.md / RULES.md / SOUL.md
│       ├── rules/                       #     git-workflow / security / codex-workflow + 固有3
│       └── codex/                       #     justfile / tools/codex/run.py / codex-README.md
├── CLAUDE.md / AGENTS.md / RULES.md / SOUL.md   # ← このリポへ /setup-project した産物
├── .claude/                             # ← 同上（rules/ ・ justfile ・ tools/codex/）
└── README.md
```

## よくあるワークフロー

### 配布物（道具箱）を変更する

1. `plugins/my-plugin/` 配下の該当ファイル（command / skill / hook / template）を編集する
2. 必要なら `marketplace.json` / `plugin.json` のバージョン・一覧を更新
3. JSON の妥当性を確認（[`commands.md`](commands.md) 参照）し、コミット
4. 利用側は `/plugin update` で最新化

### 新しいスキルを追加する

1. `plugins/my-plugin/skills/<name>/SKILL.md` を作成（`skill-creator` プラグインが補助）
2. frontmatter の `name` / `description`（トリガー条件）を整える
3. README のスキル一覧を更新

### テンプレート（展開される雛形）を変更する

1. `plugins/my-plugin/templates/` 配下を編集（**ここが正典**。リポ直下の `.claude/` ではない）
2. `/setup-project` を試験プロジェクトで実行し、REFRESH/KEEP の挙動を確認
