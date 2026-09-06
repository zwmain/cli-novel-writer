# 脚本工具集实施计划（Utility Scripts）

日期：2026-09-06
来源 spec：`docs/superpowers/specs/2026-09-06-utility-scripts-design.md`（cbbe4fe）
执行方式：Subagent-Driven（SDD）

## 目标

为技能包新增脚本工具集：目录检查/创建（`check_dir`）、文件写入（`write_file`），py 版 + node 版双实现，配 py 单测 + node 单测。路径解析共享模块 `pathresolve`。辅助定位（agent 自带能力优先，环境满足才用）。

## 环境事实（已核实）

- Python 3.13.14（`python` 在 PATH）。
- Node v25.8.1（`node -v` 返回 v25.8.1，在 PATH，由 fnm 管理）。`node` 命令可直接调用。
- 现有脚本 `scripts/count_cjk.py` + `tests/test_count_cjk.py`（10 测试）保持不变。
- 当前分支 `continuation`，工作区干净。

## 验收标准

1. `scripts/` 新增：`pathresolve.py`、`check_dir.py`、`write_file.py`、`pathresolve.mjs`、`check_dir.mjs`、`write_file.mjs`。
2. `tests/` 新增：`test_check_dir.py`、`test_write_file.py`。
3. py 单测全绿：`python -m pytest tests/ -q`。
4. node 单测全绿：同一套用例参数化跨 py + js 跑，本机用 node 绝对路径。
5. 现有 10 个 count_cjk 测试保持全绿。
6. SKILL.md「脚本工具」段、README.md、CLAUDE.md 已按集成点更新。

---

## Task 1 — pathresolve.py（py 共享路径解析模块）

**改动**：新建 `scripts/pathresolve.py`。

**验收**：pytest 通过（`test_pathresolve` 覆盖在 test_write_file 内或以独立文件）。

**实现要点（继承 spec「路径解析规则」与上一特性的判定表）**：

- 纯函数，不探测 OS，不访问文件系统。
- `is_absolute(p: str) -> bool`：Windows 绝对 = `^[A-Za-z]:[\\/]` 或 `^\\\\`；macOS/Linux 绝对 = `^/`。返回 bool。
- `normalize(p: str) -> str`：展开 `~`（`os.path.expanduser`）；不解析环境变量；返回归一化字符串（含 . 和 .. 的拼接由 os.path.abspath 在调用方做，此处仅展开 ~ 并去引号/空白）。返回展开后的路径。
- `resolve(p: str, cwd: str) -> str`：`normalize` 后，若 `is_absolute` 则直接 `os.path.abspath`；否则 `os.path.abspath(os.path.join(cwd, norm))`。返回绝对路径字符串。
- 跨 OS 识别：绝对判定需同时处理 `/`（win 相对、nix 绝对）——**注意**：Windows 下 `/x` 是相对（nix 是绝对）。此判定留给平台调用方传入的 `is_windows` 标志？**不**——按 spec「脚本自身不探测 OS，依赖模型按平台传参」，但 pathresolve 作为纯函数需要知道平台规则。**决策**：`resolve(p, cwd, *, is_windows=None)`，`is_windows=None` 时由 `os.name == 'nt'` 自动推导；模型可显式传 `is_windows=True/False` 覆盖。这样既"不探测"（默认仍自动），又给了平台传参能力。
- 提供 `assert`/类型注释，风格对齐 count_cjk。

**校验**：`python -c "import sys;sys.path.insert(0,'scripts');import pathresolve;print(pathresolve.resolve('~/x','/tmp'))"` 应输出展开后的绝对路径。

## Task 2 — check_dir.py（py 目录检查/创建脚本）

**改动**：新建 `scripts/check_dir.py`。顶部 `sys.path.insert(0, os.path.dirname(__file__))` 以便 `import pathresolve`。

**CLI（沿用 spec）**：
```
python scripts/check_dir.py <path>            # 纯检查 → 0 存在 / 1 不存在
python scripts/check_dir.py --create <path>   # 检查+创建 → 0 存在或已建 / 1 无法创建
python scripts/check_dir.py --help            # → 0 打印用法
```
退出码：0=存在/成功 1=不存在/无法创建 2=用法错误 3=环境/IO 错误。

**实现要点**：
- `main(argv) -> int`。
- 解析 `<path>`（必须）、`--create` 开关。
- 用 `pathresolve.resolve` 得绝对路径。
- 存在性：`os.path.isdir`。创建：`os.makedirs(..., exist_ok=True)`，捕获 `OSError` → 1。
- `import pathresolve` 需 sys.path 引导。

**校验**：
```
python -c "import sys;sys.path.insert(0,'scripts');import check_dir;print(check_dir.main(['check_dir.py','nope']))"  # 0 之前 1
python scripts/check_dir.py --create /tmp/cd_test/x/y   # 存在/创建
python scripts/check_dir.py --create /tmp/cd_test/x/y   # 再次 → 0 幂等
```

## Task 3 — write_file.py（py 文件写入脚本）

**改动**：新建 `scripts/write_file.py`。同 Task 2 的 sys.path 引导。

**CLI（默认递归创建，spec 决策 5）**：
```
python scripts/write_file.py <path> <content>   # 写入；父目录缺失→递归创建
python scripts/write_file.py --help             # → 0
```
退出码：0=成功 1=写入失败 2=用法错误 3=IO/环境错误。

**实现要点**：
- `main(argv) -> int`。
- 取 `<path>`、`<content>` 两参。content 可含多行、任意字符（不做转义）。
- `pathresolve.resolve` 得绝对路径。
- 父目录递归创建：`os.makedirs(os.path.dirname(abs), exist_ok=True)`。
- 写入：`open(abs, 'w', encoding='utf-8').write(content)`，捕获 `OSError` → 1。
- 内容为空字符串也应成功（写空文件）。

**校验**：
```
python scripts/write_file.py /tmp/wf_test/a/b/c.txt "你好\n世界"
cat /tmp/wf_test/a/b/c.txt    # 应输出内容，父目录 a/b 已自动创建
```

## Task 4 — pathresolve.mjs（node 共享路径解析模块）

**改动**：新建 `scripts/pathresolve.mjs`。

**实现要点**：镜像 `pathresolve.py`。
- `isAbsolute(p)`：win 绝对 `^[A-Za-z]:[\\/]` 或 `^\\\\`；nix 绝对 `^/`。
- `resolve(p, cwd, {isWindows})`：`isWindows` 未传时用 `os.platform()==='win32'` 自动推导。展开 `~`（`os.homedir()`）。不解析环境变量。返回 `path.resolve(...)` 绝对路径。
- 用 `export` 导出；`import { isAbsolute, resolve } from './pathresolve.mjs'`。
- 顶层 `import os from 'node:os'`、`import path from 'node:path'`。

**校验**（`node` 在 PATH）：
```
node -e "import('./scripts/pathresolve.mjs').then(m=>console.log(m.resolve('~/x','/tmp')))"
```

## Task 5 — check_dir.mjs + write_file.mjs（node CLI 脚本）

**改动**：新建 `scripts/check_dir.mjs`、`scripts/write_file.mjs`。

**实现要点**：镜像 py 版，CLI 逐字一致（仅解释器换 node）。
- `check_dir.mjs`：`import { isAbsolute, resolve } from './pathresolve.mjs'`；`process.argv` 解析 `<path>`、`--create`；`fs.existsSync`/`fs.mkdirSync(p,{recursive:true})`；退出码 0/1/2/3 对齐 py。
- `write_file.mjs`：`import { resolve } from './pathresolve.mjs'`；`fs.mkdirSync(dirname,{recursive:true})` 后 `fs.writeFileSync(abs, content, 'utf-8')`；退出码对齐。
- 从 stdin 或 argv 取 content？——**决策**：content 作为 argv 位置参数（与 py 一致，`process.argv[3]`）。支持多行：shell 引号传换行。不做 stdin 模式（YAGNI）。
- 顶层 shebang `#!/usr/bin/env node` + `process.exitCode = main(...)` 风格（Node 惯例）。

**校验**：与 py 版同 CLI 跑一遍，退出码一致。

## Task 6 — test_check_dir.py + test_write_file.py（py + node 参数化单测）

**改动**：新建 `tests/test_check_dir.py`、`tests/test_write_file.py`（内含对 py 版子进程测 + node 版子进程测）。

**实现要点**：
- **不 import 函数**（要测真实副作用 + 退出码），用 `subprocess.run([sys.executable, 'scripts/check_dir.py', ...])` 跑 py 版；`subprocess.run(['node', 'scripts/check_dir.mjs', ...])` 跑 node 版（`node` 在 PATH）。
- Node 可用性守卫：若 `shutil.which('node') is None` 则 `pytest.skip('node 不可用')`（跨平台，不在 PATH 时跳过，不硬编码绝对路径）。
- 用例（同一套，参数化 cross py/js）：
  - check_dir：目录存在 → 0；不存在 → 1；`--create` 不存在 → 0 且创建；`--create` 已存在 → 0 幂等；无参数 → 2；相对路径（以 tmp_path 为 cwd）→ 正确识别。
  - write_file：写文件成功 → 0 且内容正确；父目录缺失 → 自动创建且 0；空内容 → 0 空文件；无参数 → 2；相对路径 → 写对位置。
- 测试内 `cwd=` 用 `tmp_path` 相对路径验证相对解析。
- 风格对齐 test_count_cjk：顶部 `sys.path.insert`。

**校验**：`python -m pytest tests/ -q` 全绿（py + node 都跑）。`python -m pytest tests/ -q -k node` 仅 node；`-k "not node"` 仅 py。

## Task 7 — 集成：SKILL.md / README.md / CLAUDE.md 脚本工具段

**改动**：更新 3 个文档。

**SKILL.md「脚本工具」段（L155-158）**替换为：
```
## 脚本工具（辅助，环境满足才用）
- `scripts/count_cjk.py`：统计中文字符数。Windows 用 `python scripts/count_cjk.py <文件>`，macOS/Linux 用 `python3 scripts/count_cjk.py <文件>`；可选 `--min N --max M`。用于文笔自检与复核判决。
- `scripts/check_dir.py` / `check_dir.mjs`：校验目录存在，`--create` 时创建。`python scripts/check_dir.py [--create] <path>`（node 同 CLI）。
- `scripts/write_file.py` / `write_file.mjs`：写入文件，父目录缺失自动递归创建。`python scripts/write_file.py <path> <content>`（node 同 CLI）。
- 路径：绝对 / 相对 cwd / `~` 均可识别；相对以 cwd 展开。
- **脚本可用性**：agent 自带文件/文件夹操作能力优先；脚本是辅助工具，环境满足（有 python 或 node）才用，不满足则用 agent 自带能力，不做硬依赖。
```
（注意：这里出现的 `<content>`、`--create` 等是参数说明，**不含**被 NO_OUTPUTS_REF 门控的 `outputs` 字符串。）

**README.md**：在「它会读写文件」/ 依赖段补一段脚本集 + 环境满足才用原则；测试命令段加 node 跑法。

**CLAUDE.md**：测试/开发命令段加 node 脚本说明 + node 单测跑法。

## Task 8 — 收尾验证

**改动**：无代码改动，只验证。

**校验**：
1. `python -m pytest tests/ -q` → 全绿（count_cjk 10 + check_dir + write_file 的 py & node 用例）。
2. `git status --short` → 仅新增 scripts/ + tests/ + 文档改动，无多余文件。
3. SKILL.md / README.md / CLAUDE.md 三个文档都提到 check_dir、write_file、脚本可用性原则。
4. `pathresolve` 被 py + node 版本正确引用（无 import 错误）。

---

## 部署检查（SDD）

- Node 定位通过 `node`（在 PATH）；不可用时 `pytest.skip`。不硬编码绝对路径进脚本逻辑或测试。
- 每个 Task 走 brief → report → review → fix 循环。
- 汇总验收：`python -m pytest tests/ -q` 全绿；git clean；文档三处一致。
