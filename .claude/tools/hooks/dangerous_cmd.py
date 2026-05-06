#!/usr/bin/env python3
import json, sys

data = json.load(sys.stdin)
command = data.get("tool_input", {}).get("command", "")

patterns = [
    ("rm -rf",           "ディレクトリの強制削除"),
    ("git reset --hard", "コミット履歴の強制リセット"),
    ("git push --force", "リモートへの強制プッシュ"),
    ("git push -f",      "リモートへの強制プッシュ"),
    ("git clean -f",     "未追跡ファイルの強制削除"),
    ("git checkout --",  "ファイルの強制上書き"),
]

for pattern, description in patterns:
    if pattern in command:
        print(f"⚠️ 危険なコマンドを検知: `{pattern}` ({description})")
        print("意図的な場合はターミナルから直接実行してください。")
        sys.exit(2)
