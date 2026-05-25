"""
BluePrinter Blender PoC —— GLB 导出版
程序化建场景 → 导出 GLB → 浏览器用 Three.js 实时交互查看

跑法：
  /Applications/Blender.app/Contents/MacOS/Blender --background --python test_scene_glb.py

输出：
  viewer/scene.glb  （供网页查看器加载）
"""
import bpy
import math
import os
import time
from mathutils import Vector

# GLB 输出到 viewer 目录，方便 web 直接加载
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "viewer")
GLB_PATH = os.path.join(OUTPUT_DIR, "scene.glb")


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
    wall = add_pbr("wall", (0.92, 0.88, 0.78), 0.9)
    floor = add_pbr("oak_floor", (0.72, 0.55, 0.35), 0.5)
    ceil = add_pbr("ceiling", (0.96, 0.94, 0.90), 0.95)

    add_box("floor", (0, 0, 0), (4, 5, 0.05), floor)
    add_box("ceiling", (0, 0, 2.8), (4, 5, 0.05), ceil)
    add_box("wall_n", (0, 2.5, 1.4), (4, 0.1, 2.8), wall)
    add_box("wall_s", (0, -2.5, 1.4), (4, 0.1, 2.8), wall)
    add_box("wall_e_top", (2.0, 0, 2.5), (0.1, 5, 0.6), wall)
    add_box("wall_e_bot", (2.0, 0, 0.4), (0.1, 5, 0.8), wall)
    add_box("wall_e_l", (2.0, 1.7, 1.4), (0.1, 1.6, 2.8), wall)
    add_box("wall_e_r", (2.0, -1.7, 1.4), (0.1, 1.6, 2.8), wall)
    add_box("wall_w", (-2.0, 0, 1.4), (0.1, 5, 2.8), wall)


def add_furniture():
    sofa_mat = add_pbr("sofa", (0.7, 0.68, 0.62), 0.85)
    add_box("sofa_base", (-0.5, 1.8, 0.35), (2.0, 0.85, 0.7), sofa_mat)
    add_box("sofa_back", (-0.5, 2.15, 0.85), (2.0, 0.15, 1.0), sofa_mat)
    pillow = add_pbr("pillow", (0.5, 0.55, 0.6), 0.9)
    add_box("pillow1", (-1.2, 1.7, 0.85), (0.4, 0.4, 0.3), pillow)
    pillow2 = add_pbr("pillow2", (0.85, 0.7, 0.5), 0.9)
    add_box("pillow_2", (0.0, 1.75, 0.85), (0.35, 0.4, 0.3), pillow2)

    table_mat = add_pbr("walnut", (0.35, 0.22, 0.12), 0.3)
    add_box("coffee_table_top", (-0.5, 0.5, 0.45), (1.2, 0.7, 0.05), table_mat)
    add_box("table_leg1", (-1.0, 0.2, 0.225), (0.05, 0.05, 0.45), table_mat)
    add_box("table_leg2", (0.0, 0.2, 0.225), (0.05, 0.05, 0.45), table_mat)
    add_box("table_leg3", (-1.0, 0.8, 0.225), (0.05, 0.05, 0.45), table_mat)
    add_box("table_leg4", (0.0, 0.8, 0.225), (0.05, 0.05, 0.45), table_mat)

    cab_mat = add_pbr("white_lacquer", (0.95, 0.94, 0.92), 0.25)
    add_box("tv_cabinet", (0, -2.2, 0.35), (2.5, 0.45, 0.6), cab_mat)
    add_box("tv", (0, -2.35, 1.25), (1.8, 0.05, 0.9),
            add_pbr("tv", (0.02, 0.02, 0.02), 0.1, metallic=0.3))

    rug_mat = add_pbr("rug", (0.45, 0.4, 0.35), 0.95)
    add_box("rug", (-0.5, 0.8, 0.025), (2.5, 2.2, 0.01), rug_mat)

    lamp_mat = add_pbr("lamp_pole", (0.15, 0.15, 0.15), 0.3, metallic=0.7)
    add_cylinder("lamp_pole", (1.5, 1.8, 0.85), 0.03, 1.7, lamp_mat)
    add_cylinder("lamp_shade", (1.5, 1.8, 1.8), 0.25, 0.3,
                 add_pbr("shade", (0.95, 0.88, 0.7), 0.9))

    pot = add_pbr("pot", (0.4, 0.32, 0.28), 0.7)
    add_cylinder("plant_pot", (-1.6, -1.8, 0.2), 0.2, 0.4, pot)
    leaf = add_pbr("leaves", (0.25, 0.45, 0.2), 0.6)
    add_cylinder("plant_body", (-1.6, -1.8, 0.85), 0.15, 0.9, leaf)


def export_glb():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.time()
    bpy.ops.export_scene.gltf(
        filepath=GLB_PATH,
        export_format='GLB',
        export_apply=True,
        export_materials='EXPORT',
        export_yup=True,
        export_lights=False,
        export_cameras=False,
    )
    return time.time() - t0


def main():
    print("\n========== GLB 导出测试 ==========\n")
    t0 = time.time()
    clean_scene()
    build_room()
    add_furniture()
    scene_time = time.time() - t0
    print(f"[1] 场景构建 ({len(bpy.data.objects)} 物体): {scene_time:.2f}s")

    glb_time = export_glb()
    size_kb = os.path.getsize(GLB_PATH) / 1024
    print(f"[2] GLB 导出: {glb_time:.2f}s ({size_kb:.1f} KB)")
    print(f"    → {GLB_PATH}")
    print(f"\n========== 总耗时 {scene_time + glb_time:.2f}s ==========\n")


if __name__ == "__main__":
    main()
