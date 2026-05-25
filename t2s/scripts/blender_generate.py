"""Build a low-poly apartment scene in Blender and export it as GLB.

Usage:
  blender --background --python scripts/blender_generate.py -- output/scene.json web/scene.glb
"""

from __future__ import annotations

import json
import math
import sys
import urllib.request
from pathlib import Path

import bpy
from mathutils import Vector

try:
    import numpy as np

    if not hasattr(np, "bool"):
        np.bool = bool
except Exception:
    pass


MATERIALS = {
    "wood_floor": (0.74, 0.56, 0.36, 1.0),
    "kitchen_tile": (0.80, 0.82, 0.78, 1.0),
    "bath_tile": (0.66, 0.78, 0.82, 1.0),
    "wall": (0.91, 0.88, 0.82, 1.0),
    "wall_cap": (0.68, 0.65, 0.58, 1.0),
    "door": (0.50, 0.31, 0.16, 1.0),
    "window": (0.42, 0.70, 0.95, 0.36),
    "window_frame": (0.88, 0.90, 0.88, 1.0),
    "sofa": (0.28, 0.44, 0.54, 1.0),
    "cushion": (0.86, 0.78, 0.62, 1.0),
    "bed_frame": (0.45, 0.30, 0.20, 1.0),
    "mattress": (0.92, 0.90, 0.84, 1.0),
    "pillow": (0.76, 0.84, 0.88, 1.0),
    "rug": (0.74, 0.40, 0.34, 1.0),
    "table": (0.48, 0.34, 0.22, 1.0),
    "counter": (0.78, 0.76, 0.68, 1.0),
    "cabinet": (0.40, 0.48, 0.46, 1.0),
    "appliance": (0.16, 0.18, 0.20, 1.0),
    "sanitary": (0.92, 0.92, 0.88, 1.0),
    "shower_glass": (0.62, 0.82, 0.95, 0.30),
    "wardrobe": (0.54, 0.42, 0.32, 1.0),
    "plant": (0.20, 0.48, 0.24, 1.0),
    "pot": (0.48, 0.32, 0.22, 1.0),
    "black": (0.06, 0.07, 0.08, 1.0),
    "metal": (0.62, 0.64, 0.62, 1.0),
}

ROOT_DIR = Path(__file__).resolve().parents[1]
ASSET_CACHE = ROOT_DIR / "assets" / "polyhaven"
POLYHAVEN_LICENSE = "Poly Haven assets are CC0. Source: https://polyhaven.com/license"
POLYHAVEN_MODELS = {
    "sofa": "Sofa_01",
    "bed": "GothicBed_01",
    "table": "modern_coffee_table_01",
    "counter": "electric_stove",
    "wardrobe": "wooden_bookshelf_worn",
    "tv_console": "modern_wooden_cabinet",
}
PROCEDURAL_MODELS = {
    "toilet": "procedural_sanitary_toilet_v1",
    "shower": "procedural_glass_shower_v1",
}

EXTRA_ASSETS = [
    {
        "asset": "modern_ceiling_lamp_01",
        "name": "living_ceiling_lamp",
        "location": (2.25, 2.45, 2.15),
        "rotation_deg": 0,
        "target_size": (0.9, 0.9, 0.42),
    },
    {
        "asset": "potted_plant_01",
        "name": "living_potted_plant",
        "location": (0.55, 0.62, 0.0),
        "rotation_deg": 18,
        "target_size": (0.62, 0.62, 1.2),
    },
    {
        "asset": "ceramic_vase_01",
        "name": "table_ceramic_vase",
        "location": (1.72, 1.35, 0.55),
        "rotation_deg": -15,
        "target_size": (0.25, 0.25, 0.42),
    },
]


def argv_after_double_dash() -> list[str]:
    if "--" not in sys.argv:
        return []
    return sys.argv[sys.argv.index("--") + 1 :]


def load_scene(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def ensure_asset_coverage(scene: dict) -> None:
    missing = []
    for item in scene.get("furniture", []):
        furniture_type = item["type"]
        asset_id = item.get("asset_id") or POLYHAVEN_MODELS.get(furniture_type) or PROCEDURAL_MODELS.get(furniture_type)
        if not asset_id:
            missing.append(f"{item['id']}:{furniture_type}")
    if missing:
        raise ValueError("Missing asset coverage for furniture: " + ", ".join(missing))


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    engines = {item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"


def material(name: str, color: tuple[float, float, float, float]):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = color
        principled.inputs["Roughness"].default_value = 0.58
        if "Metallic" in principled.inputs and name == "metal":
            principled.inputs["Metallic"].default_value = 0.45
        if "Alpha" in principled.inputs:
            principled.inputs["Alpha"].default_value = color[3]
    if color[3] < 1:
        mat.blend_method = "BLEND"
        mat.use_screen_refraction = True
    return mat


def build_materials() -> dict:
    return {name: material(name, color) for name, color in MATERIALS.items()}


def download_file(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    print(f"Downloading {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "Text2Blender/0.1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        path.write_bytes(response.read())


def polyhaven_gltf_path(asset_id: str, resolution: str = "2k") -> Path | None:
    asset_dir = ASSET_CACHE / asset_id / resolution
    gltf_path = asset_dir / f"{asset_id}_{resolution}.gltf"
    if gltf_path.exists():
        return gltf_path

    try:
        request = urllib.request.Request(
            f"https://api.polyhaven.com/files/{asset_id}",
            headers={"User-Agent": "Text2Blender/0.1"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            files = json.load(response)
        gltf_info = files["gltf"][resolution]["gltf"]
        download_file(gltf_info["url"], gltf_path)
        for relative_path, include in gltf_info.get("include", {}).items():
            download_file(include["url"], asset_dir / relative_path)
        (asset_dir / "LICENSE.txt").write_text(POLYHAVEN_LICENSE + "\n", encoding="utf-8")
        return gltf_path
    except Exception as exc:
        print(f"Could not fetch Poly Haven asset {asset_id}: {exc}")
        return None


def imported_objects(before: set[bpy.types.Object]) -> list[bpy.types.Object]:
    return [obj for obj in bpy.context.scene.objects if obj not in before]


def bounds_for_objects(objects: list[bpy.types.Object]):
    corners = []
    for obj in objects:
        if obj.type not in {"MESH", "CURVE", "EMPTY"}:
            continue
        corners.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not corners:
        return None
    min_v = Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners)))
    max_v = Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners)))
    return min_v, max_v


def transform_asset_objects(objects: list[bpy.types.Object], location, target_size, rotation_deg: float, name_prefix: str) -> bool:
    bounds = bounds_for_objects(objects)
    if bounds is None:
        return False
    min_v, max_v = bounds
    size = max_v - min_v
    target = Vector(target_size)
    nonzero = [target[i] / size[i] for i in range(3) if size[i] > 0.0001 and target[i] > 0]
    scale = min(nonzero) if nonzero else 1.0
    center = (min_v + max_v) / 2
    bottom_z = min_v.z
    rotation = math.radians(rotation_deg)
    parent = bpy.data.objects.new(name_prefix, None)
    bpy.context.collection.objects.link(parent)

    for obj in objects:
        obj.name = f"{name_prefix}_{obj.name}"
        obj.parent = parent
        obj.matrix_parent_inverse.identity()

    parent.scale = (scale, scale, scale)
    parent.rotation_euler[2] = rotation
    parent.location = (
        location[0] - center.x * scale,
        location[1] - center.y * scale,
        location[2] - bottom_z * scale,
    )
    return True


def import_polyhaven_asset(asset_id: str, name_prefix: str, location, target_size, rotation_deg: float = 0) -> bool:
    gltf_path = polyhaven_gltf_path(asset_id)
    if gltf_path is None:
        return False
    before = set(bpy.context.scene.objects)
    try:
        bpy.ops.import_scene.gltf(filepath=str(gltf_path))
    except Exception as exc:
        print(f"Could not import {gltf_path}: {exc}")
        return False
    objects = imported_objects(before)
    return transform_asset_objects(objects, location, target_size, rotation_deg, name_prefix)


def polygon_center(points: list[list[float]]) -> tuple[float, float]:
    x = sum(point[0] for point in points) / len(points)
    y = sum(point[1] for point in points) / len(points)
    return x, y


def add_polygon_floor(room: dict, mats: dict) -> None:
    mesh = bpy.data.meshes.new(f"{room['id']}_floor_mesh")
    vertices = [(x, y, 0) for x, y in room["polygon"]]
    faces = [list(range(len(vertices)))]
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(f"floor_{room['id']}_{room['name']}", mesh)
    bpy.context.collection.objects.link(obj)
    floor_mat = mats["wood_floor"]
    if room["type"] == "kitchen":
        floor_mat = mats["kitchen_tile"]
    elif room["type"] == "bathroom":
        floor_mat = mats["bath_tile"]
    obj.data.materials.append(floor_mat)


def add_cube(name: str, location, scale, mat, bevel: float = 0.0) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new(name="soft_edges", type="BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        obj.modifiers.new(name="weighted_normals", type="WEIGHTED_NORMAL")
    return obj


def add_cylinder(name: str, location, radius: float, depth: float, mat, vertices: int = 32) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    obj.modifiers.new(name="weighted_normals", type="WEIGHTED_NORMAL")
    return obj


def rotated_offset(x: float, y: float, rotation_deg: float) -> tuple[float, float]:
    angle = math.radians(rotation_deg)
    return x * math.cos(angle) - y * math.sin(angle), x * math.sin(angle) + y * math.cos(angle)


def add_part(prefix: str, item: dict, suffix: str, offset, size, mat, bevel: float = 0.0) -> bpy.types.Object:
    rotation = item.get("rotation_deg", 0)
    ox, oy = rotated_offset(offset[0], offset[1], rotation)
    base = item["position"]
    obj = add_cube(
        f"{prefix}_{item['id']}_{suffix}",
        (base[0] + ox, base[1] + oy, base[2] + offset[2]),
        size,
        mat,
        bevel,
    )
    obj.rotation_euler[2] = math.radians(rotation)
    return obj


def wall_transform(start: list[float], end: list[float], thickness: float, height: float):
    sx, sy = start
    ex, ey = end
    dx = ex - sx
    dy = ey - sy
    length = math.hypot(dx, dy)
    cx = (sx + ex) / 2
    cy = (sy + ey) / 2
    angle = math.atan2(dy, dx)
    return (cx, cy, height / 2), (length, thickness, height), angle


def add_wall(wall: dict, mats: dict) -> None:
    height = 1.45 if wall.get("kind") == "exterior" else 1.18
    thickness = wall.get("thickness", 0.14)
    location, scale, angle = wall_transform(wall["start"], wall["end"], thickness, height)
    obj = add_cube(f"wall_{wall['id']}", location, scale, mats["wall"], bevel=0.015)
    obj.rotation_euler[2] = angle

    cap_location, cap_scale, _ = wall_transform(wall["start"], wall["end"], thickness + 0.04, 0.05)
    cap = add_cube(f"wall_cap_{wall['id']}", (cap_location[0], cap_location[1], height + 0.025), cap_scale, mats["wall_cap"], bevel=0.01)
    cap.rotation_euler[2] = angle


def wall_direction(wall: dict) -> tuple[float, float, float]:
    sx, sy = wall["start"]
    ex, ey = wall["end"]
    dx = ex - sx
    dy = ey - sy
    length = math.hypot(dx, dy) or 1
    return dx / length, dy / length, math.atan2(dy, dx)


def add_opening_marker(opening: dict, wall: dict, mats: dict, prefix: str) -> None:
    ux, uy, angle = wall_direction(wall)
    nx, ny = -uy, ux
    cx, cy = opening["center"]
    thickness = wall.get("thickness", 0.14) + 0.03

    if prefix == "door":
        obj = add_cube(
            f"door_{opening['id']}",
            (cx + nx * 0.04, cy + ny * 0.04, 0.53),
            (opening["width"], 0.045, 1.06),
            mats["door"],
            bevel=0.012,
        )
        obj.rotation_euler[2] = angle
        handle_offset = opening["width"] * 0.32
        hx = cx + ux * handle_offset + nx * 0.075
        hy = cy + uy * handle_offset + ny * 0.075
        add_cylinder(f"door_handle_{opening['id']}", (hx, hy, 0.72), 0.035, 0.035, mats["metal"], vertices=16)
        return

    z = opening.get("sill_height", 0.75) + min(opening["height"], 0.9) / 2
    glass = add_cube(
        f"window_glass_{opening['id']}",
        (cx + nx * 0.05, cy + ny * 0.05, z),
        (opening["width"], thickness, min(opening["height"], 0.9)),
        mats["window"],
        bevel=0.01,
    )
    glass.rotation_euler[2] = angle
    for side, offset in (("left", -opening["width"] / 2), ("right", opening["width"] / 2)):
        fx = cx + ux * offset + nx * 0.055
        fy = cy + uy * offset + ny * 0.055
        frame = add_cube(f"window_frame_{opening['id']}_{side}", (fx, fy, z), (0.045, thickness + 0.02, 0.98), mats["window_frame"], bevel=0.006)
        frame.rotation_euler[2] = angle


def add_furniture(item: dict, mats: dict) -> None:
    furniture_type = item["type"]
    sx, sy, sz = item["size"]
    asset_id = POLYHAVEN_MODELS.get(furniture_type)
    if asset_id and import_polyhaven_asset(
        asset_id,
        f"asset_{furniture_type}_{item['id']}",
        item["position"],
        (sx, sy, sz),
        item.get("rotation_deg", 0),
    ):
        return

    if furniture_type == "sofa":
        add_part("furniture", item, "seat", (0, 0, -0.12), (sx, sy, 0.28), mats["sofa"], 0.06)
        add_part("furniture", item, "back", (0, sy * 0.42, 0.18), (sx, 0.18, 0.70), mats["sofa"], 0.05)
        add_part("furniture", item, "left_arm", (-sx * 0.45, 0, 0.08), (0.18, sy, 0.48), mats["sofa"], 0.05)
        add_part("furniture", item, "right_arm", (sx * 0.45, 0, 0.08), (0.18, sy, 0.48), mats["sofa"], 0.05)
        add_part("furniture", item, "pillow_a", (-0.42, 0.12, 0.26), (0.45, 0.12, 0.34), mats["cushion"], 0.04)
        add_part("furniture", item, "pillow_b", (0.36, 0.12, 0.26), (0.45, 0.12, 0.34), mats["cushion"], 0.04)
    elif furniture_type == "bed":
        add_part("furniture", item, "frame", (0, 0, -0.08), (sx + 0.18, sy + 0.18, 0.22), mats["bed_frame"], 0.035)
        add_part("furniture", item, "mattress", (0, 0, 0.10), (sx, sy, 0.24), mats["mattress"], 0.05)
        add_part("furniture", item, "pillow_l", (-sx * 0.24, sy * 0.32, 0.28), (0.55, 0.28, 0.16), mats["pillow"], 0.04)
        add_part("furniture", item, "pillow_r", (sx * 0.24, sy * 0.32, 0.28), (0.55, 0.28, 0.16), mats["pillow"], 0.04)
    elif furniture_type == "table":
        add_part("furniture", item, "top", (0, 0, 0.14), (sx, sy, 0.08), mats["table"], 0.025)
        for ix in (-0.38, 0.38):
            for iy in (-0.18, 0.18):
                add_part("furniture", item, f"leg_{ix}_{iy}", (ix, iy, -0.12), (0.07, 0.07, 0.32), mats["table"], 0.01)
    elif furniture_type == "tv_console":
        add_part("furniture", item, "console", (0, 0, -0.06), (sx, sy, 0.28), mats["cabinet"], 0.02)
        add_part("furniture", item, "screen", (-0.03, 0, 0.42), (0.05, sy * 0.88, 0.62), mats["black"], 0.012)
    elif furniture_type == "counter":
        add_part("furniture", item, "base", (0, 0, 0), (sx, sy, sz), mats["counter"], 0.025)
        add_part("furniture", item, "sink", (-sx * 0.25, 0, 0.50), (0.55, 0.38, 0.04), mats["metal"], 0.02)
        add_part("furniture", item, "cooktop", (sx * 0.25, 0, 0.51), (0.50, 0.34, 0.035), mats["black"], 0.015)
    elif furniture_type == "wardrobe":
        add_part("furniture", item, "body", (0, 0, 0), (sx, sy, sz), mats["wardrobe"], 0.025)
        add_part("furniture", item, "handle_a", (-sx * 0.08, -sy * 0.48, 0.05), (0.025, 0.035, sz * 0.55), mats["metal"], 0.006)
        add_part("furniture", item, "handle_b", (sx * 0.08, -sy * 0.48, 0.05), (0.025, 0.035, sz * 0.55), mats["metal"], 0.006)
    elif furniture_type == "toilet":
        add_part("furniture", item, "tank", (0, 0.22, 0.15), (0.46, 0.16, 0.42), mats["sanitary"], 0.04)
        add_cylinder(f"furniture_{item['id']}_bowl", tuple(item["position"]), 0.26, 0.28, mats["sanitary"], vertices=32)
    elif furniture_type == "shower":
        add_part("furniture", item, "base", (0, 0, -0.88), (sx, sy, 0.12), mats["sanitary"], 0.025)
        add_part("furniture", item, "glass_a", (0, -sy * 0.48, 0), (sx, 0.035, sz), mats["shower_glass"], 0.01)
        add_part("furniture", item, "glass_b", (-sx * 0.48, 0, 0), (0.035, sy, sz), mats["shower_glass"], 0.01)
    else:
        add_part("furniture", item, "body", (0, 0, 0), (sx, sy, sz), mats["cabinet"], 0.02)


def add_decor(scene: dict, mats: dict) -> None:
    add_cube("rug_living", (1.8, 1.75, 0.025), (2.35, 1.45, 0.04), mats["rug"], bevel=0.03)
    add_cube("rug_bedroom", (2.0, 5.8, 0.025), (2.35, 1.85, 0.035), mats["rug"], bevel=0.025)
    add_cube("kitchen_backsplash", (5.45, 0.08, 0.88), (2.3, 0.04, 0.56), mats["bath_tile"], bevel=0.006)
    for asset in EXTRA_ASSETS:
        if not import_polyhaven_asset(
            asset["asset"],
            f"asset_{asset['name']}",
            asset["location"],
            asset["target_size"],
            asset["rotation_deg"],
        ):
            if "plant" in asset["name"]:
                add_cylinder("plant_pot", (0.55, 0.55, 0.18), 0.18, 0.36, mats["pot"], vertices=24)
                add_cylinder("plant_greenery", (0.55, 0.55, 0.62), 0.28, 0.42, mats["plant"], vertices=24)


def add_room_labels(scene: dict) -> None:
    for room in scene["rooms"]:
        x, y = polygon_center(room["polygon"])
        bpy.ops.object.text_add(location=(x, y, 0.03), rotation=(0, 0, 0))
        obj = bpy.context.object
        obj.name = f"label_{room['id']}"
        obj.data.body = room["name"]
        obj.data.align_x = "CENTER"
        obj.data.align_y = "CENTER"
        obj.data.size = 0.28
        bpy.ops.object.convert(target="MESH")


def add_camera_and_light(scene: dict) -> None:
    points = [point for room in scene["rooms"] for point in room["polygon"]]
    min_x = min(point[0] for point in points)
    max_x = max(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_y = max(point[1] for point in points)
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    span = max(max_x - min_x, max_y - min_y)

    bpy.ops.object.light_add(type="AREA", location=(cx, cy, 6))
    light = bpy.context.object
    light.name = "main_area_light"
    light.data.energy = 450
    light.data.size = span

    bpy.ops.object.light_add(type="POINT", location=(cx - span * 0.35, cy + span * 0.2, 2.7))
    accent = bpy.context.object
    accent.name = "warm_interior_light"
    accent.data.energy = 90
    accent.data.color = (1.0, 0.84, 0.62)

    bpy.ops.object.camera_add(location=(cx, cy - span * 1.0, span * 0.82), rotation=(math.radians(60), 0, 0))
    camera = bpy.context.object
    direction = Vector((cx, cy, 0)) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = camera


def build_scene(scene: dict) -> None:
    reset_scene()
    mats = build_materials()
    walls = {wall["id"]: wall for wall in scene["walls"]}

    for room in scene["rooms"]:
        add_polygon_floor(room, mats)
    add_decor(scene, mats)
    for wall in scene["walls"]:
        add_wall(wall, mats)
    for door in scene["doors"]:
        add_opening_marker(door, walls[door["wall_id"]], mats, "door")
    for window in scene["windows"]:
        add_opening_marker(window, walls[window["wall_id"]], mats, "window")
    for item in scene["furniture"]:
        add_furniture(item, mats)

    add_room_labels(scene)
    add_camera_and_light(scene)


def export_glb(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB")


def main() -> None:
    args = argv_after_double_dash()
    if len(args) != 2:
        raise SystemExit("Expected: blender --background --python scripts/blender_generate.py -- scene.json scene.glb")

    scene_path = Path(args[0])
    output_path = Path(args[1])
    scene = load_scene(scene_path)
    ensure_asset_coverage(scene)
    build_scene(scene)
    export_glb(output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
