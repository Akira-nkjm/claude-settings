# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 自動ロードされるルール (`.claude/rules/`)

- `codex-workflow.md` — Codex 呼び出し手順・並列実行・フォールバック
- `git-workflow.md` — コミットメッセージ規約・ブランチ戦略
- `project.md` — プロジェクト固有の設定（プロジェクトごとに編集）

## 利用可能なコマンド (`.claude/commands/`)

- `/read-pdf <path> [--pages N] [--interval N]` — PDF をページごとに読み込み Markdown サマリーを生成。出力先: `book_analysis/`
- `/find-skills [keyword]` — 利用可能なスキルを検索・一覧表示

## Codex 委譲ワークフロー

実装タスクは **計画 → 承認 → Codex 委譲** の順で進める。呼び出し手順・コマンド・注意事項は `codex-workflow.md` 参照。

Codex が使えない場合は `.tasks/<task-name>.md` にタスクを書いてから `Agent(isolation: "worktree")` でサブエージェントにフォールバック。

## 参照ドキュメント (`.claude/docs/`)

大きめのリファレンスは `.claude/docs/` に置き、必要時に `@.claude/docs/<file>.md` で参照する。

---

@.claude/rules/project.md
