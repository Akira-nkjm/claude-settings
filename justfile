default:
    @just --list

# プロジェクトルート（親ディレクトリ）に .claude/ をインストールする
# 使い方: プロジェクト配下に git clone してから just install
install:
    #!/usr/bin/env bash
    dest="$(dirname "$(pwd)")"
    echo "Installing to: $dest"
    cp -r .claude "$dest/"
    cp CLAUDE.md "$dest/CLAUDE.md"
    cp justfile "$dest/justfile"
    if [ -f "$dest/.gitignore" ]; then
        grep -vxFf "$dest/.gitignore" .gitignore >> "$dest/.gitignore" && echo "Merged .gitignore"
    else
        cp .gitignore "$dest/.gitignore"
    fi
    echo "Done. Edit $dest/.claude/rules/project.md for project-specific settings."

# Codex にタスクファイルを渡して実行する
# 使い方: just run <task-name>  (.tasks/<task-name>.md を渡す)
codex-run name:
    node "$(echo $HOME/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs)" task --write --prompt-file ".tasks/{{ name }}.md"

# タスクファイルを新規作成する
# 使い方: just new <task-name>
codex-new-task name:
    @mkdir -p .tasks
    @printf "# {{ name }}\n\n## 概要\n\n## 実装方針\n\n## 注意事項\n" > .tasks/{{ name }}.md
    @echo "Created: .tasks/{{ name }}.md"

# 未処理タスク一覧
codex-tasks:
    @ls .tasks/*.md 2>/dev/null || echo "no task"
