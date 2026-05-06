default:
    @just --list

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
