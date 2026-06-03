# claude-settings

Claude Code と Codex CLI をどちらもメインで使えるエージェント設定テンプレート。**Claude Code プラグイン**（`my-marketplace` / `my-plugin`）として配布し、任意のプロジェクトに `/plugin install` 一発で道具箱（コマンド・スキル・フック・MCP）を導入できる。ルール類は `/setup-project` で各プロジェクトに展開する。

> このリポジトリは **マーケットプレイス**そのもの（`.claude-plugin/marketplace.json` + `plugins/my-plugin/`）。配布対象はすべて `plugins/my-plugin/` 配下にあり、ルートに設定ファイルは置かない。

ECC ([affaan-m/ECC](https://github.com/affaan-m/ECC)) のアイデアを取り込みつつ、最小構成で運用可能にしている。

---

## 目次

- [Quick Start](#quick-start)
- [設計思想](#設計思想マルチハーネス)
- [プラグイン / マーケットプレイス構成](#プラグイン--マーケットプレイス構成)
- [インストール済み Claude Code プラグイン](#インストール済み-claude-code-プラグイン)
- [インストール](#インストール)
- [ディレクトリ構成](#ディレクトリ構成)
- [使い方](#使い方)
  - [1. 新規プロジェクトのセットアップ](#1-新規プロジェクトのセットアップ)
  - [2. Claude Code で作業する](#2-claude-code-で作業する)
  - [3. Codex で実装を委譲する](#3-codex-で実装を委譲する)
  - [4. スキルを呼び出す](#4-スキルを呼び出す)
  - [5. CodeGraph で構造を調べる](#5-codegraph-で構造を調べる)
  - [6. instinct（経験則）を記録する](#6-instinct経験則を記録する)
  - [7. セッションを跨いで作業する](#7-セッションを跨いで作業する)
- [カスタマイズ](#カスタマイズプラグインを拡張する)
- [トラブルシューティング](#トラブルシューティング)

---

## Quick Start

**推奨: プラグインとして導入**（任意のプロジェクトの Claude Code セッション内で）

```text
# 1. マーケットプレイスを登録（初回のみ）
/plugin marketplace add Akira-nkjm/claude-settings

# 2. プラグインを入れる（道具箱 + codegraph MCP が全プロジェクト共通で有効に）
/plugin install my-plugin@my-marketplace

# 3. このプロジェクトにルール一式・Codex 機械を展開
/setup-project
```

その後、プロジェクト固有の 3 ファイルを埋める（`/setup-project` が対話で促す）:

```bash
$EDITOR .claude/rules/project.md       # 概要・スタック・規約
$EDITOR .claude/rules/architecture.md  # データフロー・設計判断
$EDITOR .claude/rules/commands.md      # セットアップ・テスト・ビルド
```

CodeGraph を使うなら初回だけ index を作る（任意）:

```bash
just -f .claude/justfile codegraph-init
```

主要コマンド早見表（プラグイン導入後）:

| やりたいこと | コマンド |
|---|---|
| ルール一式・Codex 機械を展開／更新 | `/setup-project`（`--force` で全上書き、`--no-codex` で Codex 省略） |
| 道具箱を最新化 | `/plugin update`（全プロジェクトに反映） |
| Codex タスクを作成 | `just -f .claude/justfile codex-new-task <name>` |
| Codex に実行を委譲 | `just -f .claude/justfile codex-run <name>` |
| 未処理タスク一覧 | `just -f .claude/justfile codex-tasks` |
| CodeGraph index を作成・再構築 | `just -f .claude/justfile codegraph-init` |
| CodeGraph 健康確認 | `just -f .claude/justfile codegraph-status` |
| Claude スキルを起動 | `/skill-name`（例: `/tdd-workflow` `/markitdown`） |

> 毎回 `-f .claude/justfile` を打つのが面倒なら `alias jc='just -f .claude/justfile'` を設定し、`jc codex-run <name>` のように使う。

---

## 設計思想（マルチハーネス）

| ファイル | 役割 | ハーネス |
|---|---|---|
| `AGENTS.md` | 全エージェント共通の作業ルール | Codex / Cursor / OpenCode 等が自動読込 |
| `RULES.md` | Must Always / Must Never の絶対ルール | 全エージェント |
| `SOUL.md` | 設計哲学と判断基準 | 全エージェント |
| `CLAUDE.md` | Claude Code 固有指示（`AGENTS.md` を `@import`） | Claude Code |
| `.claude/rules/` | 詳細ルール（共有資産） | 両ハーネス |
| `my-plugin`（skills） | スキル（Claude Code は `/skill-name`、他ハーネスは `plugins/my-plugin/skills/<name>/SKILL.md` を直接参照） | 両ハーネス |
| `.claude/instincts/` | 再利用可能な経験則（YAML） | 両ハーネス |
| `.codex/` | Codex CLI 固有の運用メモ | Codex |
| `.tasks/<name>.md` | Claude → Codex タスク受け渡し | ブリッジ |

---

## プラグイン / マーケットプレイス構成

配布は **2 段構え**:

1. **道具箱はプラグインで配る** — commands / skills / hooks / MCP を `/plugin install` で全プロジェクトに。各プロジェクトに**コピーされず**、プラグインキャッシュ `~/.claude/plugins/cache/.../my-plugin/` から効く。
2. **ルールは `/setup-project` で展開** — 常時コンテキストに載る CLAUDE.md・ルール類は各プロジェクトへ物理配置する（プラグインからは自動注入できないため）。

役割分担:

| 種類 | どこに住むか | どう配るか |
|---|---|---|
| 道具箱（commands / skills / hooks / codegraph MCP） | プラグインキャッシュ | `/plugin install`（全プロジェクト共通・自動） |
| 常時コンテキスト用のルール（CLAUDE.md / 汎用ルール / 哲学） | 各プロジェクトの `.claude/` ・ルート | `/setup-project` で展開 |
| プロジェクト固有ルール（project / architecture / commands） | 各プロジェクトの `.claude/rules/` | `/setup-project` 後に記入（再実行でも保護） |

> なぜ分けるか: プラグインは「常時コンテキストに載る CLAUDE.md / ルール」を自動注入できない。だから道具箱はプラグイン、ルールは各プロジェクトへ物理配置、という分担になる。

### マーケットプレイスのファイル構成

```
.claude-plugin/
└── marketplace.json          # マーケットプレイス定義（name: my-marketplace）
plugins/
└── my-plugin/
    ├── .claude-plugin/plugin.json   # プラグイン定義 + codegraph MCP
    ├── commands/             # /setup-project
    ├── skills/               # 13 スキル（markitdown 含む）
    ├── hooks/                # hooks.json + フック群（${CLAUDE_PLUGIN_ROOT} 参照）
    └── templates/            # /setup-project が各プロジェクトに展開する雛形
        ├── CLAUDE.md / AGENTS.md / RULES.md / SOUL.md
        ├── rules/            # 汎用 + 固有プレースホルダ
        └── codex/            # .claude/justfile / run.py / .codex/README.md
```

### `/setup-project` が展開するもの

| 配置先 | 中身 | 再実行時 |
|---|---|---|
| ルート | `CLAUDE.md` / `AGENTS.md` / `RULES.md` / `SOUL.md` | 保護（既存は触らない） |
| `.claude/rules/` | `git-workflow` / `security` / `codex-workflow` / `skills` | **更新**（プラグインが正典） |
| `.claude/rules/` | `project` / `architecture` / `commands` | 保護 |
| `.claude/justfile` ほか | Codex 機械（`--no-codex` で省略） | **更新** |

`--force` を付けると保護対象も上書きする。justfile は衝突回避のため**プロジェクト直下ではなく `.claude/justfile`** に置かれる。

---

## インストール済み Claude Code プラグイン

このリポジトリの設定とは別に、Claude Code 本体に **ユーザースコープ** (`~/.claude/`) で入れているプラグインの一覧。`/plugin` コマンドまたはマーケットプレイスから導入し、`~/.claude/settings.json` の `enabledPlugins` で有効化している。

> ここに挙げるプラグインは **各自の Claude Code 環境に別途インストールが必要**（本リポジトリの `my-plugin` とは別の、サードパーティ製プラグイン）。新しいマシンで同じ構成を再現する場合は下表の `repo` を `/plugin marketplace add` → `/plugin install` する。

| プラグイン | バージョン | 提供元 | マーケットプレイス (`repo`) | 役割 |
|---|---|---|---|---|
| `code-review` | unknown | Anthropic | `anthropics/claude-plugins-official` | 複数の専門エージェントによる PR の自動コードレビュー（信頼度スコア付き） |
| `github` | unknown | GitHub | `anthropics/claude-plugins-official` | 公式 GitHub MCP サーバ。issue/PR 管理・レビュー・リポジトリ検索を Claude Code から直接実行 |
| `codex` | 1.0.4 | OpenAI | `openai/codex-plugin-cc` | Claude Code から Codex CLI にレビュー・実装を委譲。本リポジトリの Codex 連携ワークフローの土台 |
| `understand-anything` | 2.7.5 | Lum1104 | `Lum1104/Understand-Anything` | コードベースを解析し knowledge graph を生成。アーキテクチャ理解・オンボーディング・可視化 |
| `skill-creator` | unknown | Anthropic | `anthropics/claude-plugins-official` | スキルの新規作成・改善・eval/ベンチマーク・description 最適化。`my-plugin` のスキルを足す/磨くときに使う |

### 各プラグインが提供するもの

**`code-review`** — Anthropic 公式。

- コマンド: `/code-review` — 現在ブランチ or 指定 PR をレビュー。`ultra` でクラウド上のマルチエージェントレビュー、`--comment` で PR にインラインコメント、`--fix` で修正適用。

**`github`** — GitHub 公式。

- MCP サーバ（HTTP）: `https://api.githubcopilot.com/mcp/`
- 認証: 環境変数 `GITHUB_PERSONAL_ACCESS_TOKEN` が必要（`Bearer` ヘッダに展開される）。トークンはソースに書かず環境変数で渡す（`my-plugin` の `templates/rules/security.md` 参照）。

**`codex`** (v1.0.4) — OpenAI 公式。`my-plugin` の Codex 連携ワークフロー（`templates/rules/codex-workflow.md` / `templates/codex/`）と連携する。

- コマンド: `/codex:setup` `/codex:review` `/codex:adversarial-review` `/codex:rescue` `/codex:status` `/codex:result` `/codex:cancel`
- スキル: `codex-cli-runtime` / `codex-result-handling` / `gpt-5-4-prompting`（内部ヘルパ）
- エージェント: `codex-rescue`（調査・修正委譲用サブエージェント）

**`understand-anything`** (v2.7.5) — コミュニティ製（MIT）。

- スキル: `/understand` `/understand-chat` `/understand-dashboard` `/understand-diff` `/understand-domain` `/understand-explain` `/understand-knowledge` `/understand-onboard`
- エージェント: `architecture-analyzer` / `domain-analyzer` / `file-analyzer` / `project-scanner` / `tour-builder` / `graph-reviewer` / `knowledge-graph-guide` ほか
- 生成物は `.understand-anything/` に出力される。

**`skill-creator`** — Anthropic 公式。

- スキル: `/skill-creator` — スキルの新規作成、既存スキルの改善、eval/ベンチマークによる性能測定、description のトリガー精度最適化。
- 本リポジトリの `plugins/my-plugin/skills/` にスキルを足す・磨くときの土台になる。

### 確認・管理コマンド

```bash
# 有効なプラグイン一覧（Claude Code セッション内）
/plugin

# 設定ファイルで直接確認
cat ~/.claude/settings.json                        # enabledPlugins
cat ~/.claude/plugins/installed_plugins.json       # インストール済みの実体・バージョン
cat ~/.claude/plugins/known_marketplaces.json      # 登録済みマーケットプレイス
```

> **注意**: これらは個人環境のユーザースコープ設定であり、本リポジトリの管理対象外。`~/.claude/settings.json` には `GITHUB_PERSONAL_ACCESS_TOKEN` 等のシークレットを **直書きしない**（環境変数で渡す）。

---

## インストール

任意のプロジェクトの Claude Code セッション内で:

```text
/plugin marketplace add Akira-nkjm/claude-settings   # 初回のみ
/plugin install my-plugin@my-marketplace             # 道具箱 + codegraph MCP
/setup-project                                        # ルール一式・Codex 機械を展開
```

- **道具箱**（commands / skills / hooks / codegraph MCP）はプロジェクトにコピーされず、プラグインキャッシュ `~/.claude/plugins/cache/.../my-plugin/` から効く。更新は `/plugin update` で全プロジェクトに反映。
- **`/setup-project`** が各プロジェクトに展開するもの（再実行時の挙動）:

| 配置先 | 中身 | 再実行時 |
|---|---|---|
| ルート | `CLAUDE.md` / `AGENTS.md` / `RULES.md` / `SOUL.md` | 保護 |
| `.claude/rules/` | `git-workflow` / `security` / `codex-workflow` / `skills` | 更新 |
| `.claude/rules/` | `project` / `architecture` / `commands`（固有・要編集） | 保護 |
| `.claude/justfile` ほか | Codex 機械（`--no-codex` で省略） | 更新 |

`--force` で保護対象も上書き。展開後にやること:

1. `.claude/rules/project.md` をそのプロジェクト用に編集
2. `.claude/rules/architecture.md` と `commands.md` のテンプレを埋める
3. CodeGraph を使う場合は初回に `just -f .claude/justfile codegraph-init` で index を作成

---

## ディレクトリ構成

### このリポジトリ（マーケットプレイス）

**配布対象**はすべて `plugins/my-plugin/` 配下にあり、ルートには配布物を置かない（下図はその配布物のみを示す）。なおルート直下にある `CLAUDE.md` / `AGENTS.md` / `.claude/` / `justfile` などは、このリポ自身に `/setup-project` を適用した **dogfood 産物**であって配布物ではない（`justfile` は `.claude/justfile` を `import` するだけの利便ラッパー）。

```
.claude-plugin/
└── marketplace.json          # マーケットプレイス定義（name: my-marketplace）
plugins/my-plugin/
├── .claude-plugin/plugin.json   # プラグイン定義 + codegraph MCP
├── commands/                 # /setup-project
├── skills/                   # 13 スキル（find-skills / markitdown + ECC 由来）
├── hooks/                    # hooks.json + フック群（${CLAUDE_PLUGIN_ROOT} 参照）
└── templates/                # /setup-project が各プロジェクトに展開する雛形
    ├── CLAUDE.md / AGENTS.md / RULES.md / SOUL.md
    ├── rules/                # git-workflow / security / codex-workflow / skills + 固有プレースホルダ
    └── codex/                # .claude/justfile / tools/codex/run.py / .codex/README.md
README.md
.gitignore
```

### `/setup-project` 実行後のプロジェクト

```
CLAUDE.md / AGENTS.md / RULES.md / SOUL.md   # ルート文書
.claude/
├── justfile               # Codex レシピ（衝突回避でここに）
├── rules/
│   ├── project.md             # プロジェクト概要（要編集）
│   ├── architecture.md        # アーキテクチャ・設計判断（要編集）
│   ├── commands.md            # 開発コマンド一覧（要編集）
│   ├── git-workflow.md        # コミット規約（正典・更新対象）
│   ├── codex-workflow.md      # Claude → Codex 委譲手順（正典・更新対象）
│   ├── security.md            # セキュリティ規約（正典・更新対象）
│   └── skills.md              # スキルの使いどころ（正典・更新対象）
└── tools/codex/run.py     # Codex 実行スクリプト
.codex/README.md           # Codex CLI 運用メモ
.tasks/                    # Claude → Codex タスク受け渡し
```

> commands / skills / hooks / codegraph MCP は**プロジェクトに置かれず**、プラグインキャッシュから効く。

---

## 使い方

### 1. 新規プロジェクトのセットアップ

[インストール](#インストール)の通り、Claude Code セッション内で:

```text
/plugin install my-plugin@my-marketplace   # 初回はその前に /plugin marketplace add Akira-nkjm/claude-settings
/setup-project                             # ルール一式・Codex 機械を展開
```

その後、プロジェクト固有情報を埋める（`/setup-project` が対話で促す）:

```bash
$EDITOR .claude/rules/project.md
$EDITOR .claude/rules/architecture.md
$EDITOR .claude/rules/commands.md
```

`project.md` に書くべき内容（ミニマム）:

```markdown
## プロジェクト概要
<このプロジェクトが何をするものか 1-3 行>

## スタック
<言語・フレームワーク・主要依存>

## 注意事項
<コードからは読み取れない非自明な規約>
```

### 2. Claude Code で作業する

Claude Code を起動すると以下が自動で読み込まれる:

- `CLAUDE.md` (→ `AGENTS.md` / `RULES.md` / `SOUL.md` / `.claude/rules/*.md` を `@import`)
- インストール済みスキル (`/<skill-name>` で起動可能。他ハーネスでは `SKILL.md` を直接参照)
- フック（`settings.local.json` で登録されたもの）

通常の作業例:

```text
あなた: 新機能 X を追加したい。テスト先行で実装して。
Claude: <tdd-workflow スキルを起動>
        → テスト作成 → RED 確認 → 実装 → GREEN 確認 → リファクタ
```

セキュリティに関わる変更時は手動で `/security-review` を呼ぶ:

```text
あなた: /security-review
Claude: <現在の diff をスキャン>
        → CRITICAL: ハードコードされた API キー検出
        → HIGH: 入力検証なしの SQL クエリ
```

### 3. Codex で実装を委譲する

**Claude が計画 → Codex が実装 → Claude が確認** のパターン。`/codex:setup` で初期化してから:

> justfile は `.claude/justfile` にあるため、以下の `just <recipe>` は **`just -f .claude/justfile <recipe>`** と読み替える（`alias jc='just -f .claude/justfile'` 推奨）。

```bash
# 1. タスクの雛形を作成
just codex-new-task feature-x

# 2. .tasks/feature-x.md を編集し、要件・受け入れ条件を書く
$EDITOR .tasks/feature-x.md

# 3. Codex に実行委譲（ファイル変更込み）
just codex-run feature-x

# 4. 結果を確認してタスクファイルを削除
rm .tasks/feature-x.md
```

**並列実行**は Claude Code セッション内から `run_in_background: true` で複数の `just codex-run` を同時起動するのが推奨パターン（`.claude/rules/codex-workflow.md` 参照）。完了通知が届いたら結果を回収する。

```bash
# 雛形作成
just codex-new-task task-a
just codex-new-task task-b

# それぞれを編集後、Claude セッションから並列実行（または手動で & 起動）
just codex-run task-a &
just codex-run task-b &
wait
```

Codex CLI を単体で使う場合は、`/setup-project` で展開される `.codex/README.md`（雛形: [`templates/codex/codex-README.md`](plugins/my-plugin/templates/codex/codex-README.md)）を参照。

> **既存タスクの保護**: `just codex-new-task <name>` は `.tasks/<name>.md` が既存ならエラーで止まる。上書きする場合は `FORCE=1` を付ける。

### 4. スキルを呼び出す

スキルは「特定の状況で起動される完結した手順書」。Claude Code では `/skill-name` で明示起動できる。他ハーネス（Codex 等）はプラグインを読み込まないので、`plugins/my-plugin/skills/<name>/SKILL.md` を直接参照する。

```text
/tdd-workflow              # TDD 強制
/security-review           # セキュリティ脆弱性スキャン
/strategic-compact         # 圧縮タイミングを判断
/deep-research <topic>     # 多ソース調査
/documentation-lookup <lib> # Context7 で最新ドキュメント取得
/markitdown <file>         # Office/PDF/画像等を Markdown へ忠実変換
/api-design                # REST API パターン
/e2e-testing               # Playwright E2E パターン
/find-skills <keyword>     # スキル探索
```

スキルはエージェントが**プロアクティブに**起動することもある（description に書かれた発火条件に該当した場合）。

### 5. CodeGraph で構造を調べる

ローカルで tree-sitter ベースのコード知識グラフを構築し、MCP 経由でエージェントに提供する。**API キー不要・Claude Code サブスクで動作・ローカル完結**。

```bash
# 初回 index 作成（リポジトリに .codegraph/ がない場合）
just -f .claude/justfile codegraph-init

# 健康確認
just -f .claude/justfile codegraph-status
```

codegraph MCP は `my-plugin` の `plugin.json` に登録済みなので、プラグインを入れた全プロジェクトで MCP サーバが自動で立ち上がる。ただし `.codegraph/` が未初期化のままだと MCP ツール呼び出し時に未初期化エラーになるため、**最初の構造調査前に `codegraph-init`（= `codegraph init -i`）を実行する**。以降はファイル監視で自動更新される。

セッション内では「構造的な質問は grep より先に codegraph」がルール:

| 質問 | MCP ツール |
|---|---|
| 「X はどこで定義？」 | `codegraph_search` |
| 「Y を呼ぶのは？」 | `codegraph_callers` |
| 「Y は何を呼ぶ？」 | `codegraph_callees` |
| 「X から Y への経路・フロー」 | `codegraph_explore` |
| 「Z を変えると何が壊れる？」 | `codegraph_impact` |
| 「ファイル構成・一覧」 | `codegraph_files` |
| 「複数シンボルのソース／概観」 | `codegraph_explore` |

[CodeGraph 公式 README](https://github.com/colbymchenry/codegraph) 時点の公式ベンチで **35% 安・57% トークン減・46% 速・71% ツール呼出削減**（vs 素の grep ベース探索）。エージェント向けの詳細な使い方指針は [CodeGraph 公式ドキュメント](https://github.com/colbymchenry/codegraph) を参照。

### 6. instinct（経験則）を記録する

同じ問題に 2 回以上ぶつかったら instinct に書く:

```bash
$EDITOR .claude/instincts/project/<topic>.yaml
```

スキーマ例（`hook-absolute-path.yaml` 参照）:

```yaml
name: <short-kebab-case>
description: <一行サマリー>
scope: project
confidence: high
observations: 2
created: 2026-05-26
updated: 2026-05-26
tags: [<tag>]

trigger: |
  いつこのインスティンクトが発火するか

guidance: |
  そのとき何をすべきか

rationale: |
  なぜそうするのか
```

汎用性が確認できたら `inherited/` に移して他プロジェクトでも使う。

### 7. セッションを跨いで作業する

メモリ永続化フック (`session_start.py` / `session_end.py` / `pre_compact.py`) はデフォルト無効。`CLAUDE_SESSION_PERSIST=1` を設定した場合のみ、前回セッションの要約が自動で次回 context に注入される。保存前に redaction は行うが、機密情報を扱うプロジェクトでは必要性を確認してから有効化する。

```bash
export CLAUDE_SESSION_PERSIST=1

# セッション履歴の確認
ls .claude/sessions/
cat .claude/sessions/latest.md

# 古いセッションを掃除
find .claude/sessions/ -mtime +30 -delete
```

無効化したい場合:

```bash
unset CLAUDE_SESSION_PERSIST
```

注入サイズ上限の変更:

```bash
export ECC_SESSION_START_MAX_CHARS=12000   # デフォルト 8000
```

---

## カスタマイズ（プラグインを拡張する）

道具箱はすべて `plugins/my-plugin/` 配下にある。編集後は `/plugin update` で各プロジェクトに反映する。

### ルールを足す

横断ルールは `plugins/my-plugin/templates/rules/<topic>.md` に置き、`templates/CLAUDE.md` の `@import` リストに追記する。`/setup-project` で各プロジェクトに展開される（汎用ルール扱いにするなら setup-project.md の REFRESH 群に追加）。

### スキルを足す

```bash
mkdir -p plugins/my-plugin/skills/<name>
cat > plugins/my-plugin/skills/<name>/SKILL.md <<'EOF'
---
name: <name>
description: <いつ起動されるべきか>
origin: local
---

# <Skill Title>

## When to Use
...

## Steps
...
EOF
```

### フックを足す

1. スクリプトを `plugins/my-plugin/hooks/<name>.py` に作成
2. `plugins/my-plugin/hooks/hooks.json` に登録（パスは `${CLAUDE_PLUGIN_ROOT}/hooks/<name>.py` で指定）

### コマンド (`/foo`) を足す

`plugins/my-plugin/commands/<name>.md` に作成。フロントマターと本文の書式は既存の `setup-project.md` を参照。

---

## トラブルシューティング

### セッション永続化が動かない

フック自体は `.claude/settings.local.json` で登録済み（`SessionStart` / `Stop` / `PreCompact`）。実際の保存・読込は **`CLAUDE_SESSION_PERSIST=1` がセットされている時のみ**動く。

```bash
export CLAUDE_SESSION_PERSIST=1
# 以降のセッションで .claude/sessions/ への保存と次回コンテキスト注入が有効
```

自前で hook を足すときは、**パスを必ず `$CLAUDE_PROJECT_DIR/` で絶対化する**（相対パスは cwd 依存で壊れる）。

### `rm -rf` がブロックされる

`dangerous_cmd.py` フック（`my-plugin` 提供）の意図的挙動。`-r` と `-f` の組み合わせ（`rm -rf`, `rm -fr`, `rm -r -f` 等）のみブロックされ、`rm -f file.txt` や `rm -r dir` は通る。検出が必要なら端末から直接実行する。

### `settings.local.json` を編集できない

`protect_settings.py` フック（`my-plugin` 提供）が Edit/Write をブロックしている。保護対象は `.claude/settings.json` / `.claude/settings.local.json` / `~/.claude/settings.json` の絶対パス一致のみ。エージェント経由ではなく、エディタで直接開いて編集する。

### Codex に `just` 経由でタスクを渡せない

まず `/codex:setup` スキルで認証・CLI 可用性を確認する。`just -f .claude/justfile codex-run` は内部で `.claude/tools/codex/run.py` を呼び、Claude plugin cache の `codex-companion.mjs` を探索する:

- **0 件**: 「Codex plugin がインストールされていません」と表示 → `/codex:setup` を実行
- **複数件**: 最新バージョンを自動選択（選択結果は stderr に表示）
- **node 不在**: PATH を確認

レート制限等で Codex 自体が落ちた場合は、`.tasks/<name>.md` を書いた状態のまま `Agent(isolation: "worktree")` サブエージェントへフォールバックする。詳細は [`templates/rules/codex-workflow.md`](plugins/my-plugin/templates/rules/codex-workflow.md) を参照。

### スキルが起動しない

スキルは `my-plugin` が提供する。まずプラグインが有効か確認:

```text
/plugin                       # my-plugin が有効か
```

スキル本体は `plugins/my-plugin/skills/<name>/SKILL.md`。明示起動なら `/skill-name`、自動起動を期待するなら SKILL.md の `description` に発火条件を明確に書く。

---

## 参考

- [affaan-m/ECC](https://github.com/affaan-m/ECC) — 本リポジトリが参考にしている上位互換システム
- [Claude Code ドキュメント](https://docs.claude.com/en/docs/claude-code)
- [Codex CLI](https://github.com/openai/codex)
