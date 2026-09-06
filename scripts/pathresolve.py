#!/usr/bin/env python3
"""pathresolve.py — 纯函数路径解析共享模块（无 CLI，仅供 check_dir/write_file 导入）。

按 project-directory-resolution 的判定表识别绝对/相对路径并归一化：
- 绝对路径：Windows `C:\\x`、`\\\\srv\\x`；macOS/Linux `/x`。
- 相对路径（Windows）：`x\\y`、`.\\x`、`..\\x`、`x/y`、`./x`、`../x`。
- 相对路径（macOS/Linux）：`x/y`、`./x`、`../x`。
- `~` 展开用户主目录（os.path.expanduser）；不展开 `$VAR` / `%VAR%`。
- 相对路径以 cwd 展开为绝对路径。

本模块为纯字符串/路径逻辑，不探测 OS、不访问文件系统。
"""
from __future__ import annotations

import os
import re

# Windows 绝对路径：驱动器号 + 冒号 + 斜杠（`C:\x`），或 UNC（`\\srv\x`）。
_WIN_ABS_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")
_WIN_ABS_UNC = re.compile(r"^\\\\")


def _detect_is_windows(is_windows: bool | None) -> bool:
    """is_windows 为 None 时按 os.name 自动推断，否则原样返回。"""
    return os.name == "nt" if is_windows is None else is_windows


def is_absolute(p: str, *, is_windows: bool | None = None) -> bool:
    """p 是否为绝对路径（仅按字符串特征识别，不探测 OS）。

    is_windows=None 时自动推断平台；传入 True/False 可强制按 Windows /
    macOS·Linux 规则判定，用于跨平台路径识别。
    """
    if _detect_is_windows(is_windows):
        # Windows：驱动器号（C:\x）或 UNC（\\srv\x）。
        return bool(_WIN_ABS_DRIVE.match(p) or _WIN_ABS_UNC.match(p))
    # macOS/Linux：以 `/` 开头。
    return p.startswith("/")


def normalize(p: str) -> str:
    """归一化路径字符串：去首尾空白与成对引号、展开 `~`。

    不展开环境变量（`$VAR` / `%VAR%`）；`.`/`..` 的折叠由调用方通过
    os.path.abspath 处理，此处不做。
    """
    s = p.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        s = s[1:-1].strip()
    return os.path.expanduser(s)


def resolve(p: str, cwd: str, *, is_windows: bool | None = None) -> str:
    """把 p 解析为绝对路径：先归一化，再按平台规则判定绝对/相对展开。

    绝对 → os.path.abspath；相对 → os.path.abspath(os.path.join(cwd, norm))。
    关键点：Windows 下 `/x` 是相对路径，macOS/Linux 下 `/x` 是绝对路径，
    由 is_windows 旗标消歧。
    """
    norm = normalize(p)
    win = _detect_is_windows(is_windows)
    if is_absolute(norm, is_windows=win):
        return os.path.abspath(norm)
    return os.path.abspath(os.path.join(cwd, norm))
