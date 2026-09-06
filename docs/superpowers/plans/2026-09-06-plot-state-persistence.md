# 剧情推演落盘（plot-state persistence）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增项目根文件 `剧情推演.md`，把剧情子代理的动态状态（剧情现状事实链 / 情绪心电图 / 支线与矛盾 / 后续计划）落盘持久化，防止上下文丢失，并接入文笔/复核/续写/导入全生命周期。

**Architecture:** 单一新文件 `剧情推演.md` 承载四块动态状态；剧情子代理每章定稿后增量更新（只追加事实、滚动修订计划）；文笔/复核派单按其角色读入对应切片；启动流程 A/C 路与续写 B 路均产出/读取该文件。纯文档改动（SKILL.md + 3 个子代理 rules + README + CLAUDE.md + 剧情 checklist），无代码。

**Tech Stack:** 无（纯 Markdown 提示词/文档改动）。

**Spec:** `docs/superpowers/specs/2026-09-06-plot-state-persistence-design.md`

## Global Constraints

- 所有技能内容为**中文**——提示词/清单/示例用中文撰写，与现有文件一致。
- 「数据靠文件传，不靠对话传」：`剧情推演.md` 是剧情动态状态唯一权威，子代理按路径读写，不自行推断目录；路径一律从**项目根**展开。
- 派单纪律「一次只派一件事；同一时刻只存在一个待办任务」——每章更新推演是串行的额外一单，不并行。
- `剧情推演.md` 更新纪律：已发生节点**只追加**，不改写既定事实；变动只发生在「后续计划」「情绪心电图当前态」「支线状态」；确需修订已发生节点用「修订注释：旧值→新值，理由」追加。
- 外来导入（C 路）推导 `剧情推演.md` 时标注「从原章节推导」，随草案同批确认；外来原文件只读。
- 复核六一致性与「外来导入宽松复核」规则维持不变——`剧情推演.md` 是**新增对照物**，不替换宪法/白皮书/人物档案/伏笔台账。

---

### Task 1: SKILL.md 本地存储规范加 `剧情推演.md` 与模板

**Files:**
- Modify: `SKILL.md`
  - 本地存储规范（「项目根下直接存放以下文件」清单，~第 93-99 行）
  - 项目索引状态文件清单（`SKILL.md:110`「状态文件：」行）
  - 章节版本管理旁（可选，不强制）

**Interfaces:**
- Consumes: 无（首个任务）
- Produces: `剧情推演.md` 文件名 + 四块模板（供后续任务引用）；「状态文件」清单含 `剧情推演.md`

- [ ] **Step 1: 在「项目根下直接存放以下文件」清单中加入 `剧情推演.md`**

在现有清单（`叙事宪法.md`/`世界规则白皮书.md`/`人物档案.json`/`伏笔台账.md`/`章节目录.md`）中，于 `章节目录.md` 行**之后**插入一行：

```markdown
- `剧情推演.md` ：剧情动态状态（剧情现状事实链 / 情绪心电图 / 支线与矛盾 / 后续计划）。见下「剧情推演」。
```

- [ ] **Step 2: 在该清单之后、`### 项目索引与续写回查` 之前新增「### 剧情推演」小节，含四块模板**

新增小节（含 python 式 ` ```markdown ` 代码围栏，围栏内为模板）：

````markdown
### 剧情推演

`剧情推演.md` 是剧情动态状态的唯一权威，载四块：剧情现状（事实链）、情绪心电图、支线与矛盾、后续计划（滚动）。由剧情子代理每章定稿后增量更新，队长在派文笔/复核/剧情更新时按需传入对应切片。

模板：

```markdown
# 剧情推演

## 剧情现状（事实链）
| 节点 | 章号 | 事件 | 因果（因为…所以…） |
|------|------|------|---------------------|
| 1 | 3 | 张澈发现妹妹旧发绳 | 因为废墟中发现旧发绳且未见尸骨，所以他燃起偏执的希望 |
| 2 | 5 | 与城主结盟 | 因为需要城防资金，所以接受城主条件 |

## 情绪心电图
| 人物 | 处境 | 情绪走线 | 变化触发点 |
|------|------|----------|------------|
| 张澈 | 被通缉 | 绝望→偏执希望 | 3章末发现遗物 |

## 支线与矛盾
- 支线：城主背后的走私网（伏笔 F-007）
- 主线矛盾：复仇 vs 生存

## 后续计划（滚动）
- [ ] 回收 F-003 伏笔（6章）
- [ ] 触发转折：妹妹被目击在城北
```

更新纪律（铁律）：已发生节点**只追加**，不改写既定事实；变动只发生在「后续计划」「情绪心电图当前态」「支线状态」；确需修订已发生节点 → 用「修订注释：旧值→新值，理由」追加，不静默改写。
````

- [ ] **Step 3: 更新 `项目索引.md` 的「状态文件」清单**

将 `SKILL.md:110` 行：

```markdown
- 状态文件：叙事宪法.md / 世界规则白皮书.md / 人物档案.json / 伏笔台账.md / 章节目录.md / 第N章-vX.md
```

改为：

```markdown
- 状态文件：叙事宪法.md / 世界规则白皮书.md / 人物档案.json / 伏笔台账.md / 章节目录.md / 剧情推演.md / 第N章-vX.md
```

- [ ] **Step 4: 验证**

```bash
grep -c "剧情推演" SKILL.md
```
预期 ≥ 4（清单插入 ×1 + 模板小节标题与正文 ×2~3 + 状态文件清单 ×1）。

```bash
# 验证围栏配平：``` 出现偶数次（模板内 2 个围栏 + 其它正文围栏）
grep -c '^```' SKILL.md | grep -E '[02468]$' || echo "UNBALANCED"
python - <<'EOF'
import re
t = open('SKILL.md', encoding='utf-8').read()
n = len(re.findall(r'^```', t, re.M))
print(f"code fences: {n}, balanced: {n % 2 == 0}")
EOF
```

- [ ] **Step 5: Commit**

```bash
git add SKILL.md
git commit -m "docs(skill): add 剧情推演.md to local storage spec with template"
```

---

### Task 2: SKILL.md 工作流「每章定稿后派剧情更新」+ 启动流程 A/C 路产出 + B 路读取

**Files:**
- Modify: `SKILL.md`
  - 工作流（逐章循环）小节（`SKILL.md:65-68`）
  - 启动流程第一步（`SKILL.md:151`）
  - 启动流程 B 路（`SKILL.md:146`）
  - 导入外来项目流程第 2/3/5 步（`SKILL.md:159-166`）
  - 派单协议「一次只派一件事」约束（`SKILL.md:36`，补充串行允许）

**Interfaces:**
- Consumes: Task 1 的 `剧情推演.md` 文件名与模板
- Produces: 每章定稿后剧情更新派单；A/C 路产出、B 路读取 `剧情推演.md` 的流程落位

- [ ] **Step 1: 工作流「逐章循环」加入每章更新推演**

将 `SKILL.md:67` 行：

```markdown
- 逐章创作：你派「文笔」子代理写第N章 → 存档 → 派「复核」子代理把关 → 通过则进入下一章，红灯则带复核意见重新派「文笔」重写。
```

改为：

```markdown
- 逐章创作：你派「文笔」子代理写第N章 → 存档 → 派「复核」子代理把关 → 通过后**派「剧情」子代理增量更新 `剧情推演.md`**（读最新章 + 现有推演 + 台账 → 追加事实行 / 更新当前态 / 修订后续计划；串行，不并行）→ 进入下一章，红灯则带复核意见重新派「文笔」重写。
```

- [ ] **Step 2: 启动流程第一步加 `剧情推演.md` 产出**

将 `SKILL.md:151` 行：

```markdown
第一步：派「世界」和「剧情」子代理开联席会，产出 `叙事宪法` 草案和 `世界规则白皮书` 大纲；草案通过前禁止写正文。
```

改为（剧情一并产出 `剧情推演.md` 初版，与草案同批确认）：

```markdown
第一步：派「世界」和「剧情」子代理开联席会，产出 `叙事宪法` 草案和 `世界规则白皮书` 大纲；「剧情」另产出 `剧情推演.md` 初版（主线首段节点 + 初始情绪心电图 + 初始矛盾/支线），与草案同批确认；草案通过前禁止写正文。
```

- [ ] **Step 3: 启动流程 B 路加 `剧情推演.md` 读取**

将 `SKILL.md:146` 行中「读 `章节目录.md` 定位最高版本章节 → 续写」改为：

```markdown
…→ 读 `章节目录.md` 定位最高版本章节，读 `剧情推演.md` 作为剧情状态入口 → 续写。
```

- [ ] **Step 4: 导入外来项目流程第 2 步加 `剧情推演.md` 推导**

将 `SKILL.md:162` 行（剧情子代理产出行）：

```markdown
   - 剧情 → `叙事宪法.md` + `伏笔台账.md` + `章节目录.md`（含每章最新版本 + 一句话梗概）
```

改为：

```markdown
   - 剧情 → `叙事宪法.md` + `伏笔台账.md` + `章节目录.md`（含每章最新版本 + 一句话梗概）+ `剧情推演.md`（含剧情现状事实链 + 情绪心电图 + 支线与矛盾 + 后续计划，标注「从原章节推导」）
```

- [ ] **Step 5: 导入外来项目流程第 3/5 步补同步确认与续写**

第 3 步（`SKILL.md:164`）文案加「（含 `剧情推演.md` 草案）」；第 5 步（`SKILL.md:166`）续写句加「读 `剧情推演.md` 作为剧情状态入口」：

```markdown
3. **用户确认草案**：向用户展示各草案要点（含 `剧情推演.md` 草案）→ 用户确认 / 修正 → 定稿。草案被推翻则重新派对应子代理修订，不硬压。
...
5. **续写**：从最后一章的最高顺序，按 A 的逐章流程继续（读 `剧情推演.md` 作为剧情状态入口；派文笔写下一章 → 复核 → 剧情更新推演 → 下一章）。
```

- [ ] **Step 6: 派单协议「一次只派一件事」补串行说明**

将 `SKILL.md:36` 行：

```markdown
- 一次只派一件事；同一时刻只存在一个待办任务；
```

改为：

```markdown
- 一次只派一件事；同一时刻只存在一个待办任务；「剧情更新推演」与「写章/复核」串行执行，不并行；
```

- [ ] **Step 7: 验证**

```bash
grep -n "剧情推演" SKILL.md
```
预期覆盖：存储规范小节、工作流逐章、启动 A/B/C 路、导入流程第 2/3/5 步、派单协议约束。

```bash
# 围栏配平
python - <<'EOF'
import re
t = open('SKILL.md', encoding='utf-8').read()
n = len(re.findall(r'^```', t, re.M))
print(f"code fences: {n}, balanced: {n % 2 == 0}")
EOF
```

- [ ] **Step 8: Commit**

```bash
git add SKILL.md
git commit -m "docs(skill): wire 剧情推演.md into per-chapter loop, startup A/C, resume B, import flow"
```

---

### Task 3: 剧情子代理 rules + checklist 落 `剧情推演.md` 产出/更新纪律

**Files:**
- Modify: `references/agents/剧情/rules.md`
- Modify: `references/agents/剧情/checklist.md`

**Interfaces:**
- Consumes: Task 1 模板（四块 + 更新纪律）；Task 2 的每章更新派单流程
- Produces: 剧情子代理对 `剧情推演.md` 的产出/读入/更新纪律描述（供复核/文笔读入一致性）

- [ ] **Step 1: 改写 `剧情/rules.md`（产出 + 读入 + 更新纪律）**

将 `剧情/rules.md:3` 全文改为（在原文基础上加粗标注新增；实际替换为完整新文）：

```markdown
【剧情子代理】主线与因果的总策划。产出：主线节点、支线触发、伏笔台账、转折点设计、`剧情推演.md`（剧情动态状态，四块：剧情现状事实链 / 情绪心电图 / 支线与矛盾 / 后续计划）。用「节点法」规划大纲，只定关键情节点 + 情绪心电图，不限制具体描写。转折点要写到细节节点：什么小事触发、牵涉谁、引向什么后果。逻辑铁律（最重要）：一切情节都要有推动因素，不能拍脑袋硬写，要有「水到渠成」感——哪怕换成「我」处在那个位置也会这么做；所以每个节点都要写清「因为…所以…」的因果链。伏笔与矛盾：主动埋伏笔记入台账，并主动设计矛盾点——小说在矛盾冲突中发展，每个节点都要有冲突推动。规划新节点前先检索台账，强制「有因必有果」；本章回收旧伏笔时标注「回收第X章伏笔」。
**更新纪律（铁律）**：`剧情推演.md` 已发生节点**只追加**，不改写既定事实；变动只发生在「后续计划」「情绪心电图当前态」「支线状态」；确需修订已发生节点 → 用「修订注释：旧值→新值，理由」追加，不静默改写。每章定稿后的增量更新：读最新章 + 现有推演 + 台账 → 追加事实行 / 更新当前态 / 修订后续计划。
读：宪法、已有台账、已写章节、现有 `剧情推演.md`。
```

- [ ] **Step 2: 扩展 `剧情/checklist.md`（加 2 条更新纪律检查）**

在现有 5 行之后追加：

```markdown
- [ ] 本次更新只追加事实行 / 刷新「后续计划 / 情绪心电图当前态 / 支线状态」，没有改写既定事实？
- [ ] 确需修订旧节点时用了「修订注释：旧值→新值，理由」而不是静默覆盖？
```

- [ ] **Step 3: 验证**

```bash
grep -c "剧情推演" references/agents/剧情/rules.md   # 预期 ≥ 3
grep -c "修订注释" references/agents/剧情/rules.md  # 预期 ≥ 1
grep -c "只追加" references/agents/剧情/rules.md   # 预期 ≥ 1
```

- [ ] **Step 4: Commit**

```bash
git add references/agents/剧情/rules.md references/agents/剧情/checklist.md
git commit -m "docs(agents/剧情): add 剧情推演.md output & append-only update discipline"
```

---

### Task 4: 复核/文笔 rules 加 `剧情推演.md` 读入

**Files:**
- Modify: `references/agents/复核/rules.md`
- Modify: `references/agents/文笔/rules.md`

**Interfaces:**
- Consumes: Task 1 模板；Task 3 的 `剧情推演.md` 四块定义
- Produces: 复核/文笔派单时传入 `剧情推演.md` 对应切片的依据

- [ ] **Step 1: 复核 rules 读入 + 判决对照加 `剧情推演.md`**

将 `复核/rules.md:3` 中两处：
- 「读：最新版正文、宪法、白皮书、台账、人物卡。」→「读：最新版正文、宪法、白皮书、台账、人物卡、`剧情推演.md`（剧情现状事实链）。」
- 🔴红灯列举内「逻辑断链」之后补「/剧情断裂」：`…逻辑断链/剧情断裂/伏笔未回收）`，并在句末对照清单加「判『逻辑断链/剧情断裂』时对照 `剧情推演.md` 剧情现状事实链 + 伏笔台账」。

即改为：

```markdown
【复核子代理】只挑错、不改写。把正文逐条对照所有设定（宪法、白皮书、人物档案、伏笔台账、战力差值、`剧情推演.md` 剧情现状事实链），找出不合要求处，用三色灯判决：🔴红灯＝致命（人设崩塌/人物标签化/行为不合情理/战力冲突/地理错误/逻辑断链/剧情断裂/伏笔未回收）→ 驳回让文笔重写，并写清「哪里不合、为什么、怎么改」；🟡黄灯＝警告（文笔略水/节奏拖沓）→ 给修改建议，改后过审；🟢绿灯＝通过。还要专门验：剧情是否「水到渠成」、有没有「拍脑袋」的硬转折。判「逻辑断链/剧情断裂」时对照 `剧情推演.md` 剧情现状事实链 + 伏笔台账。额外输出【节奏建议】和【章末钩子备选】（3 个不同方向，供队长选）。读：最新版正文、宪法、白皮书、台账、人物卡、`剧情推演.md`。产出：复核报告。字数检查：运行 scripts/count_cjk.py 核对正文中文字符数，脱离 2000–4000 字区间按偏离程度判 🟡 或 🔴。
```

- [ ] **Step 2: 文笔 rules 读入加 `剧情推演.md` 切片**

将 `文笔/rules.md:3` 中「读：宪法、世界白皮书（本章局部）、人物档案（本章出场角色）、伏笔台账（待回收）、章节目录（定位最新版）。」改为：

```markdown
读：宪法、世界白皮书（本章局部）、人物档案（本章出场角色）、伏笔台账（待回收）、章节目录（定位最新版）、`剧情推演.md`（剧情现状末行 + 情绪心电图 + 与本章相关的后续计划）。
```

- [ ] **Step 3: 验证**

```bash
grep -c "剧情推演" references/agents/复核/rules.md   # 预期 ≥ 2
grep -c "剧情推演" references/agents/文笔/rules.md   # 预期 ≥ 1
```

- [ ] **Step 4: Commit**

```bash
git add references/agents/复核/rules.md references/agents/文笔/rules.md
git commit -m "docs(agents): 复核/文笔 read 剧情推演.md (fact-chain check / emotion pacing)"
```

---

### Task 5: README.md + CLAUDE.md 文档同步

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: Task 1-4 引入的 `剧情推演.md` 语义
- Produces: 用户文档与架构文档含该文件

- [ ] **Step 1: README.md 文件清单加 `剧情推演.md`**

将 `README.md:51` 行（`章节目录.md` 行）之后插入：

```markdown
├─ 剧情推演.md          剧情动态状态：剧情现状事实链/情绪心电图/支线与矛盾/后续计划
```

- [ ] **Step 2: CLAUDE.md 架构描述加该文件职责**

在 `CLAUDE.md`「Project output」bullet（`CLAUDE.md:27`）末尾追加：

```markdown
`剧情推演.md`（剧情动态状态：剧情现状事实链/情绪心电图/支线与矛盾/后续计划，剧情子代理每章定稿后增量更新，只追加不改写既定事实）也归一于项目根。
```

- [ ] **Step 3: 验证**

```bash
grep -c "剧情推演" README.md   # 预期 ≥ 1
grep -c "剧情推演" CLAUDE.md   # 预期 ≥ 1
```

- [ ] **Step 4: Commit**

```bash
git add README.md CLAUDE.md
git commit -m "docs: document 剧情推演.md in README and CLAUDE.md"
```

---

### Task 6: 全量验证（终检）

**Files:**
- 只读检查，不改文件

**Interfaces:**
- Consumes: Task 1-5 全部改动

- [ ] **Step 1: 全量 grep `剧情推演` 落位清单**

```bash
grep -rn "剧情推演" --include="*.md" . | grep -v docs/superpowers
```
预期覆盖（非 docs 目录）：
- `SKILL.md` ≥ 6 处：存储规范清单、模板小节、状态文件清单、工作流逐章、启动 B 路、导入流程第 2 步（A/C 路、派单协议）
- `references/agents/剧情/rules.md` + `checklist.md`
- `references/agents/复核/rules.md`、`references/agents/文笔/rules.md`
- `README.md`、`CLAUDE.md`

- [ ] **Step 2: 围栏配平（全部 md）**

```bash
python - <<'EOF'
import re, pathlib
for p in sorted(pathlib.Path('.').rglob('*.md')):
    t = p.read_text(encoding='utf-8')
    n = len(re.findall(r'^```', t, re.M))
    print(f"{p}: fences={n} balanced={n % 2 == 0}")
EOF
```

- [ ] **Step 3: 导入/续写流程一致性 grep**

```bash
# 导入流程应含 "剧情推演" 且带 "从原章节推导"
grep -n "从原章节推导" SKILL.md
# 续写 B 路含 "剧情推演"
grep -n "剧情推演" SKILL.md | grep -i "续写\|B 路\|入口"
```

- [ ] **Step 4: 运行既有测试套件（应保持全绿）**

```bash
python -m pytest tests/ -q
```
预期：104 passed（无回归——本特性只改文档，不改代码/测试）。

- [ ] **Step 5: `git status` 干净、无未提交**

```bash
git status --porcelain
```
预期：空输出。

---

## Self-Review

**1. Spec coverage:**
- Spec「文件模板（四块）」→ Task 1 Step 2 ✓
- Spec「增量更新纪律（铁律级）」→ Task 1 Step 2（更新纪律）+ Task 3 Step 1/2 ✓
- Spec「生命周期-新开 A 路」→ Task 2 Step 2 ✓
- Spec「生命周期-每章定稿后」→ Task 2 Step 1 + 5 ✓
- Spec「生命周期-导入 C 路」→ Task 2 Step 4/5 ✓
- Spec「生命周期-续写 B 路」→ Task 2 Step 3 ✓
- Spec「生命周期-全局刷新 3–5 章」→ SKILL.md 现有「全局刷新」句已含「复盘校准后续大纲」，`剧情推演.md` 即该大纲落盘载体，无需额外改动（已在 Global Constraints 说明）
- Spec「文笔/复核读入」→ Task 4 ✓
- Spec「涉及修改文件」表 → Task 1/2/3/4/5 ✓
- **缺口检查**：复习「全局刷新」—spec 说「现有复盘校准流程新增「读推演 → 校准后续计划」一步」。SKILL.md:68 全局刷新句当前是「复盘校准后续大纲」。改其为「读 `剧情推演.md` → 复盘校准后续计划」更贴合 spec。**需并入 Task 2**。

**2. Placeholder scan:** 无 TBD/TODO；每步给到具体文案与替换目标。✓

**3. Type consistency:** `剧情推演.md` 文件名、四块块名（剧情现状/情绪心电图/支线与矛盾/后续计划）、「只追加」「修订注释」术语全程一致。✓

**待补（Task 2 Step 8 之前）：**
在 Task 2 Step 1 之后插入一步（全局刷新句同步），并将 Task 2 步骤顺延：

```markdown
- [ ] **Step 1b: 全局刷新句同步**

将 `SKILL.md:68` 行：

```markdown
- 全局刷新：每完成 3–5 章，你召集「世界+剧情+人物」三个子代理复盘校准后续大纲。
```

改为：

```markdown
- 全局刷新：每完成 3–5 章，你召集「世界+剧情+人物」三个子代理，读 `剧情推演.md` 复盘校准后续计划。
```
```