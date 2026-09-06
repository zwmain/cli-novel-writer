# cli-novel-writer 续写 / 外来小说导入 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 skill 支持对外来小说（只有原始章节、无结构化文件）的导入与续写，并把启动流程改为三路分流（新开 / 继续 skill 项目 / 导入外来项目）。

**Architecture:** 纯 Markdown/文本层改动（skill 规则），无 Python 逻辑。核心是重写 SKILL.md 启动流程为三路分流，新增「导入外来项目」流程（C 路）：派 剧情/世界/人物 子代理读外来原章节 → 生成标注「从原章节推导」的结构文件草案 → 用户确认 → 建 `项目索引.md`（含来源标记 + 章节映射表）→ 按逐章流程续写。复核 rules 补「外来导入宽松复核」规则。外来原章节只读、不复制。

**Tech Stack:** 无（纯 Markdown skill 规则文本；模型执行）。

**Spec:** `docs/superpowers/specs/2026-09-06-import-continuation-design.md`（本计划实现此 spec，executor 需同时读 spec 与计划）

## Global Constraints

- **外来原章节只读**：不复制、不改写、不入版本管理；结构化文件是叠加生成，不替换原章节（Spec §1 决策1, §3）。
- **需用户确认草案**：子代理生成的 宪法/世界/人物/伏笔/章节目录 草案必须先向用户展示要点、确认/修正、定稿，才能续写（Spec 决策2, §3）。
- **第零步分流三路**：新开(A) / 继续 skill 项目(B) / 导入外来项目(C)，并入同一个启动流程分流；判定只看项目目录下是否已有 skill 结构化文件（Spec 决策3, §1）。
- **推导标记 + 宽松复核**：导入结构文件标注「从原章节推导」；复核对导入设定宽松、对续写新增严格（Spec 决策4, §4）。
- **内容中文**：所有 skill 提示词/检查表/示例用中文，与现有文件一致（CLAUDE.md Key conventions）。
- **不新增脚本**：导入流程全部由队长文本执行 + 子代理；不改 `scripts/count_cjk.py` 及测试（Spec §6）。
- **顺序不确定即停**：外来章节无法确定顺序时停住问用户，不硬猜（Spec §3, §6）。

---

### Task 1: 重写 SKILL.md 启动流程为三路分流

**Files:**
- Modify: `SKILL.md:138-146`（「## 启动流程（每次开新项目必须遵守）」整节）

**Interfaces:**
- Consumes: Spec §1（第零步三路分流判定）、Spec §2（继续 skill 项目回查，沿用现状）、Spec §3（导入外来项目流程）。
- Produces: SKILL.md「启动流程」一节改为三路分流；新增导入流程 C 路文本。后续 Task 2（本地存储规范补来源标记）与 Task 3（复核 rules）引用这里的分流与导入规则。

- [ ] **Step 1: 修改启动流程节标题与开篇**

将 `SKILL.md:138` 的：

```markdown
## 启动流程（每次开新项目必须遵守）
```

改为：

```markdown
## 启动流程（每次启动必须遵守：三路分流）
```

- [ ] **Step 2: 修改开篇句为三路分流判定**

将 `SKILL.md:140` 的：

```markdown
用户给题材/梗概或说「开始」后，按以下步骤走，每步完成后先向用户汇报、等确认再继续：
```

改为：

```markdown
用户给题材/梗概、或说「开始 / 续写 / 继续」后，按以下第零步分流判定，每步完成后先向用户汇报、等确认再继续：
```

- [ ] **Step 3: 第零步改为三路分流**

将 `SKILL.md:142` 的：

```markdown
第零步：解析项目根目录（规则见「本地存储规范」；用户指定或默认）→ 创建该目录 → 若该路径下已有 `项目索引.md` 则读回作为「继续该项目」；否则新建 `项目索引.md` 并写入项目名、创建日期（`YYYY-MM-DD`）、`项目根目录`（绝对路径）。此后所有派单的「数据来源 / 产出写回」路径都从项目根展开。
```

改为：

```markdown
第零步：三路分流判定（判定只看项目目录下是否已有 skill 结构化文件）：
- **A 新开项目**：用户给题材/梗概、未提已有小说 → 解析项目根目录（规则见「本地存储规范」；用户指定或默认）→ 创建该目录 → 新建 `项目索引.md` 并写入项目名、创建日期（`YYYY-MM-DD`）、`项目根目录`（绝对路径）→ 进入下面第一步三步走。
- **B 继续 skill 项目**：用户说「续写 / 继续」，或给的项目目录下**已有 `项目索引.md`** → 按「项目索引与续写回查」规则回查定位项目根 → 若该索引标记为「外来导入」则按「复核：外来导入宽松规则」复核 → 读 `章节目录.md` 定位最高版本章节 → 续写。
- **C 导入外来项目**：用户给的目录下**只有原始章节 / 正文、无结构化文件**（无 `项目索引.md` 等）→ 按「导入外来项目流程」执行（见下）。

此后所有派单的「数据来源 / 产出写回」路径都从项目根展开。
```

- [ ] **Step 4: 在启动流程节末尾追加「导入外来项目流程」**

在 `SKILL.md` 启动流程节末尾（第零步三步走之后、`## 输出纪律` 之前）追加：

```markdown
### 导入外来项目流程（第零步 C 路）

用户给的是只有原始章节、无结构化文件的外来小说时，走此流程，每步先向用户汇报、等确认再继续：

1. **定位来源 + 确认章节顺序**：读取外来目录 / 文件列表，按文件名序号排序确认章节顺序；若无法确定顺序（无序号 / 混杂）→ 停住问用户。
2. **派子代理读全章、出草案**：派「世界」「剧情」「人物」三个子代理读完外来全部章节，各自产出对应草案，全部标注「从原章节推导」：
   - 世界 → `世界规则白皮书.md`（含战力天花板与差值）
   - 剧情 → `叙事宪法.md` + `伏笔台账.md` + `章节目录.md`（含原文件名 ↔ 章节顺序映射）
   - 人物 → `人物档案.json`（按既有 Schema）
3. **用户确认草案**：向用户展示各草案要点 → 用户确认 / 修正 → 定稿。草案被推翻则重新派对应子代理修订，不硬压。
4. **建 `项目索引.md`**：记录项目名、创建日期、绝对根路径、**来源标记「外来导入」**、以及**章节映射表**（原文件名 ↔ 章节号 ↔ 状态）。
5. **续写**：从最后一章的最高顺序，按 A 的逐章流程继续（派文笔写下一章 → 复核 → 下一章）。

外来原文件**只读**：不复制、不改写、不入版本管理。续写产出的新章节写入项目根下 `第N章-vX.md`。
```

- [ ] **Step 5: 校验**

运行：
```bash
grep -c "三路分流" SKILL.md
grep -c "导入外来项目流程" SKILL.md
```
Expected: 两者各至少 1；确认「三路分流」「A 新开项目」「B 继续 skill 项目」「C 导入外来项目」文本均已落位。

- [ ] **Step 6: Commit**

```bash
git add SKILL.md
git commit -m "docs: rewrite startup as 3-way branch; add foreign-novel import flow"
```

---

### Task 2: SKILL.md「项目索引与续写回查」补来源标记与映射

**Files:**
- Modify: `SKILL.md:101-114`（「### 项目索引与续写回查」小节）

**Interfaces:**
- Consumes: Spec §2（回查规则沿用）、Spec §3 步骤4（来源标记 + 章节映射表）、Task 1 的分流与导入流程（B/C 路引用「外来导入」标记）。
- Produces: `项目索引.md` 的字段定义（来源标记 + 章节映射表），供 Task 1 的 B/C 路、Task 3 复核 rules 引用「外来导入」。

- [ ] **Step 1: 修改项目索引字段说明**

将 `SKILL.md:110` 的：

```markdown
- 状态文件：叙事宪法.md / 世界规则白皮书.md / 人物档案.json / 伏笔台账.md / 章节目录.md / 第N章-vX.md
```

改为：

```markdown
- 状态文件：叙事宪法.md / 世界规则白皮书.md / 人物档案.json / 伏笔台账.md / 章节目录.md / 第N章-vX.md
- 来源标记：原生（skill 内新开）或 外来导入（从其他来源小说导入）
```

- [ ] **Step 2: 在回查规则后追加来源标记与映射说明**

在 `SKILL.md:114`（回查规则 ③）之后追加：

```markdown
- 外来导入标记：若 `项目索引.md` 标记为「外来导入」，则该项目按「复核：外来导入宽松规则」复核（对导入设定宽松、对续写新增严格）；`章节目录.md` 含原文件名 ↔ 章节号 ↔ 状态的映射表。
```

- [ ] **Step 3: 校验**

运行：
```bash
grep -c "外来导入" SKILL.md
```
Expected: ≥ 3（Task 1 已加 2 处，本 Task 再加 2 处）。确认「来源标记」「外来导入宽松规则」已落位。

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "docs: add source-marker and chapter-mapping to project index"
```

---

### Task 3: references/agents/复核/rules.md 补「外来导入宽松复核」

**Files:**
- Modify: `references/agents/复核/rules.md:1-3`（在既有规则末尾追加）

**Interfaces:**
- Consumes: Spec §4（宽松复核规则）、Task 1 的 B 路与导入流程（引用「复核：外来导入宽松规则」）。
- Produces: `references/agents/复核/rules.md` 新增「外来导入宽松复核」段落，Task 1 已引用的「复核：外来导入宽松规则」指向这里。

- [ ] **Step 1: 在复核 rules 末尾追加导入宽松规则**

将 `references/agents/复核/rules.md` 末尾追加：

```markdown

【外来导入宽松复核】复核外来导入项目（`项目索引.md` 标记「外来导入」）时：
- 对「从原章节推导」的设定/人物/伏笔（宪法、白皮书、人物档案、伏笔台账）**宽松**：不强求与 skill 原生项目一致，不因导入期推导偏差误判。
- 对续写**新增**内容**严格**一致：新章节必须与已定稿的导入设定一致，六一致性照常适用。
```

- [ ] **Step 2: 校验**

运行：
```bash
grep -c "外来导入宽松复核" references/agents/复核/rules.md
```
Expected: 1。确认规则已落位、与 Task 1 引用名一致（「复核：外来导入宽松规则」/「外来导入宽松复核」）。

- [ ] **Step 3: Commit**

```bash
git add references/agents/复核/rules.md
git commit -m "docs: add lenient-review rule for imported foreign novels"
```

---

### Task 4: README.md 补外来导入说明

**Files:**
- Modify: `README.md:48-62`（「## 它会读写文件」一节）

**Interfaces:**
- Consumes: Spec §5.4、Task 1（三路分流）、Task 2（来源标记 + 映射）。
- Produces: README「它会读写文件」反映外来导入模型（原章节只读、叠加结构文件、来源标记与章节映射）。

- [ ] **Step 1: 更新项目结构树，补外来导入说明**

将 `README.md:51` 的：

```markdown
├─ 项目索引.md          项目名/创建日期/项目根（绝对路径），供续写回查
```

改为：

```markdown
├─ 项目索引.md          项目名/创建日期/项目根（绝对路径）+ 来源标记（原生/外来导入）+ 章节映射，供续写回查
```

- [ ] **Step 2: 在「它会读写文件」节末尾追加外来导入段**

在 `README.md:62` 之后追加：

```markdown
### 外来小说导入

如果给的是一个只有原始章节、无 skill 结构化文件的外来小说项目：队长读全部原始章节 → 派 世界/剧情/人物 子代理生成 叙事宪法/世界规则白皮书/人物档案.json/章节目录.md 草案（标注「从原章节推导」）→ 展示要点给你确认/修正 → 定稿 → 建 `项目索引.md`（含来源标记「外来导入」+ 章节映射表）→ 从最后一章续写。原始章节**只读**、不复制不改写；续写的新章节写入项目根 `第N章-vX.md`。
```

- [ ] **Step 3: 校验**

运行：
```bash
grep -c "外来导入" README.md
```
Expected: ≥ 1。

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: document foreign-novel import in README"
```

---

### Task 5: CLAUDE.md 补三路分流与外来导入

**Files:**
- Modify: `CLAUDE.md:27`（「Project output」一段）

**Interfaces:**
- Consumes: Spec §5.5、Task 1（三路分流）、Task 2（来源标记 + 映射）。
- Produces: CLAUDE.md「Project output」补三路分流与外来导入路径，供后续维护者理解架构。

- [ ] **Step 1: 更新 Project output 段**

将 `CLAUDE.md:27` 的：

```markdown
- **Project output**: when a novel is started, the队长 resolves the 项目根 directory (user-specified — absolute/relative cwd/`~` — or default `cwd/日期-项目名/`), writes `项目索引.md` (project name, created date, **absolute** root path) for resume-lookup, and creates 叙事宪法/世界规则白皮书/人物档案.json/伏笔台账/章节目录/章节正文 (`第N章-vX.md`, versioned — never overwrite, only add higher X). Path resolution rules live only in SKILL.md's 本地存储规范.
```

改为：

```markdown
- **Project output**: when a novel is started, the队长 resolves the 项目根 directory (user-specified — absolute/relative cwd/`~` — or default `cwd/日期-项目名/`), writes `项目索引.md` (project name, created date, **absolute** root path, source-marker 原生/外来导入, chapter-mapping) for resume-lookup, and creates 叙事宪法/世界规则白皮书/人物档案.json/伏笔台账/章节目录/章节正文 (`第N章-vX.md`, versioned — never overwrite, only add higher X). Path resolution rules live only in SKILL.md's 本地存储规范. The startup flow branches three ways in SKILL.md: (A) 新开 project from 题材/梗概; (B) continue a skill project via `项目索引.md` resume; (C) import a foreign novel (raw chapters only) by reading chapters → generating draft 叙事宪法/世界规则/人物档案/章节目录 (marked 从原章节推导) → user confirmation → build `项目索引.md` (source-marker 外来导入 + chapter map) → continue. Foreign raw chapters stay read-only.
```

- [ ] **Step 2: 校验**

运行：
```bash
grep -c "外来导入" CLAUDE.md
```
Expected: ≥ 1。

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: document 3-way startup and foreign-novel import in CLAUDE.md"
```

---

### Task 6: 终验（对照 spec 全量校验）

**Files:**
- 只读校验，不改文件。

**Interfaces:**
- Consumes: Spec 全部 §；Task 1-5 的全部改动。

- [ ] **Step 1: 校验三路分流覆盖**

运行：
```bash
grep -n "三路分流\|A 新开项目\|B 继续 skill 项目\|C 导入外来项目" SKILL.md
```
Expected: 4 处全部匹配。

- [ ] **Step 2: 校验外来导入关键词一致性**

运行：
```bash
grep -c "外来导入" SKILL.md README.md CLAUDE.md references/agents/复核/rules.md
```
Expected: 每个文件计数均 ≥ 1。

- [ ] **Step 3: 运行已有测试集确保无回归**

运行：
```bash
python -m pytest tests/ -q
```
Expected: 72 passed。

- [ ] **Step 4: 校验无未闭合 Markdown 代码块**

运行：
```bash
python -c '
for f in ["SKILL.md", "README.md", "CLAUDE.md", "references/agents/复核/rules.md"]:
    cnt = open(f, encoding="utf-8").read().count("```")
    assert cnt % 2 == 0, f"{f} fence unclosed: {cnt}"
print("all fences balanced")
'
```
Expected: `all fences balanced`。
