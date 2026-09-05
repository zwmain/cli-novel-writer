# cli-novel-writer 项目目录解析 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 cli-novel-writer skill 支持用户指定项目根目录（绝对/相对/`~`），未指定时默认建在 cwd 下 `日期-项目名/`（去掉 `outputs/` 层），并通过 `项目索引.md` 支持跨会话续写回查。

**Architecture:** 纯文本/Markdown 改动（skill 规则层，无 Python 逻辑）。路径解析规则只定义在 SKILL.md「本地存储规范」一处，其他文件引用它；新增「第零步」在启动流程中解析项目根、建目录、写 `项目索引.md`；派单协议声明「数据来源/产出写回」一律从项目根展开。

**Tech Stack:** Markdown 文档编辑（无代码逻辑改动）。`scripts/count_cjk.py` 与 pytest 不受影响。

**Spec:** `docs/superpowers/specs/2026-09-05-project-directory-resolution-design.md`

## Global Constraints

- 指定的目录 = **项目根**（`叙事宪法.md`/`人物档案.json`/`第1章-v1.md` 等直接建在指定目录下，不再追加 `日期-项目名` 层）。
- 未指定目录 → 默认 `cwd/日期-项目名/`（日期 `YYYY-MM-DD`；**删除**「若已有 outputs 则放 outputs」逻辑，全文不再出现 `outputs/` 层）。
- 路径解析支持：相对（cwd 展开）+ 绝对 + `~` 展开；**不做环境变量展开**（`$VAR`/`%VAR%`）。
- 跨平台判定表（win 含 `x\y`/`.\x`/`..\x` 反斜杠相对、`/` 开头非盘符当相对；unix 以 `/` 为绝对）是唯一权威；模型不需要运行时 OS 检测。
- 跨会话回查：项目根内落 `项目索引.md`，`项目根目录` 字段一定写**绝对路径**；续写先找 cwd 的 `项目索引.md`，找不到再问用户。
- 不改 `scripts/count_cjk.py` 及测试；不新增 Python 脚本。
- 所有文件用中文书写（与现有 SKILL.md 一致）。

---

## Task 1: SKILL.md 派单协议 — 声明路径从项目根展开

**Files:**
- Modify: `SKILL.md`（派单协议段，约 12-18 行与 22-37 行）

**Interfaces:**
- Consumes: 现状 SKILL.md（已读；`## 你的核心工作方式：派单` 小结铁律在 18 行；`## 派单协议` 三块在 22-37 行）。
- Produces: 派单协议中新增「路径从项目根展开」的约束行。Task 3（本地存储规范重写）定义「项目根」；本任务只在派单协议加声明，不重复定义规则。

- [ ] **Step 1: 在「你的核心工作方式：派单」小结铁律后新增一行**

在 SKILL.md:18 的「铁律：数据靠文件传，不靠对话传；一次只派一件事；写正文时只派「文笔」子代理，别让它同时管设定或复核。」之后，加一行：

```markdown
路径约束：派单的「数据来源 / 产出写回」路径一律从**项目根**展开（项目根由「本地存储规范」解析，见下）；子代理只按给定路径读写，不自行推断目录。
```

- [ ] **Step 2: 在「派单协议」第 3 块补充路径原则**

在 SKILL.md:26 第 3 块「数据来源：读哪个文件的哪一部分（给出路径范围）、产出写回哪个文件（给出路径）。」之后，加一行：

```markdown
3. 数据来源：读哪个文件的哪一部分（给出路径范围）、产出写回哪个文件（给出路径）。**路径一律从项目根展开**——项目根由启动流程解析（用户指定或默认，见「本地存储规范」），子代理只按给定路径读写。
```

（上面第 1 步的「路径约束」行与第 2 步的「路径一律从项目根展开」是同一原则在派单协议两处的一致性表述；三处定义（派单协议 2 处 + 本地存储规范 1 处）必须一致。）

- [ ] **Step 3: 校验无残留「outputs」引用**

```bash
grep -n "outputs" SKILL.md || echo "NO_OUTPUTS_REF"
```

Expected: `NO_OUTPUTS_REF`（SKILL.md 在本 Task 后不得出现 outputs 字样；若仍有，属后续 Task 的存储规范区，见 Task 2。）

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "docs: dispatch paths resolve from project root"
```

---

## Task 2: SKILL.md 本地存储规范 — 重写为项目根 + 路径解析

**Files:**
- Modify: `SKILL.md`（`## 本地存储规范` 段，约 68-92 行：68-77 列表 + 78-92 JSON Schema 保留）

**Interfaces:**
- Consumes: Task 1 已在派单协议声明「路径从项目根展开」；本任务在本地存储规范**唯一定义**路径解析规则（整个 plan 的权威来源，其他 Task 引用它）。
- Produces: `## 本地存储规范` 重写为「项目根目录解析规则（§1）+ 项目索引.md（§2）+ 必备文件列表」。Task 3 的「第零步」、Task 4 README、Task 5 CLAUDE.md 都引用这里的规则。

- [ ] **Step 1: 重写「本地存储规范」标题与开头两段**

把 SKILL.md:68-70：

```markdown
## 本地存储规范

每开一个新小说项目，在你的工作目录下建项目文件夹（若工作目录下已有 outputs 目录则放进 outputs），形如 outputs/日期-项目名/，内含：
```

替换为：

```markdown
## 本地存储规范

每开一个新小说项目的项目根目录按以下规则解析（**这是项目目录的唯一权威定义**，派单协议与启动流程都引用这里）：

- **用户指定** → 该路径即项目根（绝对路径直接用；相对路径以 cwd 展开；`~` 展开用户主目录）。判定规则见下方跨平台表。
- **未指定**（用户只给题材、未提路径，或明确说「不指定/随便」）→ `cwd/日期-项目名/`（日期格式 `YYYY-MM-DD`）。

项目根下直接存放以下文件（不再有 `outputs/` 层）：
```

- [ ] **Step 2: 加入「路径解析判定表」与要点**

在 Step 1 的列表（69 行原列表内容，见 Step 3）之前、Step 1 末段之后，插入：

```markdown
### 路径解析判定表（跨平台；模型按所在平台取对应列，一次判定命中即止）

| 输入形式 | Windows 判定 | macOS/Linux 判定 |
|---|---|---|
| `~` / `~/xxx` | 主目录（绝对） | 主目录（绝对） |
| `C:\x`、`C:/x`、`\\srv\x` | 绝对 | 视为相对（罕见）→ 拼 cwd |
| `/x` | 相对（`/` 开头非盘符） | 绝对 |
| `x\y`、`.\x`、`..\x` | 相对（反斜杠分隔） | 视为相对 → 拼 cwd |
| `x/y`、`./x`、`../x` | 相对 | 相对 |

要点：
- 相对/绝对判定**只看输入字符串特征**，不依赖「当前 OS」猜测；`..`（`../` 或 `..\`）跨层级回退在规范化解析后保留，超出文件系统根则报错请用户修正。
- 用户给了**任意路径字符串**（相对/绝对/`~`，即使形如 `2026-09-05-书名`）→ 按表解析并作为项目根；只有「未指定」才走默认规则。
```

- [ ] **Step 3: 更新必备文件列表（去 outputs 层 + 加项目索引.md）**

把 SKILL.md:72-77 原列表：

```markdown
- `叙事宪法.md` ：核心冲突、禁用项、硬性约束。
- `世界规则白皮书.md` ：物理法则、地理、货币、种族、战力天花板与差值。
- `人物档案.json` ：按 Schema 存每个角色。
- `伏笔台账.md` ：表格【伏笔ID｜埋设章节｜具体描述｜计划回收章节｜当前状态】（待回收/已回收/已废弃）。
- `章节目录.md` ：每章当前最新版本号 + 一句话梗概。
- 章节正文：每章单独文件，见下「章节版本管理」。
```

替换为（在列表第一项前插入 `项目索引.md`）：

```markdown
- `项目索引.md` ：项目名 / 创建日期 / 项目根（绝对路径）。见下「项目索引与续写回查」。
- `叙事宪法.md` ：核心冲突、禁用项、硬性约束。
- `世界规则白皮书.md` ：物理法则、地理、货币、种族、战力天花板与差值。
- `人物档案.json` ：按 Schema 存每个角色。
- `伏笔台账.md` ：表格【伏笔ID｜埋设章节｜具体描述｜计划回收章节｜当前状态】（待回收/已回收/已废弃）。
- `章节目录.md` ：每章当前最新版本号 + 一句话梗概。
- 章节正文：每章单独文件，见下「章节版本管理」。
```

- [ ] **Step 4: 新增「项目索引与续写回查」小节**

在 Step 3 列表之后、原「人物档案 JSON Schema（人物子代理专用，示例）：」之前，插入：

```markdown
### 项目索引与续写回查

项目根下放一个 `项目索引.md`（启动流程第零步创建），内容：

```markdown
# 项目索引
- 项目名：
- 创建日期：YYYY-MM-DD
- 项目根目录：（绝对路径）
- 状态文件：叙事宪法.md / 世界规则白皮书.md / 人物档案.json / 伏笔台账.md / 章节目录.md / 第N章-vX.md
```

- `项目根目录` 字段一定写**绝对路径**（win: `C:\...`，unix: `/...`），即便用户当初给的是相对路径——换 cwd 后仍能唯一回查。
- 回查规则（用户说「继续上次小说 / 续写」时）：① 先在 **cwd** 找 `项目索引.md`，找到 → 以其 `项目根目录` 为项目根；② 找不到 → 问用户「上次项目目录在哪？」，用户给指即用；③ 用户指定了新路径且该路径下已有 `项目索引.md` → 直接重用该索引继续。
```

- [ ] **Step 5: 校验「outputs」不再出现**

```bash
grep -n "outputs" SKILL.md || echo "NO_OUTPUTS_REF"
```

Expected: `NO_OUTPUTS_REF`

- [ ] **Step 6: 校验 Markdown 片段嵌套正确（内层代码块用 3 反引号转义）**

```bash
python - <<'PY'
import pathlib
t = pathlib.Path('SKILL.md').read_text(encoding='utf-8')
print('outputs refs:', t.count('outputs'))
print('has 项目索引.md:', '项目索引.md' in t)
print('has 路径解析判定表:', '路径解析判定表' in t)
print('fence balance:', t.count('```') % 2 == 0)
PY
```

Expected: `outputs refs: 0`、`has 项目索引.md: True`、`has 路径解析判定表: True`、`fence balance: True`

- [ ] **Step 7: Commit**

```bash
git add SKILL.md
git commit -m "docs: rewrite storage spec with project root resolution and project index"
```

---

## Task 3: SKILL.md 启动流程 — 新增第零步（解析根目录 + 建目录 + 写索引）

**Files:**
- Modify: `SKILL.md`（`## 启动流程` 段，约 101-107 行）

**Interfaces:**
- Consumes: Task 2 在「本地存储规范」定义的路径解析规则（判定表 + 默认规则）与 `项目索引.md` 回查规则。
- Produces: 启动流程第零步（在用户给题材/梗概后、三步走之前）——解析项目根、创建目录、写/读 `项目索引.md`。

- [ ] **Step 1: 在「启动流程」开头新增「第零步」**

把 SKILL.md:101-103：

```markdown
## 启动流程（每次开新项目必须遵守）

用户给题材/梗概或说「开始」后，按三步走，每步完成后先向用户汇报、等确认再继续：
```

替换为：

```markdown
## 启动流程（每次开新项目必须遵守）

用户给题材/梗概或说「开始」后，按以下步骤走，每步完成后先向用户汇报、等确认再继续：

第零步：解析项目根目录（规则见「本地存储规范」；用户指定或默认）→ 创建该目录 → 若该路径下已有 `项目索引.md` 则读回作为「继续该项目」；否则新建 `项目索引.md` 并写入项目名、创建日期（`YYYY-MM-DD`）、`项目根目录`（绝对路径）。此后所有派单的「数据来源 / 产出写回」路径都从项目根展开。
`
```

- [ ] **Step 2: 校验「第零步」存在且后续仍有三步**

```bash
grep -n "第零步\|第一步：派「世界」\|第二步：草案通过后\|第三步：全部就绪后" SKILL.md
```

Expected: 四行都命中（第零步新增、三步行保留）。

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "docs: add step-zero project root resolution to startup flow"
```

---

## Task 4: README.md 同步 — 项目根模型 + 指定目录支持

**Files:**
- Modify: `README.md`（「它会读写文件」一节，约 46-61 行）

**Interfaces:**
- Consumes: Task 2 的本地存储规范（项目根解析规则）。
- Produces: README 反映项目根模型，去掉 outputs 层、加 `项目索引.md`、说明支持指定目录。

- [ ] **Step 1: 更新「它会读写文件」一节**

把 README.md:46-61：

```markdown
## 它会读写文件

每开一个新小说，在工作目录建项目文件夹 outputs/日期-项目名/：

```
├─ 叙事宪法.md          核心冲突、禁用项、硬性约束
├─ 世界规则白皮书.md    世界设定全记录（含战力天花板与差值）
├─ 人物档案.json        每个角色的「灵魂四维」档案
├─ 伏笔台账.md          伏笔埋设/回收状态表
├─ 章节目录.md          每章最新版本 + 一句话梗概
├─ 第1章-v1.md          第一章正文（带版本号）
├─ 第1章-v2.md          改过的第二版
└─ 第1章-vN.md          改过的第N版
```

（Python 可选：`scripts/count_cjk.py` 客观统计中文字数；无 Python 时模型估算并标注「估算」。）
```

替换为：

```markdown
## 它会读写文件

项目根目录由「本地存储规范」解析：用户指定（绝对 / 相对 cwd / `~`）则该路径即项目根；未指定则建在工作目录下 `日期-项目名/`。项目根下直接存放：

```
├─ 项目索引.md          项目名/创建日期/项目根（绝对路径），供续写回查
├─ 叙事宪法.md          核心冲突、禁用项、硬性约束
├─ 世界规则白皮书.md    世界设定全记录（含战力天花板与差值）
├─ 人物档案.json        每个角色的「灵魂四维」档案
├─ 伏笔台账.md          伏笔埋设/回收状态表
├─ 章节目录.md          每章最新版本 + 一句话梗概
├─ 第1章-v1.md          第一章正文（带版本号）
├─ 第1章-v2.md          改过的第二版
└─ 第1章-vN.md          改过的第N版
```

（Python 可选：`scripts/count_cjk.py` 客观统计中文字数；无 Python 时模型估算并标注「估算」。）
```

- [ ] **Step 2: 校验 README 无「outputs」残留**

```bash
grep -n "outputs" README.md || echo "NO_OUTPUTS_REF"
```

Expected: `NO_OUTPUTS_REF`

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: sync README with project root model and custom directory support"
```

---

## Task 5: CLAUDE.md 同步 — Project output 更新

**Files:**
- Modify: `CLAUDE.md`（「Project output」段，约 26 行）

**Interfaces:**
- Consumes: Task 2 的本地存储规范（项目根 + 项目索引.md）。
- Produces: CLAUDE.md 的 project-output 描述与最新规则一致。

- [ ] **Step 1: 更新「Project output」段**

把 CLAUDE.md:26：

```markdown
- **Project output**: when a novel is started, the队长 creates `outputs/日期-项目名/` with 叙事宪法/世界规则白皮书/人物档案.json/伏笔台账/章节目录/章节正文 (`第N章-vX.md`, versioned — never overwrite, only add higher X).
```

替换为：

```markdown
- **Project output**: when a novel is started, the队长 resolves the 项目根 directory (user-specified — absolute/relative cwd/`~` — or default `cwd/日期-项目名/`), writes `项目索引.md` (project name, created date, **absolute** root path) for resume-lookup, and creates 叙事宪法/世界规则白皮书/人物档案.json/伏笔台账/章节目录/章节正文 (`第N章-vX.md`, versioned — never overwrite, only add higher X). Path resolution rules live only in SKILL.md's 本地存储规范.
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: sync CLAUDE.md with project root resolution"
```

---

## Task 6: 全仓一致性校验

**Files:**
- Read/校验: 全仓

**Interfaces:**
- Consumes: Task 1-5 全部。
- Produces: 验证结果报告，无产出文件。

- [ ] **Step 1: 校验「outputs」全仓无残留（除 spec/plan 历史文档）**

```bash
grep -rn "outputs" SKILL.md README.md CLAUDE.md || echo "NO_OUTPUTS_REF"
```

Expected: `NO_OUTPUTS_REFe`（SKILL.md/README.md/CLAUDE.md 三个活跃文档均无 outputs；docs/superpowers 下历史 spec/plan 属已提交历史，允许保留。）

- [ ] **Step 2: 校验 SKILL.md / README.md 均提到「项目索引.md」**

```bash
grep -c "项目索引" SKILL.md README.md
```

Expected: 两个数字都 >= 1。

- [ ] **Step 3: 校验 SKILL.md 内相对链接可解析**

```bash
python - <<'PY'
import re, pathlib
root = pathlib.Path('.')
skill = (root/'SKILL.md').read_text(encoding='utf-8')
links = re.findall(r'\]\(([^)#]+)', skill)
bad = [l for l in links if not (root/l).exists() and not l.startswith('http')]
print('BAD LINKS:', bad if bad else 'none')
PY
```

Expected: `BAD LINKS: none`

- [ ] **Step 4: 跑原测试确认 count_cjk 未受影响**

```bash
python -m pytest tests/test_count_cjk.py -q
```

Expected: 全部通过（原逻辑未动）。

- [ ] **Step 5: 验证路径解析规则唯一来源**

```bash
grep -rn "路径解析判定表\|项目根目录解析规则" SKILL.md
```

Expected: 出现于 SKILL.md「本地存储规范」一处（唯一权威定义）。

- [ ] **Step 6: 全仓库 git 状态干净**

```bash
git status --short
```

Expected: 无未提交改动（除已提交 docs/）。

---

## Self-Review 记录

- **Spec coverage**: §1（路径解析）→ Task 1+2; §2（项目索引 回查）→ Task 2; §3（集成点：派单协议/存储规范/启动流程/README/CLAUDE.md）→ Task 1/2/3/4/5; §4 边界 → Global Constraints; §5 迁移 → Task 2 说明（无强制迁移动作）。
- **Placeholder scan**: 无 TODO/TBD；每个 Task 的「旧→新」文本逐字给出（含反引号、表格、`项目索引.md` 代码块内层用 4 反引号转义——Task 2 Step 4 内层代码块用 4 反引号包裹避免与外层 3 反引号冲突，请实现时严格保持）。
- **Type/路径一致性**: 全部用 `项目根目录`、`项目索引.md`；跨 Task 引用一致；`outputs` 仅历史文档保留。规则唯一来源为 SKILL.md「本地存储规范」。