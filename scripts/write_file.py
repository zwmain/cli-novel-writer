#!/usr/bin/env python3
"""write_file.py — 写入文件，父目录缺失时默认递归创建（无需开关）。

用法: write_file.py <路径> <内容>
退出码: 0=写入成功  1=写入失败  2=用法错误  3=环境/IO 错误
"""
from __future__ import annotations

import os
import sys

# 保证以 `python scripts/write_file.py` 或 pytest 方式运行时都能导入同目录共享模块。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathresolve import resolve

USAGE = "用法: write_file.py <路径> <内容>"


def _print_usage(file: object) -> None:
    print(
        "写入文件（父目录缺失时递归创建；内容可含多行，不做转义）\n"
        + USAGE,
        file=file,
    )


def main(argv: list[str]) -> int:
    """CLI 入口。返回退出码，见模块 docstring。"""
    if len(argv) != 3:
        if len(argv) == 2 and argv[1] in ("-h", "--help"):
            _print_usage(sys.stdout)
            return 0
        print(USAGE, file=sys.stderr)
        return 2
    path, content = argv[1], argv[2]
    try:
        cwd = os.getcwd()
    except OSError as exc:
        print(f"无法获取当前工作目录: {exc}", file=sys.stderr)
        return 3
    abs_path = resolve(path, cwd)
    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as fh:
            fh.write(content)
    except OSError as exc:
        print(f"无法写入文件 {abs_path}: {exc}", file=sys.stderr)
        return 1
    print(abs_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
