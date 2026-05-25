# CLAUDE.md —— BluePrinter 仓库文档分配规则

> 给团队（包括 Claude Code）的硬规则：**每一篇新文档落地前，先来这里查 30 秒，决定它放哪。**
>
> 规则越简单越能被遵守。本仓库只有三个顶层文档大类：**调研 / 技术 / 结果**。

---

## 一、三档分类（顶层）

| 顶层目录 | 中文 | 放什么 | 不该放什么 |
|---|---|---|---|
| **`research/`** | 调研 | 选型对比、方案权衡、踩坑实测、竞品分析、外部资料归档 | 已经决定的架构、最终交付物 |
| **`tech/`** | 技术 | 架构、源代码、PoC、可复现的实验脚本 | 选型过程的犹豫、未结论的对比 |
| **`docs/`** | 结果 | 给外部看的成品：PRD、BP、提案、PPT、PDF | 内部讨论、半成品、PoC 截图 |

> 三档之外仅保留两个治理目录：
> - `decisions/` —— 架构决策记录（ADR），跨档不可变文档
> - `README.md` / `CLAUDE.md` —— 仓库根入口
>
> 其它任何顶层目录（例如 `notes/`、`misc/`、`scratch/`、`tmp/`）**不允许新建**。

---

## 二、30 秒决策树

```
我要新建一份文档 / 一段代码 / 一个文件
        │
        ├─ 是给客户/老师/投资人/外部看的成品？
        │     ├─ 是 → docs/
        │     └─ 否 → 下一题
        │
        ├─ 是源代码、架构图、PoC 脚本、可跑的东西？
        │     ├─ 是 → tech/
        │     └─ 否 → 下一题
        │
        ├─ 是在比较/调研/踩坑/外部资料？
        │     ├─ 是 → research/
        │     └─ 否 → 下一题
        │
        └─ 是关键架构/产品决策的"为什么这么定"？
              └─ 是 → decisions/NNNN-标题.md（ADR 格式）
```

如果四个都不是，**就不要建这个文件**，先在 issue / PR / 群里讨论清楚再说。

---

## 三、每档的细则

### `research/` 调研

- **命名规范**：`YYYY-MM-DD-主题.md`（带日期前缀，方便按时间排序）
- **写作模板**：见 `research/README.md`，要求"给数据 + 给可复现 PoC 位置"
- **谁写谁负责**：文末标作者
- **状态标记**：在 `research/README.md` 索引表里标 `✅ 已结论` / `🟡 进行中` / `❌ 已废弃`
- **特殊情况**：调研得出的"结论"如果是架构级决策，**摘要写一份 ADR 进 `decisions/`**，原文留在 `research/`

✅ 例子：
- `research/2026-05-25-展示技术栈对比.md`（Blender / Three.js / SD 五条路线对比）
- `research/2026-06-XX-Agent框架选型.md`（LangGraph vs Claude Agent SDK）
- `research/2026-06-XX-GPU部署成本对比.md`（A10 vs 4090 vs 自建）

❌ 反例：
- `research/我的灵感.md` —— 没有数据、没有可复现，不算调研
- `research/最终架构.md` —— 已结论的东西放 `tech/` 或 `decisions/`

### `tech/` 技术

- 是仓库里**唯一可跑代码**的地方
- 子目录按"模块"划，不按"人"划
  - ✅ `tech/blender-poc/` / `tech/agent-orchestration/` / `tech/frontend/`
  - ❌ `tech/yangjingchi/` / `tech/wjb/`
- 每个子目录**必须有 README.md**：说明这是什么、怎么跑、依赖什么
- `architecture.md` 是技术全景图，**所有子模块都要在这里被引用一次**
- PoC 的渲染输出 / 大文件不要进 git（见 `.gitignore`），样本图除外

✅ 例子：
- `tech/architecture.md`
- `tech/blender-poc/test_scene.py`
- `tech/blender-poc/viewer/index.html`

❌ 反例：
- `tech/我测了一下.md` —— 测试结果属于调研，放 `research/`
- `tech/blender教程.md` —— 学习笔记不进仓库，进个人 Notion / Obsidian

### `docs/` 结果

- 这里的每一份文件**都假设有外部读者**：客户、老师、投资人、评委、合作伙伴
- 一份"结果"通常**同时有 markdown 源 + Word/PDF/PPTX 派生**
- **markdown 是 SSOT**（单一事实源）：派生格式过期了重新跑 pandoc/skill 即可
- 改了 markdown 但没同步派生文件 → PR 时必须说明（避免 docx 和 md 内容分裂）

✅ 例子：
- `docs/PRD.md` + `docs/PRD.docx`
- `docs/BP.md` + `docs/BP.pptx` + `docs/BP.docx`

❌ 反例：
- `docs/draft.md` —— 草稿不进 docs/，在 PR 里讨论或临时放本地
- `docs/会议纪要.md` —— 内部纪要不进 docs/（可以进 Notion / 群文件）

### `decisions/` ADR

- 命名：`NNNN-短标题.md`，编号永不复用、永不删除
- 模板：背景 / 决定 / 理由 / 影响 / 备选方案及未选原因
- 状态：`Proposed` → `Accepted` → `Superseded`（被新 ADR 替代）
- **决定改了 ≠ 删 ADR**，写新 ADR 并标旧的为 Superseded

✅ 例子：`decisions/0001-naming.md`（项目改名 BluePrinter）

---

## 四、典型场景对照表

| 你正在做什么 | 应该放哪 |
|---|---|
| 想比较 LangGraph 和 Claude Agent SDK | `research/2026-XX-XX-Agent框架选型.md` |
| 比较完了决定用 LangGraph | 写 ADR：`decisions/00NN-agent-framework.md` |
| 用 LangGraph 写出来的 Supervisor 代码 | `tech/agent-orchestration/` |
| LangGraph 跑通后的实测速度数据 | 回写到原 `research/` 文档"实测验证"小节 |
| 跑完后整理给客户看的"我们用了 Agent 编排"宣传段 | `docs/BP.md` 的"技术亮点"小节 |
| 临时一个 prompt 调试笔记 | **不进仓库**，本地或 Notion |
| 团队会议纪要 | **不进仓库**，群文件 / Notion |
| Hackathon 答辩的 PPT | `docs/路演PPT.pptx`（+ markdown 大纲） |
| 跑通 Blender → GLB → Three.js 的 demo 代码 | `tech/blender-poc/` |
| 上面这个 demo 的对比文档（为什么用 Three.js） | `research/2026-XX-XX-展示技术栈对比.md` |

---

## 五、Claude Code / AI 助手专用提示

如果你（Claude / Cursor / 其他 AI）被指派往本仓库新建文件：

1. **先读本文件 §一 + §二**（30 秒），定位顶层目录
2. **新建调研类**：必须命名带日期前缀 `YYYY-MM-DD-`
3. **新建技术类**：必须**同时新建/更新** 同级 `README.md`
4. **新建成品类**：必须有 markdown 源；如改了派生文件务必提示同步
5. **如果都不属于**：**不要建文件**，先在对话里和用户对齐
6. **不要新建顶层目录**（不允许 `notes/` / `tmp/` / `scratch/` 等）
7. 命名一律小写英文 + 中文标题正文；目录不用中文

违反以上任何一条，PR 会被打回。

---

## 六、未来如果要加新顶层目录

只有以下两种情况允许新增顶层目录，**必须同步修改本文件**：

1. 三档实在装不下的全新维度（例如 `assets/` 资产库、`data/` 数据集）
2. 大型独立子项目（例如 `mobile/` 移动端）

任何新增都先开 ADR：`decisions/00NN-add-folder-xxx.md`。

---

*Last updated: 2026-05-25 · 维护者：@YangJingchi · 修改本文件需要至少 1 个 reviewer*
