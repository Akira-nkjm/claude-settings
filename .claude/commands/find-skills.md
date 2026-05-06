---
name: find-skills
description: 利用可能な Claude Code スキルをローカル・マーケットプレイス・Web から検索・一覧表示する
---

## When to Activate

ユーザーが「どんなスキルがある？」「〇〇できるスキルは？」と聞いたとき、または `/find-skills` と呼び出したとき。

## 手順

### 1. ローカル検索

**一覧表示:**
```bash
find ~/.claude/commands ~/.claude/skills .claude/commands .claude/skills -name "*.md" 2>/dev/null | sort | while read f; do
  echo "=== $f ==="
  grep -m1 "^description:" "$f" || head -3 "$f"
  echo ""
done
```

**キーワード検索:**
```bash
grep -ril "<keyword>" ~/.claude/commands ~/.claude/skills .claude/commands .claude/skills 2>/dev/null
```

### 2. Claude Code マーケットプレイス

Claude Code の `/plugin` コマンドで Discover タブから検索できる。コミュニティマーケットプレイスを追加する場合:

```
/plugin marketplace add https://github.com/affaan-m/everything-claude-code
```

### 3. Web 検索

WebSearch ツールで以下を検索する:

- `claude code skill <keyword> site:github.com`
- `claude code plugin <keyword>`

主要なコミュニティリソース:
- https://github.com/anthropics/claude-plugins-official — 公式プラグイン
- https://github.com/affaan-m/everything-claude-code — 182+ スキル・48 エージェント
- https://github.com/majiayu000/claude-skill-registry — コミュニティ registry（毎日更新）
- https://claudemarketplaces.com/skills — スキルディレクトリ

## 検索対象まとめ

| 場所 | 方法 |
|------|------|
| ローカル | `find` + `grep` |
| マーケットプレイス | `/plugin` コマンド |
| GitHub | WebSearch で `site:github.com` 検索 |
| コミュニティ | 上記リソースを WebFetch で参照 |

## Anti-patterns

- ローカルになければ即「ない」と判断しない — Web にある可能性が高い
- URL は WebFetch で実際にアクセスして存在確認してから紹介する
