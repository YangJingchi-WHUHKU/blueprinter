"""
PanoSpec Blender 程序化建房测试
模拟 AI 输出 spec 后自动生成场景的核心环节
"""
import bpy
import math
import time
import os
import sys

OUTPUT_DIR = "/tmp/blender_test"


def clean_scene():
    """清空当前场景"""
    bpy.ops.wm.read_factory_settings(use_empty=True)


def add_pbr_material(name, color, roughness=0.5, metallic=0.0):
    """创建一个 PBR 材质"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, location, scale, material=None):
    """加一个长方体（墙/家具的基础）"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    if material:
        obj.data.materials.append(material)
    return obj


def build_room():
    """建一个 4x5x2.8 的房间，带地板天花板和 4 面墙"""
    wall_mat = add_pbr_material("wall_paint", (0.95, 0.92, 0.88), roughness=0.85)
    floor_mat = add_pbr_material("wood_floor", (0.55, 0.4, 0.25), roughness=0.4)
    ceil_mat = add_pbr_material("ceiling", (0.98, 0.98, 0.98), roughness=0.9)

    # 地板 4x5
    add_box("floor", (0, 0, 0), (4, 5, 0.05), floor_mat)
    # 天花板
    add_box("ceiling", (0, 0, 2.8), (4, 5, 0.05), ceil_mat)
    # 4 面墙（厚 0.1m，高 2.8m）
    add_box("wall_n", (0, 2.5, 1.4), (4, 0.1, 2.8), wall_mat)
    add_box("wall_s", (0, -2.5, 1.4), (4, 0.1, 2.8), wall_mat)
    add_box("wall_e", (2.0, 0, 1.4), (0.1, 5, 2.8), wall_mat)
    add_box("wall_w", (-2.0, 0, 1.4), (0.1, 5, 2.8), wall_mat)


def add_furniture():
    """放几件简单家具：沙发(灰)/茶几(深棕)/电视柜(白)"""
    sofa_mat = add_pbr_material("sofa_fabric", (0.35, 0.35, 0.4), roughness=0.8)
    table_mat = add_pbr_material("walnut", (0.25, 0.15, 0.08), roughness=0.3)
    cabinet_mat = add_pbr_material("white_lacquer", (0.92, 0.92, 0.92), roughness=0.2)

    # 沙发（贴北墙）
    add_box("sofa", (0, 2.0, 0.45), (2.0, 0.85, 0.9), sofa_mat)
    # 茶几
    add_box("coffee_table", (0, 0.8, 0.25), (1.2, 0.6, 0.5), table_mat)
    # 电视柜（贴南墙）
    add_box("tv_cabinet", (0, -2.2, 0.35), (2.0, 0.45, 0.7), cabinet_mat)
    # 电视
    tv_mat = add_pbr_material("tv_glass", (0.05, 0.05, 0.05), roughness=0.1)
    add_box("tv", (0, -2.4, 1.2), (1.5, 0.05, 0.9), tv_mat)


def add_lighting():
    """三点布光 + 强窗光（室内场景需要更亮的灯）"""
    # 主光（区域光模拟落地窗，朝东墙内侧）
    bpy.ops.object.light_add(type='AREA', location=(-1.9, 0, 1.5))
    main = bpy.context.object
    main.name = "window_light"
    main.data.energy = 800
    main.data.size = 2.5
    main.rotation_euler = (0, math.radians(90), 0)
    main.data.color = (1.0, 0.95, 0.85)  # 暖白

    # 顶部辅光
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 2.7))
    fill = bpy.context.object
    fill.name = "fill_light"
    fill.data.energy = 300
    fill.data.size = 3.0
    fill.rotation_euler = (math.radians(180), 0, 0)

    # 角落点光（暖橙，制造氛围）
    bpy.ops.object.light_add(type='POINT', location=(1.5, 1.8, 1.2))
    accent = bpy.context.object
    accent.name = "accent_light"
    accent.data.energy = 80
    accent.data.color = (1.0, 0.7, 0.4)


def add_world_hdri_fallback():
    """没有 HDRI 时用纯色环境光打底"""
    world = bpy.data.worlds["World"] if "World" in bpy.data.worlds else bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.85, 0.88, 0.95, 1.0)  # 淡蓝天光
        bg.inputs["Strength"].default_value = 0.8


def add_perspective_camera():
    """45° 透视相机，自动 look-at 房间中心"""
    from mathutils import Vector
    loc = Vector((1.7, -1.7, 1.6))
    target = Vector((0, 1.0, 1.0))  # 看向沙发方向
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.name = "persp_cam"
    cam.data.lens = 18  # 更广角，能看到更多
    direction = target - loc
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    bpy.context.scene.camera = cam
    return cam


def add_pano_camera():
    """360° equirectangular 全景相机（房间中心）"""
    bpy.ops.object.camera_add(location=(0, 0, 1.6))
    cam = bpy.context.object
    cam.name = "pano_cam"
    cam.data.type = 'PANO'
    if hasattr(cam.data, 'panorama_type'):
        cam.data.panorama_type = 'EQUIRECTANGULAR'
    return cam


def setup_render(engine, resolution=(800, 600), samples=64):
    scene = bpy.context.scene
    scene.render.engine = engine  # 'BLENDER_EEVEE' or 'CYCLES'
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    if engine == 'CYCLES':
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
    elif 'EEVEE' in engine:
        if hasattr(scene, 'eevee'):
            scene.eevee.taa_render_samples = samples
    scene.render.image_settings.file_format = 'PNG'


def render_to(filepath):
    bpy.context.scene.render.filepath = filepath
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    return time.time() - t0


def main():
    results = []
    print("\n========== PanoSpec Blender 程序化建房测试 ==========\n")

    # === 1. 建场景 ===
    t0 = time.time()
    clean_scene()
    build_room()
    add_furniture()
    add_lighting()
    add_world_hdri_fallback()
    scene_build_time = time.time() - t0
    print(f"[1] 场景构建耗时: {scene_build_time:.2f}s")
    print(f"    物体数量: {len(bpy.data.objects)}")

    # === 2. EEVEE 透视渲染（800x600，64 samples）===
    add_perspective_camera()
    bpy.context.scene.camera = bpy.data.objects["persp_cam"]
    setup_render('BLENDER_EEVEE', resolution=(800, 600), samples=64)
    dur = render_to(f"{OUTPUT_DIR}/01_eevee_persp.png")
    results.append(("EEVEE 透视 800x600", dur))
    print(f"[2] EEVEE 透视渲染: {dur:.2f}s → 01_eevee_persp.png")

    # === 3. Cycles 透视渲染（800x600，64 samples）===
    setup_render('CYCLES', resolution=(800, 600), samples=64)
    dur = render_to(f"{OUTPUT_DIR}/02_cycles_persp.png")
    results.append(("Cycles 透视 800x600 64spp", dur))
    print(f"[3] Cycles 透视渲染: {dur:.2f}s → 02_cycles_persp.png")

    # === 4. Cycles 360° 全景（1024x512，32 samples）===
    add_pano_camera()
    bpy.context.scene.camera = bpy.data.objects["pano_cam"]
    setup_render('CYCLES', resolution=(1024, 512), samples=32)
    dur = render_to(f"{OUTPUT_DIR}/03_cycles_pano.png")
    results.append(("Cycles 360° 全景 1024x512 32spp", dur))
    print(f"[4] Cycles 360° 全景: {dur:.2f}s → 03_cycles_pano.png")

    # === 总结 ===
    print("\n========== 真实速度汇总 ==========")
    for name, dur in results:
        print(f"  {name:40s} {dur:6.2f}s")
    total = sum(d for _, d in results) + scene_build_time
    print(f"  {'总耗时（场景+3 张渲染）':40s} {total:6.2f}s")
    print("==================================\n")


if __name__ == "__main__":
    main()
