---
description: 現在のプロジェクトに CLAUDE.md・汎用ルール・Codex 連携機械（.claude/justfile）を展開する
argument-hint: "[--force] [--no-codex]"
allowed-tools: Bash(mkdir:*), Bash(cp:*), Bash(test:*), Bash(ls:*), Bash(touch:*), Read, Edit
---

# setup-project — プロジェクト初期化スキャフォルダ

`my-plugin` プラグインの `templates/` から、現在のプロジェクトに
ルール類・CLAUDE.md・Codex 連携機械を展開する。道具箱（commands / skills / hooks / MCP）は
プラグインから自動で効くので、ここでは **プロジェクト側に物理配置が必要なもの**だけを置く。

## 上書きポリシー（重要）

ファイルを 2 種類に分けて扱う:

| 種別 | 対象 | 既定動作 |
|---|---|---|
| **REFRESH（更新）** | 汎用ルール3本・Codex 機械（プラグインが正典） | **常に最新へ上書き** |
| **KEEP（保護）** | 固有ルール3本・ルート文書（あなたが編集する） | **既存があれば触らない** |

`--force` を付けた場合のみ、KEEP 対象も上書きする。

## 手順

1. **引数を解釈し、テンプレートを展開する。** 次の bash をそのまま実行する:

   ```bash
   FORCE=0; CODEX=1
   case " $ARGUMENTS " in *" --force "*)     FORCE=1;; esac
   case " $ARGUMENTS " in *" --no-codex "*)  CODEX=0;; esac
   SRC="${CLAUDE_PLUGIN_ROOT}/templates"

   refresh() { cp -f "$1" "$2"; }                                  # 常に最新へ
   keep()    { if [ "$FORCE" = 1 ] || [ ! -e "$2" ]; then cp -f "$1" "$2"; fi; }  # 既存は保護

   mkdir -p .claude/rules

   # --- REFRESH: 汎用ルール（プラグインが正 → 常に更新） ---
   refresh "$SRC/rules/git-workflow.md"   .claude/rules/git-workflow.md
   refresh "$SRC/rules/security.md"       .claude/rules/security.md
   refresh "$SRC/rules/codex-workflow.md" .claude/rules/codex-workflow.md

   # --- KEEP: プロジェクト固有（あなたが書く → 既存は保護） ---
   keep "$SRC/rules/project.md"      .claude/rules/project.md
   keep "$SRC/rules/architecture.md" .claude/rules/architecture.md
   keep "$SRC/rules/commands.md"     .claude/rules/commands.md

   # --- KEEP: ルート文書（既存は保護） ---
   keep "$SRC/CLAUDE.md" CLAUDE.md
   keep "$SRC/AGENTS.md" AGENTS.md
   keep "$SRC/RULES.md"  RULES.md
   keep "$SRC/SOUL.md"   SOUL.md

   # --- Codex 機械（--no-codex でスキップ）。run.py / justfile / README は REFRESH ---
   if [ "$CODEX" = 1 ]; then
     mkdir -p .claude/tools/codex .codex .tasks
     refresh "$SRC/codex/justfile"           .claude/justfile
     refresh "$SRC/codex/tools/codex/run.py" .claude/tools/codex/run.py
     refresh "$SRC/codex/codex-README.md"    .codex/README.md
     touch .tasks/.gitkeep
   fi
   ```

   > `cp -n` を使わないので、GNU coreutils の `-n は非推奨` 警告は出ない。

2. **プロジェクト固有の 3 ファイル**を、この後の対話で埋めるよう促す:
   - `.claude/rules/project.md` — プロジェクト概要・スタック
   - `.claude/rules/architecture.md` — アーキテクチャ・データフロー・「なぜ」
   - `.claude/rules/commands.md` — 実際に動くセットアップ/テスト/ビルドコマンド

   ユーザーにプロジェクトの目的・スタック・主要コマンドを尋ね、回答をもとに
   これら 3 ファイルを編集する（汎用ルールはそのままでよい）。

3. 展開したファイル一覧と「次に埋めるべき 3 ファイル」を要約して報告する。
   `--force` なしで再実行した場合、固有ファイルは保護され汎用ルールだけが最新化される旨も伝える。

## Codex の呼び方

justfile は**プロジェクト直下ではなく `.claude/justfile`** にあり、プロジェクト自身の justfile と衝突しない:

```bash
just -f .claude/justfile codex-run <task-name>
# 毎回 -f を打つのが面倒なら:  alias jc='just -f .claude/justfile'  →  jc codex-run <task-name>
```

## 注意

- 道具箱（read-pdf コマンド、各スキル、フック、codegraph MCP）は**プラグイン側で完結**しており、
  このコマンドでコピーする必要はない。物理的には `~/.claude/plugins/cache/.../my-plugin/` に住む。
- フックはプラグインの hooks.json が自動適用される。`CLAUDE_SESSION_PERSIST=1` を設定すると
  セッション永続化フックが動く。
- **codegraph MCP は `/plugin install` で全プロジェクト共通に有効**だが、各プロジェクトで一度
  `just -f .claude/justfile codegraph-init`（= `codegraph init -i`）してインデックスを作る必要がある。
- Codex 実行には `node` と、`/codex:setup` で入る Codex companion プラグインが必要。
