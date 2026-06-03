# Root justfile
#
# Codex 連携 / codegraph などのレシピ本体は .claude/justfile にある。
# import で取り込むことで `just <recipe>`（-f 不要）で呼べて、シェル補完も効く。
# .claude/justfile は cwd を source_directory() から求めるので、import でも cwd は
# 正しくリポルートに揃う。
#
# 使い方（プロジェクトルートから）:
#   just                       # レシピ一覧
#   just codegraph-sync        # 例: codegraph index を差分更新
#   just codex-run <task-name>
#
# プロジェクト独自のレシピを足す場合は、このファイルに直接書けば共存できる。

# import 先（.claude/justfile）にも default があるので、後勝ちで上書きできるようにする
set allow-duplicate-recipes := true

import '.claude/justfile'

# 既定: レシピ一覧を表示（import 先の default を上書き）
default:
    @just --list
