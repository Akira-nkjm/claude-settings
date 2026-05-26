# claude-settings

Claude Code と Codex CLI をどちらもメインで使えるエージェント設定テンプレート。新しいプロジェクトに `git clone` → `just install` で設定一式を展開できる。

ECC ([affaan-m/ECC](https://github.com/affaan-m/ECC)) のアイデアを取り込みつつ、最小構成で運用可能にしている。

---

## 目次

- [Quick Start](#quick-start)
- [設計思想](#設計思想マルチハーネス)
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
- [カスタマイズ](#カスタマイズ)
- [トラブルシューティング](#トラブルシューティング)

---

## Quick Start

```bash
# 1. プロジェクトに導入
cd ~/projects/my-app
git clone https://github.com/<you>/claude-settings.git
cd claude-settings && just install && cd ..

# 2. プロジェクト固有情報を埋める
$EDITOR .claude/rules/project.md       # 概要・スタック・規約
$EDITOR .claude/rules/architecture.md  # データフロー・設計判断
$EDITOR .claude/rules/commands.md      # セットアップ・テスト・ビルド

# 3. CodeGraph index を作る（任意・初回のみ）
npx -y @colbymchenry/codegraph init -i

# 4. Claude Code を起動して作業開始
claude
```

主要コマンド早見表:

| やりたいこと | コマンド |
|---|---|
| 設定を別プロジェクトへ適用（非破壊） | `just install` |
| 差分だけ確認 | `DRY_RUN=1 just install` |
| 既存を退避して上書き | `FORCE=1 just install` |
| Codex タスクを作成 | `just codex-new-task <name>` |
| Codex に実行を委譲 | `just codex-run <name>` |
| 未処理タスク一覧 | `just codex-tasks` |
| Claude スキルを起動 | `/skill-name`（例: `/tdd-workflow`） |
| 危険コマンド hook をテスト | `python3 .claude/tools/tests/test_dangerous_cmd.py` |

---

## 設計思想（マルチハーネス）

| ファイル | 役割 | ハーネス |
|---|---|---|
| `AGENTS.md` | 全エージェント共通の作業ルール | Codex / Cursor / OpenCode 等が自動読込 |
| `RULES.md` | Must Always / Must Never の絶対ルール | 全エージェント |
| `SOUL.md` | 設計哲学と判断基準 | 全エージェント |
| `CLAUDE.md` | Claude Code 固有指示（`AGENTS.md` を `@import`） | Claude Code |
| `.claude/rules/` | 詳細ルール（共有資産） | 両ハーネス |
| `.claude/skills/` | スキル（Claude Code は `/skill-name`、他ハーネスは `SKILL.md` を直接参照） | 両ハーネス |
| `.claude/instincts/` | 再利用可能な経験則（YAML） | 両ハーネス |
| `.codex/` | Codex CLI 固有の運用メモ | Codex |
| `.tasks/<name>.md` | Claude → Codex タスク受け渡し | ブリッジ |

---

## インストール

```bash
cd my-project
git clone <this-repo> claude-settings
cd claude-settings
just install
```

以下がプロジェクトルートに非破壊で適用される。既存ファイルはデフォルトで上書きせず、ディレクトリ内の不足ファイルだけを追加する。

| ファイル/ディレクトリ | 内容 |
|---|---|
| `AGENTS.md` | 全エージェント共通指示 |
| `RULES.md` | 絶対ルール |
| `SOUL.md` | 設計哲学 |
| `CLAUDE.md` | Claude Code 用指示 |
| `.claude/` | フック・ルール・コマンド・スキル・instincts |
| `.codex/` | Codex 運用メモ |
| `.mcp.json` | CodeGraph MCP 設定 |
| `justfile` | `just` レシピ（既存があればマージ） |
| `.gitignore` | `.tasks/*.md` 等の除外（既存があればマージ） |

更新オプション:

```bash
DRY_RUN=1 just install   # 変更せずに差分だけ確認
FORCE=1 just install     # 既存ファイルを .bak.<timestamp> に退避して上書き
```

`.claude/rules/project.md` / `architecture.md` / `commands.md` など、プロジェクト固有編集が入るファイルは既存があれば保護される。

インストール後にやること:

1. `.claude/rules/project.md` をそのプロジェクト用に編集
2. `.claude/rules/architecture.md` と `commands.md` のテンプレを埋める
3. （任意）`.claude/settings.local.json` でフックを有効化（[トラブルシューティング](#フックを有効化したい)）
4. CodeGraph を使う場合は、初回に `npx -y @colbymchenry/codegraph init -i` で index を作成

---

## ディレクトリ構成

```
AGENTS.md              # 全エージェント共通指示
RULES.md               # 絶対遵守ルール
SOUL.md                # 設計哲学
CLAUDE.md              # Claude Code 固有指示

.claude/
├── commands/          # Claude Code カスタムコマンド (/read-pdf)
├── skills/            # スキル（find-skills + ECC 由来 11 個）
├── instincts/         # 再利用可能な経験則 YAML
│   ├── project/            # このプロジェクト固有
│   └── inherited/          # 他プロジェクトから移植
├── rules/             # 両ハーネスから参照される共有ルール
│   ├── project.md          # プロジェクト概要（要編集）
│   ├── architecture.md     # アーキテクチャ・設計判断（テンプレ）
│   ├── commands.md         # 開発コマンド一覧（テンプレ）
│   ├── git-workflow.md     # コミット規約（正典）
│   ├── codex-workflow.md   # Claude → Codex 委譲手順（正典）
│   └── security.md         # セキュリティ規約（正典）
├── sessions/          # フックが自動保存（.gitignore 済）
├── tools/
│   ├── hooks/         # PreToolUse / PostToolUse / SessionStart / Stop / PreCompact
│   ├── install/       # justfile マージ等のインストール補助
│   └── tests/         # フックスクリプトのテスト
└── settings.local.json     # パーミッション・フック設定

.codex/
└── README.md          # Codex CLI 運用メモ
```

---

## 使い方

### 1. 新規プロジェクトのセットアップ

```bash
# プロジェクトに設定を展開
cd ~/projects/my-new-app
git clone https://github.com/<you>/claude-settings.git claude-settings
cd claude-settings && just install && cd ..

# プロジェクト固有情報を埋める
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

Codex CLI を単体で使う場合は [`.codex/README.md`](.codex/README.md) を参照。

> **既存タスクの保護**: `just codex-new-task <name>` は `.tasks/<name>.md` が既存ならエラーで止まる。上書きする場合は `FORCE=1` を付ける。

### 4. スキルを呼び出す

スキルは「特定の状況で起動される完結した手順書」。Claude Code では `/skill-name` で明示起動できる。他ハーネスでは `.claude/skills/<name>/SKILL.md` を直接参照する。

```text
/tdd-workflow              # TDD 強制
/security-review           # セキュリティ脆弱性スキャン
/strategic-compact         # 圧縮タイミングを判断
/deep-research <topic>     # 多ソース調査
/documentation-lookup <lib> # Context7 で最新ドキュメント取得
/api-design                # REST API パターン
/e2e-testing               # Playwright E2E パターン
/find-skills <keyword>     # スキル探索
```

スキルはエージェントが**プロアクティブに**起動することもある（description に書かれた発火条件に該当した場合）。

### 5. CodeGraph で構造を調べる

ローカルで tree-sitter ベースのコード知識グラフを構築し、MCP 経由でエージェントに提供する。**API キー不要・Claude Code サブスクで動作・ローカル完結**。

```bash
# 初回 index 作成（リポジトリに .codegraph/ がない場合）
npx -y @colbymchenry/codegraph init -i

# 健康確認
npx -y @colbymchenry/codegraph status
```

`.mcp.json` に `codegraph serve --mcp` が登録済みなので、Claude Code 起動時に MCP サーバが自動で立ち上がる。`.codegraph/` が未初期化のままだと MCP ツール呼び出し時に未初期化エラーになるため、**最初の構造調査前に `init -i` を実行する**。以降はファイル監視で自動更新される。

セッション内では「構造的な質問は grep より先に codegraph」がルール:

| 質問 | MCP ツール |
|---|---|
| 「X はどこで定義？」 | `codegraph_search` |
| 「Y を呼ぶのは？」 | `codegraph_callers` |
| 「Y は何を呼ぶ？」 | `codegraph_callees` |
| 「X から Y への経路」 | `codegraph_trace` |
| 「Z を変えると何が壊れる？」 | `codegraph_impact` |
| 「タスク用の context」 | `codegraph_context` |
| 「複数シンボルのソース」 | `codegraph_explore` |

[CodeGraph 公式 README](https://github.com/colbymchenry/codegraph) 時点の公式ベンチで **35% 安・57% トークン減・46% 速・71% ツール呼出削減**（vs 素の grep ベース探索）。エージェント向けの詳細な使い方指針は [`.claude/CLAUDE.md`](.claude/CLAUDE.md) を参照。

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

## カスタマイズ

### ルールを足す

新しい横断ルールは `.claude/rules/<topic>.md` に置き、CLAUDE.md の `@import` リストに追記:

```markdown
@.claude/rules/<topic>.md
```

### スキルを足す

```bash
mkdir -p .claude/skills/<name>
cat > .claude/skills/<name>/SKILL.md <<'EOF'
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

1. スクリプトを `.claude/tools/hooks/<name>.py` に作成
2. `.claude/settings.local.json` の `hooks` に登録（パスは必ず `$CLAUDE_PROJECT_DIR/` 始まりで絶対化）
3. `.claude/tools/tests/` にテストを書く

### コマンド (`/foo`) を足す

`.claude/commands/<name>.md` に作成。フロントマターと本文の書式は既存の `read-pdf.md` を参照。

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

`dangerous_cmd.py` の意図的挙動。`-r` と `-f` の組み合わせ（`rm -rf`, `rm -fr`, `rm -r -f` 等）のみブロックされ、`rm -f file.txt` や `rm -r dir` は通る。検出が必要なら端末から直接実行する。テスト:

```bash
python3 .claude/tools/tests/test_dangerous_cmd.py
```

### `settings.local.json` を編集できない

`protect_settings.py` フックが Edit/Write をブロックしている。保護対象は `.claude/settings.json` / `.claude/settings.local.json` / `~/.claude/settings.json` の絶対パス一致のみ。エージェント経由ではなく、エディタで直接開いて編集する。

### `just install` で既存設定が消えた

デフォルトは非破壊（既存ファイルは触らず、不足分のみコピー）。もし `FORCE=1` で上書きした場合は、退避された `<file>.bak.<timestamp>` から復元できる。次回からは `DRY_RUN=1 just install` で事前確認を推奨。

### Codex に `just` 経由でタスクを渡せない

まず `/codex:setup` スキルで認証・CLI 可用性を確認する。`just codex-run` は内部で `.claude/tools/codex/run.py` を呼び、Claude plugin cache の `codex-companion.mjs` を探索する:

- **0 件**: 「Codex plugin がインストールされていません」と表示 → `/codex:setup` を実行
- **複数件**: 最新バージョンを自動選択（選択結果は stderr に表示）
- **node 不在**: PATH を確認

レート制限等で Codex 自体が落ちた場合は、`.tasks/<name>.md` を書いた状態のまま `Agent(isolation: "worktree")` サブエージェントへフォールバックする。詳細は [`.claude/rules/codex-workflow.md`](.claude/rules/codex-workflow.md) を参照。

### スキルが起動しない

```bash
# インストール確認
ls .claude/skills/<name>/SKILL.md

# フロントマターの origin が正しいか
head -5 .claude/skills/<name>/SKILL.md
```

明示起動なら `/skill-name`、自動起動を期待するなら SKILL.md の `description` に発火条件を明確に書く。

---

## 参考

- [affaan-m/ECC](https://github.com/affaan-m/ECC) — 本リポジトリが参考にしている上位互換システム
- [Claude Code ドキュメント](https://docs.claude.com/en/docs/claude-code)
- [Codex CLI](https://github.com/openai/codex)
