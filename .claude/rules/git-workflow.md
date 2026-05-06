# Git ワークフロー

## コミットメッセージ

```
<type>: <概要（50文字以内）>

<本文（任意）>
```

type: `feat` / `fix` / `docs` / `refactor` / `test` / `chore`

- 現在形・命令形で書く（"add" not "added"）
- 本文には「何を」でなく「なぜ」を書く

## ブランチ戦略

```
main          ← 常に動く状態を保つ
feature/<name>  ← 新機能
fix/<name>      ← バグ修正
chore/<name>    ← 設定・依存更新
```

- `main` への直接 push は禁止
- PR はレビュー後にマージ

## 禁止事項

- `git push --force` を `main` に対して実行しない
- `git commit --no-verify` でフックをスキップしない
- バイナリや生成ファイルをコミットしない（`.gitignore` で除外）

## よく使うコマンド

```bash
git status
git diff --staged          # コミット前の確認
git log --oneline -10      # 直近の履歴確認
git stash / git stash pop  # 作業の一時退避
```
