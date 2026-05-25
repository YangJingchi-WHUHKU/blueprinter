# BluePrinter

> 给小设计工作室的 AI 方案生成助手 —— 一句话出客户能签字的完整方案包，建筑空间和工业产品都能做。
>
> **AI 设计赛道都在比功能，我们只比一件事：把"看着像 AI"变成"看着像设计公司"。**

📌 项目原代号 **PanoSpec / 全景译**，2026-05 正式定名 **BluePrinter**。

---

## 🎯 项目一图速懂

```
[用户一句话]
   ↓
[多 Agent 协同决策：需求 / 材料 / 物理 / 风格 / 成本 / 合规]
   ↓
[Blender 程序化建模 + 自动化决策智能层（HDRI/布光/构图/LUT）]
   ↓
[Cycles 离线渲染 + Pannellum 360° 全景 + WeasyPrint PDF]
   ↓
[一份客户能签字的完整方案包]
```

**目标客户**：4-10 人小设计/装修/产品工作室
**核心场景**：家装方案、工业产品方案、小商业空间方案
**演示口号**："90 秒出一份让客户当场签字的方案"

---

## 📁 仓库结构

> 三档分类的硬规则在 [`CLAUDE.md`](CLAUDE.md)，**所有新文件落地前先看 30 秒**。

| 顶层目录 | 类别 | 内容 |
|---|---|---|
| [`research/`](research/) | **调研** | 选型对比、踩坑实测、外部资料归档（按日期命名）|
| [`tech/`](tech/) | **技术** | 架构、源代码、可跑的 PoC |
| [`docs/`](docs/) | **结果** | 对外成品：PRD、BP、提案、PDF、PPT |
| [`decisions/`](decisions/) | ADR | 关键架构/产品决策记录（不可变） |

**热门入口**：
- [`docs/PRD.md`](docs/PRD.md) / [`docs/BP.md`](docs/BP.md) —— 产品 & 商业
- [`tech/architecture.md`](tech/architecture.md) —— 技术全景图 + 12 个决策点
- [`tech/blender-poc/`](tech/blender-poc/) —— Blender 程序化建模 PoC（已实测）
- [`research/`](research/) —— 调研归档（首篇：[展示技术栈对比](research/2026-05-25-展示技术栈对比.md)）

---

## 🚀 快速上手（团队成员看这里）

### 第一次进项目，按顺序读：

1. **本 README**（5 分钟）—— 项目是什么
2. **`docs/PRD.md` § 0-2**（10 分钟）—— 我们做什么、给谁做
3. **`docs/PRD.md` § 7 竞品分析**（10 分钟）—— 为什么能赢
4. **`tech/architecture.md`**（15 分钟）—— 技术栈和决策点
5. **`tech/blender-poc/README.md`**（10 分钟）—— 跑通 Blender 测试

### 不同角色重点关注：

| 你是 | 重点看 |
|---|---|
| 产品 / 商业 | `docs/PRD.md`、`docs/BP.md` |
| AI / Agent 工程师 | `tech/architecture.md` § Agent 层 |
| 3D / Blender 工程师 | `tech/blender-poc/`、`tech/architecture.md` § 渲染层 |
| 前端 / 交互 | `tech/architecture.md` § 前端 |
| BD / 运营 | `docs/BP.md` § 商业模式、§ 获客路径 |

---

## 🛠️ 当前进度（v0.2）

- ✅ 产品定位锁定：4-10 人小工作室 SaaS
- ✅ 竞品深度核查完成（酷家乐 / Coohom / Vizcom / Depix / mnml.ai / Reviz / Fenestra 等 12 家）
- ✅ Blender 程序化建模 PoC 跑通（28 物体场景 0.1 秒建好，EEVEE 2.5s / Cycles 130s 出图）
- ✅ BP v2 + PRD v0.1 已成稿
- 🟡 12 个技术决策点待团队拍板（见 `tech/architecture.md`）
- ⬜ 多 Agent 框架选型（LangGraph vs Claude Agent SDK）
- ⬜ 资产库构建（PolyHaven + 自建中日式 30 件）
- ⬜ Hackathon Demo MVP

---

## 👥 团队协作规范

### 分支模型
- `main` —— 受保护，仅 PR 合入
- `dev` —— 集成分支，所有人推这里
- `feat/<your-name>-<topic>` —— 个人特性分支

### Commit Message
- `feat:` 新功能
- `fix:` 修 bug
- `docs:` 文档
- `chore:` 杂项
- `refactor:` 重构

例：`docs: update PRD section 7 with verified competitive analysis`

### PR 规范
- 标题用中文 OK
- 描述写清楚"改了什么/为什么/怎么测"
- @ 一个 reviewer
- 不要直接推 main

### 文档协作
- **新建文件前先看 [`CLAUDE.md`](CLAUDE.md)** —— 三档分类决策树
- Markdown 直接改、PR 合入
- Word/PPT 修改后**同时同步 markdown 源**，避免分裂
- 重大决策开 ADR（`decisions/NNNN-xxx.md`）

---

## 📞 联系

**杨镜池**（产品 + 全栈）· `2838892094yjc@gmail.com`

---

*Last updated: 2026-05-25*
