# 開発コマンドリファレンス

> プロジェクトごとに編集するテンプレート。実際に動くコマンドだけを書く（陳腐化防止）。

このリポジトリは Claude Code マーケットプレイス。ビルド/テスト/実行ランタイムは無く、
作業は「プラグイン配布物（Markdown / JSON / Python フック）の編集 + 妥当性チェック」が中心。

## セットアップ

```bash
# 外部依存のインストールは不要（Python フックは標準ライブラリのみ）。
# Codex / codegraph を使う場合のみ実行系が要る:
node -v && python3 --version        # Node.js（Codex companion）・Python3（フック・run.py）
just --version                      # just（.claude/justfile のレシピ実行）
```

## プラグインの導入・更新（利用側）

```bash
# Claude Code セッション内のスラッシュコマンド
/plugin marketplace add Akira-nkjm/claude-settings   # マーケットプレイス登録（初回のみ）
/plugin install my-plugin@my-marketplace             # 道具箱 + codegraph MCP を有効化
/plugin update                                       # 道具箱を最新化（全プロジェクトに反映）
/setup-project                                        # ルール一式・Codex 機械を展開（--force / --no-codex）
```

## 妥当性チェック（テストの代わり）

```bash
# マニフェスト JSON が壊れていないか
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null && echo OK
python3 -m json.tool plugins/my-plugin/.claude-plugin/plugin.json > /dev/null && echo OK
python3 -m json.tool plugins/my-plugin/hooks/hooks.json > /dev/null && echo OK

# 全 JSON を一括検証
find . -name '*.json' -not -path './.git/*' \
  -exec sh -c 'python3 -m json.tool "$1" > /dev/null && echo "OK  $1" || echo "NG  $1"' _ {} \;

# Python フック / スクリプトが構文エラーなくコンパイルできるか
python3 -m py_compile plugins/my-plugin/hooks/*.py \
  plugins/my-plugin/templates/codex/tools/codex/run.py && echo "py OK"

# スキルに SKILL.md が揃っているか
for d in plugins/my-plugin/skills/*/; do
  test -f "$d/SKILL.md" && echo "OK  $d" || echo "MISSING SKILL.md  $d"
done
```

## Codex 連携（.claude/justfile）

```bash
# プロジェクト直下ではなく .claude/justfile を指す（プロジェクト自身の justfile と衝突回避）
just -f .claude/justfile                       # レシピ一覧（default）
just -f .claude/justfile codex-new-task <name> # タスク雛形を .tasks/ に作成
just -f .claude/justfile codex-run <name>      # Codex に実行を委譲
just -f .claude/justfile codex-tasks           # タスク一覧
just -f .claude/justfile codex-run-isolated <name>   # git worktree で隔離実行
just -f .claude/justfile codex-cleanup-isolated <name>
# 毎回 -f が面倒なら:  alias jc='just -f .claude/justfile'  →  jc codex-run <name>
```

## CodeGraph（コード構造インデックス）

```bash
just -f .claude/justfile codegraph-init     # 初回だけ index 作成（= codegraph init -i）
just -f .claude/justfile codegraph-status   # index 状態の確認
```

## ビルド / リリース

```bash
# ビルド成果物は無い。「リリース」= main へマージし、利用側が /plugin update で取得。
# バージョンは plugins/my-plugin/.claude-plugin/plugin.json の "version" を手で更新する。
```

## その他のタスク

- README のスキル一覧・リンクは配布物を変えたら手で更新する
- 配布物の正典は常に `plugins/my-plugin/` 配下（リポ直下の `.claude/` は展開先サンプル）
