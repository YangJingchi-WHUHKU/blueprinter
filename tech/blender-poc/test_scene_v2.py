"""
PanoSpec Blender 测试 v2 —— 加入「自动化决策智能层」
对比 v1（裸光）vs v2（HDRI + 曝光 + 后期 + 更多家具）
"""
import bpy
import math
import time
from mathutils import Vector

OUTPUT_DIR = "/tmp/blender_test"


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def add_pbr(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_box(name, location, scale, material=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    if material:
        obj.data.materials.append(material)
    return obj


def add_cylinder(name, location, radius, depth, material=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj


def build_room():
    """日式风格客厅 4x5x2.8"""
    # 浅原木色调
    wall = add_pbr("wall", (0.92, 0.88, 0.78), 0.9)  # 米黄墙
    floor = add_pbr("oak_floor", (0.72, 0.55, 0.35), 0.5)  # 浅橡木
    ceil = add_pbr("ceiling", (0.96, 0.94, 0.90), 0.95)

    add_box("floor", (0, 0, 0), (4, 5, 0.05), floor)
    add_box("ceiling", (0, 0, 2.8), (4, 5, 0.05), ceil)
    add_box("wall_n", (0, 2.5, 1.4), (4, 0.1, 2.8), wall)
    add_box("wall_s", (0, -2.5, 1.4), (4, 0.1, 2.8), wall)
    # 东墙留窗洞
    add_box("wall_e_top", (2.0, 0, 2.5), (0.1, 5, 0.6), wall)
    add_box("wall_e_bot", (2.0, 0, 0.4), (0.1, 5, 0.8), wall)
    add_box("wall_e_l", (2.0, 1.7, 1.4), (0.1, 1.6, 2.8), wall)
    add_box("wall_e_r", (2.0, -1.7, 1.4), (0.1, 1.6, 2.8), wall)
    add_box("wall_w", (-2.0, 0, 1.4), (0.1, 5, 2.8), wall)


def add_furniture():
    """更多家具增加真实感"""
    # 沙发 - 浅灰布艺
    sofa_mat = add_pbr("sofa", (0.7, 0.68, 0.62), 0.85)
    add_box("sofa_base", (-0.5, 1.8, 0.35), (2.0, 0.85, 0.7), sofa_mat)
    add_box("sofa_back", (-0.5, 2.15, 0.85), (2.0, 0.15, 1.0), sofa_mat)
    # 靠枕（错位摆，制造"生活感"）
    pillow = add_pbr("pillow", (0.5, 0.55, 0.6), 0.9)
    add_box("pillow1", (-1.2, 1.7, 0.85), (0.4, 0.4, 0.3), pillow)
    pillow2 = add_pbr("pillow2", (0.85, 0.7, 0.5), 0.9)
    add_box("pillow_2", (0.0, 1.75, 0.85), (0.35, 0.4, 0.3), pillow2)

    # 茶几 - 实木
    table_mat = add_pbr("walnut", (0.35, 0.22, 0.12), 0.3)
    add_box("coffee_table_top", (-0.5, 0.5, 0.45), (1.2, 0.7, 0.05), table_mat)
    add_box("table_leg1", (-1.0, 0.2, 0.225), (0.05, 0.05, 0.45), table_mat)
    add_box("table_leg2", (0.0, 0.2, 0.225), (0.05, 0.05, 0.45), table_mat)
    add_box("table_leg3", (-1.0, 0.8, 0.225), (0.05, 0.05, 0.45), table_mat)
    add_box("table_leg4", (0.0, 0.8, 0.225), (0.05, 0.05, 0.45), table_mat)

    # 电视柜
    cab_mat = add_pbr("white_lacquer", (0.95, 0.94, 0.92), 0.25)
    add_box("tv_cabinet", (0, -2.2, 0.35), (2.5, 0.45, 0.6), cab_mat)
    # 电视
    add_box("tv", (0, -2.35, 1.25), (1.8, 0.05, 0.9), add_pbr("tv", (0.02, 0.02, 0.02), 0.1))

    # 地毯（在茶几下）
    rug_mat = add_pbr("rug", (0.45, 0.4, 0.35), 0.95)
    add_box("rug", (-0.5, 0.8, 0.025), (2.5, 2.2, 0.01), rug_mat)

    # 落地灯
    lamp_mat = add_pbr("lamp_pole", (0.15, 0.15, 0.15), 0.3, metallic=0.7)
    add_cylinder("lamp_pole", (1.5, 1.8, 0.85), 0.03, 1.7, lamp_mat)
    add_cylinder("lamp_shade", (1.5, 1.8, 1.8), 0.25, 0.3,
                 add_pbr("shade", (0.95, 0.88, 0.7), 0.9))

    # 角落植物（圆柱+盆）
    pot = add_pbr("pot", (0.4, 0.32, 0.28), 0.7)
    add_cylinder("plant_pot", (-1.6, -1.8, 0.2), 0.2, 0.4, pot)
    leaf = add_pbr("leaves", (0.25, 0.45, 0.2), 0.6)
    add_cylinder("plant_body", (-1.6, -1.8, 0.85), 0.15, 0.9, leaf)


def add_lighting_pro():
    """v2 决策智能层：曝光受控的三点布光"""
    # 主光（窗光），从东墙窗洞射入
    bpy.ops.object.light_add(type='AREA', location=(1.95, 0, 1.4))
    main = bpy.context.object
    main.name = "window_light"
    main.data.energy = 80   # 调低，避免过曝
    main.data.size = 1.6
    main.rotation_euler = (0, math.radians(-90), 0)
    main.data.color = (1.0, 0.96, 0.88)

    # 天花板均匀辅光（模拟室内反光）
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 2.75))
    fill = bpy.context.object
    fill.name = "fill"
    fill.data.energy = 30
    fill.data.size = 4.0
    fill.rotation_euler = (math.radians(180), 0, 0)
    fill.data.color = (0.95, 0.97, 1.0)

    # 落地灯局部暖光
    bpy.ops.object.light_add(type='POINT', location=(1.5, 1.8, 1.75))
    accent = bpy.context.object
    accent.name = "lamp_glow"
    accent.data.energy = 30
    accent.data.color = (1.0, 0.78, 0.5)


def setup_world_sky():
    """v2 决策智能层：用 procedural sky 代替平涂背景，HDRI 效果"""
    world = bpy.data.worlds["World"] if "World" in bpy.data.worlds else bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    bg = nodes.new("ShaderNodeBackground")
    sky = nodes.new("ShaderNodeTexSky")
    out = nodes.new("ShaderNodeOutputWorld")

    # Nishita sky model（真实大气散射）
    if hasattr(sky, 'sky_type'):
        try:
            sky.sky_type = 'NISHITA'
            sky.sun_elevation = math.radians(35)
            sky.sun_rotation = math.radians(120)
        except Exception:
            pass

    bg.inputs["Strength"].default_value = 0.5

    links.new(sky.outputs["Color"], bg.inputs["Color"])
    links.new(bg.outputs["Background"], out.inputs["Surface"])


def setup_color_management(exposure=0.0, gamma=1.0, look="None"):
    """v2 决策智能层：颜色管理 + 后期色调"""
    scene = bpy.context.scene
    scene.view_settings.view_transform = 'AgX'  # AgX = 现代电影色彩
    scene.view_settings.exposure = exposure
    scene.view_settings.gamma = gamma
    if look in {"AgX - Punchy", "AgX - Greyscale", "None"}:
        try:
            scene.view_settings.look = look
        except Exception:
            pass


def add_perspective_camera():
    loc = Vector((1.5, -1.8, 1.55))
    target = Vector((-0.3, 1.0, 0.8))
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.name = "persp_cam"
    cam.data.lens = 20
    direction = target - loc
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam


def add_pano_camera():
    bpy.ops.object.camera_add(location=(0, 0, 1.6))
    cam = bpy.context.object
    cam.name = "pano_cam"
    cam.data.type = 'PANO'
    if hasattr(cam.data, 'panorama_type'):
        cam.data.panorama_type = 'EQUIRECTANGULAR'


def setup_render(engine, resolution=(800, 600), samples=64):
    scene = bpy.context.scene
    scene.render.engine = engine
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


def render(filepath):
    bpy.context.scene.render.filepath = filepath
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    return time.time() - t0


def main():
    print("\n========== v2 决策智能层测试 ==========\n")
    t0 = time.time()
    clean_scene()
    build_room()
    add_furniture()
    add_lighting_pro()
    setup_world_sky()
    setup_color_management(exposure=-0.3, gamma=1.0, look="AgX - Punchy")
    scene_time = time.time() - t0
    print(f"[1] v2 场景（更多家具+procedural sky+曝光控制）: {scene_time:.2f}s")
    print(f"    物体数量: {len(bpy.data.objects)}")

    add_perspective_camera()
    bpy.context.scene.camera = bpy.data.objects["persp_cam"]

    setup_render('BLENDER_EEVEE', (1024, 768), samples=64)
    d1 = render(f"{OUTPUT_DIR}/v2_01_eevee.png")
    print(f"[2] EEVEE 1024x768: {d1:.2f}s")

    setup_render('CYCLES', (1024, 768), samples=128)
    d2 = render(f"{OUTPUT_DIR}/v2_02_cycles.png")
    print(f"[3] Cycles 1024x768 128spp: {d2:.2f}s")

    add_pano_camera()
    bpy.context.scene.camera = bpy.data.objects["pano_cam"]
    setup_render('CYCLES', (2048, 1024), samples=64)
    d3 = render(f"{OUTPUT_DIR}/v2_03_cycles_pano.png")
    print(f"[4] Cycles 2K 全景 64spp: {d3:.2f}s")

    print("\n========== v2 汇总 ==========")
    print(f"  场景构建：{scene_time:.2f}s")
    print(f"  EEVEE 1K：{d1:.2f}s")
    print(f"  Cycles 1K：{d2:.2f}s")
    print(f"  Cycles 2K 全景：{d3:.2f}s")
    print(f"  TOTAL：{scene_time + d1 + d2 + d3:.2f}s")
    print("==============================\n")


if __name__ == "__main__":
    main()
