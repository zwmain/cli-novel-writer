#!/usr/bin/env python3
"""check_dir.py — 检查目录是否存在，可选一键创建（纯检查 / 检查+创建）。

用法: check_dir.py <路径> [--create]
退出码: 0=存在/创建成功  1=不存在/无法创建  2=用法错误  3=环境/IO 错误
"""
from __future__ import annotations

import os
import sys

# 保证以 `python scripts/check_dir.py` 或 pytest 方式运行时都能导入同目录共享模块。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathresolve import resolve

USAGE = "用法: check_dir.py <路径> [--create]"


def _print_usage(file: object) -> None:
    print(
        "检查目录是否存在，可选一键创建（嵌套路径一并创建）\n"
        + USAGE,
        file=file,
    )


def main(argv: list[str]) -> int:
    """CLI 入口。返回退出码，见模块 docstring。"""
    if len(argv) < 2:
        print(USAGE, file=sys.stderr)
        return 2
    if argv[1] in ("-h", "--help"):
        _print_usage(sys.stdout)
        return 0
    create = argv[1] == "--create"
    i = 2 if create else 1
    if i >= len(argv):
        print(USAGE, file=sys.stderr)
        return 2
    # 未知 `-` 前缀参数（非 --create/-h/--help）→ 用法错误。
    if argv[i].startswith("-"):
        print(USAGE, file=sys.stderr)
        return 2
    # 超出预期（--create 标志后恰 1 个路径，或无标志恰 1 个路径）的尾随参数 → 用法错误。
    if i + 1 < len(argv):
        print(USAGE, file=sys.stderr)
        return 2
    path = argv[i]
    try:
        cwd = os.getcwd()
    except OSError as exc:
        print(f"无法获取当前工作目录: {exc}", file=sys.stderr)
        return 3
    abs_path = resolve(path, cwd)
    if not create:
        try:
            exists = os.path.isdir(abs_path)
        except OSError:
            exists = False
        if not exists:
            print(f"目录不存在: {abs_path}", file=sys.stderr)
            return 1
        print(abs_path)
        return 0
    try:
        os.makedirs(abs_path, exist_ok=True)
    except OSError as exc:
        print(f"无法创建目录 {abs_path}: {exc}", file=sys.stderr)
        return 1
    print(abs_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))