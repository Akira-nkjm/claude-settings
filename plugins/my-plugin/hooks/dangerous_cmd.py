#!/usr/bin/env python3
"""PreToolUse hook: 危険な Bash コマンドをブロックする。

settings.local.json 例:
    {"type": "command", "command": "python3 $CLAUDE_PROJECT_DIR/.claude/tools/hooks/dangerous_cmd.py"}
"""
import json
import re
import sys


def warn(msg: str) -> None:
    print(msg, file=sys.stderr)


# 危険コマンドのパターン。各タプルは (正規表現, 説明)
DANGEROUS_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bgit\s+reset\s+--hard\b"), "コミット履歴の強制リセット"),
    (re.compile(r"\bgit\s+push\s+(?:--force\b|-f\b|--force-with-lease\b)"), "リモートへの強制プッシュ"),
    (re.compile(r"\bgit\s+clean\s+-[a-zA-Z]*f"), "未追跡ファイルの強制削除"),
    (re.compile(r"\bgit\s+checkout\s+--\s"), "ファイルの強制上書き"),
    (re.compile(r"\bgit\s+branch\s+-D\b"), "ブランチの強制削除"),
    (re.compile(r"\b(?:sudo\s+)?(?:dd|mkfs|fdisk)\b"), "ディスク操作系コマンド"),
    (re.compile(r":\(\)\s*\{.*\|.*&\s*\}"), "フォーク爆弾の疑い"),
    (re.compile(r"\bchmod\s+-R\s+777\b"), "再帰的な 777 パーミッション"),
    (re.compile(r"\bcurl\s+[^|]*\|\s*(?:sudo\s+)?(?:bash|sh|zsh)\b"), "curl パイプ実行 (任意コード実行)"),
    (re.compile(r"\bwget\s+[^|]*\|\s*(?:sudo\s+)?(?:bash|sh|zsh)\b"), "wget パイプ実行 (任意コード実行)"),
]

# rm に対する特に危険な対象（ブロック対象がパターン本体と重なる場合の追加警告）
RM_CRITICAL_TARGETS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\brm\s+(?:-\S+\s+)*/\s*(?:$|;|&)"), "ルートディレクトリ (/) への rm"),
    (re.compile(r"\brm\s+(?:-\S+\s+)*~(?:/|\s|$)"), "ホームディレクトリ全体への rm"),
    (re.compile(r"\brm\s+(?:-\S+\s+)*\$HOME(?:/|\s|$)"), "$HOME 全体への rm"),
    (re.compile(r"\brm\s+(?:-\S+\s+)*[^\s]*\.ssh(?:/|\s|$)"), ".ssh ディレクトリへの rm"),
    (re.compile(r"\brm\s+(?:-\S+\s+)*[^\s]*\.git(?:/|\s|$)"), ".git ディレクトリへの rm"),
]

RM_COMMAND = re.compile(r"(?<![\w-])rm\s+((?:-[^\s]+\s+)*)")

# 一時ディレクトリ配下は使い捨て領域なので rm -rf を許可する（テスト用 temp の掃除など）
TMP_PREFIXES = ("/tmp/", "/var/tmp/")

# rm 呼び出し1回分（フラグ + 対象）をシェル区切りまで取り出す
RM_INVOCATION = re.compile(r"(?<![\w-])rm\s+([^\n;|&]+)")


def has_recursive_force_rm(command: str) -> bool:
    """Return True only for rm invocations combining -r/-R and -f."""
    for match in RM_COMMAND.finditer(command):
        flags = match.group(1).split()
        has_recursive = any(("r" in flag or "R" in flag) for flag in flags if flag != "--")
        has_force = any("f" in flag for flag in flags if flag != "--")
        if has_recursive and has_force:
            return True
    return False


def _strip_quotes(token: str) -> str:
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        return token[1:-1]
    return token


def rm_targets_all_under_tmp(command: str) -> bool:
    """再帰強制 rm が「すべて /tmp 配下の実パス」だけを対象にしているなら True。

    1つでも tmp 配下でない対象、tmp ルートそのもの、`..` を含む対象、
    変数展開（解決不能）が混じる場合は False（= 通常どおりブロック）。
    """
    saw_recursive_force = False
    for match in RM_INVOCATION.finditer(command):
        tokens = match.group(1).split()
        flags = [t for t in tokens if t.startswith("-")]
        has_recursive = any(("r" in f or "R" in f) for f in flags if f != "--")
        has_force = any("f" in f for f in flags if f != "--")
        if not (has_recursive and has_force):
            continue
        saw_recursive_force = True
        targets = [_strip_quotes(t) for t in tokens if not t.startswith("-")]
        if not targets:
            return False
        for target in targets:
            under_tmp = any(
                target.startswith(prefix) and len(target) > len(prefix)
                for prefix in TMP_PREFIXES
            )
            if not under_tmp or ".." in target:
                return False
    return saw_recursive_force


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        warn(f"hook input JSON parse error: {e}. hook を skip します")
        return 0

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        return 0

    if has_recursive_force_rm(command):
        # /tmp 配下だけを掃除する rm -rf は許可（使い捨て領域）
        if rm_targets_all_under_tmp(command):
            return 0
        warn("⚠️ 危険なコマンドを検知: ディレクトリの強制削除 (rm -rf 系)")
        warn(f"   コマンド: {command}")
        for target_pat, target_desc in RM_CRITICAL_TARGETS:
            if target_pat.search(command):
                warn(f"🚨 さらに重大: {target_desc}")
                break
        warn("意図的な場合はターミナルから直接実行してください。")
        return 2

    for pattern, description in DANGEROUS_PATTERNS:
        if pattern.search(command):
            warn(f"⚠️ 危険なコマンドを検知: {description}")
            warn(f"   コマンド: {command}")
            warn("意図的な場合はターミナルから直接実行してください。")
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
