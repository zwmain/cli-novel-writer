#!/usr/bin/env python3
"""count_cjk.py — 统计文本文件中的中文字符数（正则 [\\u4e00-\\u9fa5]，标点/空白/拉丁不计）。

用法: count_cjk.py <文件> [--min N] [--max M]
退出码: 0=通过  1=未达区间  2=用法错误  3=文件不可读
"""
from __future__ import annotations

import re
import sys

CJK_RE = re.compile(r"[一-龥]")
MIN_WORDS = 2000  # 每章期望下限（中文字符）
MAX_WORDS = 4000  # 每章期望上限（中文字符）


def count_cjk(text: str) -> int:
    """返回 text 中的中文字符数量。"""
    return len(CJK_RE.findall(text))


def _check_range(count: int, lo: int, hi: int) -> bool:
    """count 是否落在 [lo, hi]（含边界）。"""
    return lo <= count <= hi


def main(argv: list[str]) -> int:
    """CLI 入口。返回退出码，见模块 docstring。"""
    if len(argv) < 2:
        print("用法: count_cjk.py <文件> [--min N] [--max M]", file=sys.stderr)
        return 2
    if argv[1] in ("-h", "--help"):
        print(
            "统计文件中的中文字符数（标点/空白/拉丁不计）\n"
            "用法: count_cjk.py <文件> [--min N] [--max M]",
            file=sys.stderr,
        )
        return 0
    lo, hi, i = MIN_WORDS, MAX_WORDS, 2
    while i < len(argv):
        if argv[i] == "--min" and i + 1 < len(argv):
            lo = int(argv[i + 1])
            i += 2
        elif argv[i] == "--max" and i + 1 < len(argv):
            hi = int(argv[i + 1])
            i += 2
        else:
            print(f"未知参数: {argv[i]}", file=sys.stderr)
            return 2
    try:
        with open(argv[1], encoding="utf-8") as fh:
            count = count_cjk(fh.read())
    except OSError as exc:
        print(f"无法读取文件 {argv[1]}: {exc}", file=sys.stderr)
        return 3
    ok = _check_range(count, lo, hi)
    print(f"{count} 中文字符")
    print("PASS" if ok else f"FAIL: 不在 [{lo}, {hi}] 区间")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
