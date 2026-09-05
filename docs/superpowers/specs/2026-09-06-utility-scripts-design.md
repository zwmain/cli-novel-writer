# 脚本工具集设计（Utility Scripts）

日期：2026-09-06
状态：草案，待用户批准

## 背景与目标

技能包目前只有一个 Python 脚本 `scripts/count_cjk.py`（统计中文字数）。需求方希望增加几个辅助脚本：

1. 文件夹检查 / 校验 / 创建脚本，能识别绝对路径与相对执行目录的相对路径。
2. 文件创建 / 写入脚本，能识别绝对 / 相对路径；路径不存在时有递归创建能力。
3. 所有 py 脚本各实现一份 Node.js 版本，作为 Python 环境不可用时的另一种选择。
4. 脚本定位为「辅助工具」：agent 自带的文件 / 文件夹操作能力优先；环境能满足就用脚本，不能满足就不用（不硬依赖）。

本设计沿用上一特性（project-directory-resolution，见 `2026-09-05-project-directory-resolution-design.md`）的路径解析规则，不重复发明。

## 已确认设计决策

1. **脚本形态**：每个能力一个独立单文件脚本（`check_dir.py` / `write_file.py`），py / node 各一份。沿用 `count_cjk.py` 的退出码约定（0/1/2/3）。py 版写 pytest 单测。
2. **Node 版本**：Node v25.8.1，绝对路径 `C:\Users\zwmai\AppData\Roaming\fnm\node-versions\v25.8.1\installation\node.exe`。node 不在 PATH，测试/文档通过此绝对路径调用，不假设 `node` 在 PATH。
3. **JS 单测**：node 脚本配等价单测，同一套用例参数化跨 py + js 两套实现跑。
4. **辅助定位**：agent 自带文件/文件夹能力优先；脚本是辅助工具，环境满足才用，不满足不用（不做硬依赖）。运行时脚本自身不探测 OS，依赖模型按平台传参。

## 脚本集构成

```
scripts/
├─ count_cjk.py        # 已有，不动
├─ pathresolve.py       # (内部) 绝对/相对路径识别 + 归一化；被 py 脚本共享
├─ check_dir.py        # 校验目录存在 + 判断能否创建（--create 创建）
├─ write_file.py       # 写入文件（父目录缺失→递归创建）
├─ pathresolve.mjs     # Node 镜像（pathresolve.py）
├─ check_dir.mjs       # Node 镜像（check_dir.py）
└─ write_file.mjs      # Node 镜像（write_file.py）
|
tests/
├─ test_count_cjk.py   # 已有
├─ test_check_dir.py
└─ test_write_file.py
```

- `pathresolve.py/.mjs` 为内部共享模块，不直接作为 CLI 调用（无 main / 无 __main__）。被 check_dir / write_file 导入使用。
- count_cjk.py 及现有测试**保持不变**。

## 统一退出码协议（沿用 count_cjk 风格）

| 码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 操作失败（目录不存在 / 无法创建 / 写入失败） |
| 2 | 用法错误（缺参 / 未知参数） |
| 3 | 环境 / IO 错误 |

## CLI 形状

```bash
# 目录：纯检查，不创建。目录存在 → 0；不存在 → 1。
python scripts/check_dir.py <path>

# 目录：检查 + 创建。存在或成功创建 → 0；无法创建 → 1。
python scripts/check_dir.py --create <path>

# 写文件：父目录缺失则递归创建。成功 → 0；失败 → 1。
python scripts/write_file.py --parent <path> <content>

# 辅助：count_cjk（已有）
python scripts/count_cjk.py <文件> [--min N] [--max M]
```

Node 版 CLI 与 py 版逐字一致，仅解释器换 node：
`<node> scripts/check_dir.mjs ...` / `scripts/write_file.mjs ...`。

## 路径解析规则

沿用 project-directory-resolution 的判定表，脚本内部只按字符串特征识别，不探测 OS：

- 绝对路径：Windows `C:\x`、`\\srv\x`；macOS/Linux `/x`。
- 相对路径（Windows）：`x\y`、`.\x`、`..\x`、`x/y`、`./x`、`../x`。
- 相对路径（macOS/Linux）：`x/y`、`./x`、`../x`。
- `~` 展开用户主目录（`os.path.expanduser` / Node `os.homedir`）。
- 相对路径以 cwd 展开。

不展开 `$VAR` / `%VAR%` 环境变量。

## 集成点

1. **SKILL.md「脚本工具」段（约 L155-158）**：扩充。给每个新脚本一句话 + 触发场景（目录检查、目录创建、文件写入）。新增「脚本可用性」原则：agent 自带能力优先，脚本是辅助工具，环境满足才用，不满足不用。
2. **README.md「它会读写文件」/ 依赖段**：提及脚本集与「环境满足才用」原则；测试命令加 node 版。
3. **CLAUDE.md 测试/开发命令段**：加 node 脚本 + 测试说明。

## 测试

- py 脚本：pytest 单测。用例覆盖：绝对 / 相对 / `~` 路径、目录存在 / 不存在 / 可创建 / 不可创建、文件写入、父目录缺失递归创建、退出码（0/1/2/3）、跨 OS 路径识别。
- node 脚本：同一套用例参数化跨实现跑（py + js）。本机用绝对路径 node 跑。
- 现有 `test_count_cjk.py` 保持不变，全绿。

## 边界与不做的事（YAGNI）

- 不做 `$VAR` / `%VAR%` 环境变量展开。
- 不建 `scripts/__init__.py` / 不做包化。
- 不改 count_cjk.py 及现有测试。
- 不做文件删除 / 复制 / 移动（需求未提）。
- 脚本自身不探测 OS、不解析用户的项目根（那是队长的职责，脚本只认路径字符串）。
