# claude-settings

Claude Code の設定テンプレートリポジトリ。新しいプロジェクトに `git clone` → `just install` で設定一式を展開できる。

## インストール

```bash
cd my-project
git clone <this-repo> claude-settings
cd claude-settings
just install
```

以下がプロジェクトルートにコピーされる：

| ファイル/ディレクトリ | 内容 |
|---|---|
| `.claude/` | フック・ルール・コマンド一式 |
| `CLAUDE.md` | Claude Code へのプロジェクト指示 |
| `justfile` | Codex タスク管理コマンド |

インストール後は `.claude/rules/project.md` をそのプロジェクト用に編集する。

## ディレクトリ構成

```
.claude/
├── commands/          # Claude Code カスタムコマンド (/find-skills, /read-pdf)
├── rules/             # Claude に自動ロードされるルール
│   ├── codex-workflow.md   # Codex/サブエージェント呼び出し手順
│   ├── git-workflow.md     # コミット規約・ブランチ戦略
│   └── project.md          # プロジェクト固有設定（要編集）
├── tools/hooks/       # PreToolUse / PostToolUse フック
│   ├── autoformat.py       # ファイル保存後の自動フォーマット
│   ├── dangerous_cmd.py    # 危険なコマンドのチェック
│   └── protect_settings.py # 設定ファイルの誤編集防止
└── settings.local.json     # パーミッション・フック設定
```

## Codex ワークフロー

```bash
just codex-new-task <name>   # .tasks/<name>.md を作成
# → ファイルを編集してタスク内容を記述
just codex-run <name>        # Codex に渡して実行
just codex-tasks             # 未処理タスク一覧
```

Codex が使えない場合は `.tasks/<name>.md` を書いた上で Claude サブエージェントに委譲する（詳細: `.claude/rules/codex-workflow.md`）。
