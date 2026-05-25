# Blender PoC —— 程序化建房 + 渲染管线测试

> 验证 BluePrinter 核心技术路径：用 bpy 自动建场景 + Cycles/EEVEE 渲染 + 360° 全景

---

## 已实测结论（M 系 Mac CPU，Blender 5.1.2 headless）

| 测试 | 分辨率 | Samples | 耗时 |
|---|---|---|---|
| 场景构建（28 物体）| - | - | **0.1s** |
| EEVEE 透视图 | 1024×768 | 64 | **2.5s** |
| Cycles 透视图 | 1024×768 | 128 | **130s** |
| Cycles 360° 全景 | 2048×1024 | 64 | **172s** |

**关键发现**：
1. ✅ 程序化建模快得离谱（0.1s 建 28 物体），技术路径完全可行
2. ✅ 360° equirectangular 全景渲染跑通
3. ⚠️ Mac CPU 的 Cycles **不能用于实时演示**，必须上 GPU 云或全用 EEVEE
4. ⚠️ **默认设置出图仍有 CG 味**，证明"自动化决策智能层"是命门

---

## 怎么跑

### 准备
1. 安装 Blender 5.x（[官网下载](https://www.blender.org/download/)）
2. macOS 用户：可执行文件在 `/Applications/Blender.app/Contents/MacOS/Blender`

### 跑基础版（v1）
```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python test_scene.py
```

会输出 3 张图到 `/tmp/blender_test/`：
- `01_eevee_persp.png` —— EEVEE 透视
- `02_cycles_persp.png` —— Cycles 透视
- `03_cycles_pano.png` —— Cycles 360° 全景

### 跑加强版（v2，加入决策智能层雏形）
```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python test_scene_v2.py
```

v2 加了：
- 更多家具（28 物体）
- Procedural Nishita 天空模型
- AgX 颜色管理 + Punchy LUT
- 曝光控制（-0.3 EV）
- 三点布光收紧

---

## 文件说明

| 文件 | 作用 |
|---|---|
| `test_scene.py` | 基础版：建房 + 家具 + 灯 + 三种渲染 |
| `test_scene_v2.py` | 加强版：上述 + 决策智能层雏形 |
| `samples/` | 已渲染好的 6 张样图，可直接看 |

---

## 待完成

- [ ] 加入真实 HDRI 贴图（下载 PolyHaven 室内 HDR）
- [ ] 加入摄像机角度库（10 个预制位置）
- [ ] 加入后期 LUT 库（5-10 个 .cube）
- [ ] 加入摆放扰动函数
- [ ] 测试 GPU 渲染（Metal / CUDA）真实速度
- [ ] 端到端：Pannellum 加载本仓库生成的全景图

---

## 给 3D 工程师的建议

**最先做**：

1. 把 `test_scene_v2.py` 复制改名为 `test_scene_v3.py`，开始加 HDRI（推荐 PolyHaven 的 `studio_small_03_4k.exr` 类）
2. 跑通 GPU 渲染（macOS Metal 或云端 CUDA），把 Cycles 130s 压到 10s 以内
3. 沉淀 5 个家装"出片质量"的模板场景（日式客厅 / 北欧厨房 / 工业风书房 / 极简卧室 / 美式客厅），每个跑到能直接 demo
