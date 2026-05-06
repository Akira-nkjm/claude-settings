# Codex 呼び出し手順

## セットアップ → 実行の2ステップ

### Step 1: `/codex:setup` スキルで初期化
認証・CLI の可用性を確認。成功するまで Step 2 に進まない。

### Step 2: `just` でタスクを渡す

```bash
# 1. タスクファイルを作成（または Write ツールで直接 .tasks/<name>.md を書く）
just codex-new-task <task-name>

# 2. 内容を編集後、Codex に渡して実行
just codex-run <task-name>
```

> ⚠️ **`--model` は明示指定が必要な場合は直接 node を呼ぶ**
> `just codex-run` は `--model` 未指定。モデルを固定したい場合は justfile を編集するか直接 node を呼ぶこと。

> ⚠️ **`Bash(just *)` は `.claude/settings.local.json` で pre-approve 済み — 確認プロンプトは出ない**

> ⚠️ **`Agent(subagent_type: "codex:codex-rescue")` は使わない**
> サブエージェントは親セッションの Bash 許可リストを継承しないため `just` / `node` が毎回ブロックされる。Bash ツールから直接呼ぶこと。

## 並列実行フロー

```
/codex:setup スキル実行（完了待ち）
  ↓
Write ツールで .tasks/ にタスクファイルを書く:
  .tasks/task-a.md
  .tasks/task-b.md
  ↓
run_in_background: true で複数 Bash を並列起動:
  Bash: just codex-run task-a
  Bash: just codex-run task-b
  ↓
完了通知が届いたら結果を確認
  ↓
タスクファイルを削除:
  Bash: rm .tasks/task-a.md .tasks/task-b.md
```

## Codex に委譲しないケース（Claude が直接対応）

- コードの読み取り・説明・アーキテクチャ回答
- ドキュメント・設定ファイルの作成
- 単一ファイルの単純な編集
- 詳細な変更計画が既に書かれた構造的なファイル操作

## Codex が利用制限の場合 → Claude サブエージェントにフォールバック

Codex の利用制限（レート制限・認証エラー・応答なし）が発生した場合は、**タスクファイルを `.tasks/` に書いてから `Agent` ツールでサブエージェントに委譲する**。

### フォールバック手順

1. `/codex:setup` の失敗・エラー出力でレート制限を検知したらユーザーに通知
2. `Write` ツールで `.tasks/<task-name>.md` にタスク内容を書き出す
3. `Agent` ツールでサブエージェントにタスクファイルの内容を渡して実装を委譲する

```
# Step 1: タスクファイルを書く（just codex-new-task と同等）
Write(".tasks/<task-name>.md", "<タスク内容>")

# Step 2: サブエージェントに委譲（タスクファイルの内容を prompt に展開して渡す）
Agent({
  description: "タスクの短い説明",
  isolation: "worktree",   // コード変更を伴う場合は worktree を使う
  prompt: "<.tasks/<task-name>.md の内容をそのまま貼る>"
})

# Step 3: 完了後にタスクファイルを削除
Bash("rm .tasks/<task-name>.md")
```

### フォールバック時の注意点

- タスクファイルを先に書くことで、Codex 復帰後に `just codex-run <task-name>` で再試行できる
- `isolation: "worktree"` を付けることで、変更がメインの worktree を汚さない
- 変更なしで終了した場合は worktree が自動クリーンアップされる
- 変更ありの場合はブランチ名が返るので、内容を確認してからマージする
- 並列実行したい場合は複数の `Agent` 呼び出しを同一メッセージに並べる（Codex の並列フローと同様）
