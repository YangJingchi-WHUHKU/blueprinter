# tech/research —— 技术调研归档

> 团队成员做的技术选型调研、对比实测、踩坑记录都放这里。
> 每篇一个 markdown，命名格式：`YYYY-MM-DD-主题.md`

---

## 已归档调研

| 日期 | 主题 | 作者 | 状态 |
|---|---|---|---|
| 2026-05-25 | [展示技术栈对比](2026-05-25-展示技术栈对比.md) —— Blender vs Three.js vs SD vs Freestyle，5 条路线实测 | @YangJingchi | ✅ 已结论 |

---

## 待做调研（认领）

- [ ] **Agent 编排框架选型**：LangGraph vs Claude Agent SDK vs 自写状态机（AI 工程师）
- [ ] **GPU 部署方案**：阿里云 A10 vs AutoDL 4090 vs 自购，成本/速度/稳定性对比（3D 工程师 + 产品）
- [ ] **资产库**：PolyHaven / BlenderKit / Sketchfab，中式 + 工业资产稀缺度评估（3D 工程师）
- [ ] **法规 RAG**：ChromaDB 实测，5–10 条核心规则的硬编码 vs 检索 trade-off（AI 工程师）
- [ ] **前端实时通信**：WebSocket vs SSE，Agent 对话流的最佳协议（前端）

---

## 怎么写调研文档

最简模板：

```markdown
# {主题}
> 作者 / 日期 / 背景一句话

## 1. 问题陈述
## 2. 候选方案
## 3. 实测对比 (表格)
## 4. 推荐 + 理由
## 5. 配套 PoC 代码位置
```

不要只给结论——**给数据 + 给可复现 PoC**。被其他人质疑时，你要能让他在自己电脑上跑一遍。
