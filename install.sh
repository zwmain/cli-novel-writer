#!/usr/bin/env bash
# install.sh — 安装 cli-novel-writer 到 Claude Skills 目录。
# 用法: ./install.sh [目标目录]
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$HOME/.claude/skills/cli-novel-writer}"
FILES=(SKILL.md README.md LICENSE scripts/count_cjk.py)
copied=0
skipped=0
mkdir -p "$TARGET/scripts"
for rel in "${FILES[@]}"; do
  if [ ! -f "$SRC/$rel" ]; then
    echo "仓库中缺失文件: $rel" >&2
    continue
  fi
  if [ -e "$TARGET/$rel" ]; then
    echo "已存在，跳过: $rel"
    skipped=$((skipped + 1))
  else
    cp "$SRC/$rel" "$TARGET/$rel"
    copied=$((copied + 1))
  fi
done
echo "安装完成: $copied 个文件复制, $skipped 个跳过。目标: $TARGET"
