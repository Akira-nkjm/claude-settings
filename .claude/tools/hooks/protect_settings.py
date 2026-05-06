#!/usr/bin/env python3
import json, sys

data = json.load(sys.stdin)
file_path = data.get("tool_input", {}).get("file_path", "")

protected = ["settings.local.json", "settings.json"]
if any(p in file_path for p in protected):
    print(f"⛔ 設定ファイル ({file_path}) の直接編集はブロックされています。")
    print("変更が必要な場合はユーザーが直接編集してください。")
    sys.exit(2)
