#!/usr/bin/env python3
"""Deterministic prompt-to-scene prototype.

This is intentionally small and dependency-free. In production the LLM should
produce the same schema directly, while this script remains useful as a fixture
generator and fallback for common Chinese apartment prompts.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_PROMPT = "生成一个45平米一居室，有卧室、客厅、开放式厨房、卫生间"


def extract_area(prompt: str, default: float = 45.0) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:平米|平方米|m2|㎡)", prompt, re.I)
    return float(match.group(1)) if match else default


def one_bedroom_scene(prompt: str) -> dict[str, Any]:
    area = extract_area(prompt)
    width = 6.7
    depth = round(area / width, 2)
    service_x = 4.2
    service_split_y = 2.4
    bedroom_y = round(depth - 2.12, 2)

    return {
        "unit": "m",
        "metadata": {
            "name": f"{int(area)}sqm_one_bedroom",
            "source_prompt": prompt,
            "area_sqm": area,
            "style": "simple_placeholder",
        },
        "rooms": [
            {
                "id": "living",
                "name": "客厅",
                "type": "living_room",
                "polygon": [[0, 0], [service_x, 0], [service_x, bedroom_y], [0, bedroom_y]],
                "height": 2.8,
            },
            {
                "id": "kitchen",
                "name": "开放式厨房",
                "type": "kitchen",
                "polygon": [[service_x, 0], [width, 0], [width, service_split_y], [service_x, service_split_y]],
                "height": 2.8,
            },
            {
                "id": "bath",
                "name": "卫生间",
                "type": "bathroom",
                "polygon": [[service_x, service_split_y], [width, service_split_y], [width, bedroom_y], [service_x, bedroom_y]],
                "height": 2.8,
            },
            {
                "id": "bedroom",
                "name": "卧室",
                "type": "bedroom",
                "polygon": [[0, bedroom_y], [width, bedroom_y], [width, depth], [0, depth]],
                "height": 2.8,
            },
        ],
        "walls": [
            {"id": "w_south", "start": [0, 0], "end": [width, 0], "height": 2.8, "thickness": 0.16, "kind": "exterior"},
            {"id": "w_east", "start": [width, 0], "end": [width, depth], "height": 2.8, "thickness": 0.16, "kind": "exterior"},
            {"id": "w_north", "start": [width, depth], "end": [0, depth], "height": 2.8, "thickness": 0.16, "kind": "exterior"},
            {"id": "w_west", "start": [0, depth], "end": [0, 0], "height": 2.8, "thickness": 0.16, "kind": "exterior"},
            {"id": "w_bed_living", "start": [0, bedroom_y], "end": [width, bedroom_y], "height": 2.8, "thickness": 0.12, "kind": "interior"},
            {"id": "w_living_service", "start": [service_x, 0], "end": [service_x, bedroom_y], "height": 2.8, "thickness": 0.12, "kind": "interior"},
            {"id": "w_kitchen_bath", "start": [service_x, service_split_y], "end": [width, service_split_y], "height": 2.8, "thickness": 0.12, "kind": "interior"},
        ],
        "doors": [
            {"id": "d_entry", "wall_id": "w_south", "center": [1.1, 0], "width": 0.9, "height": 2.1, "sill_height": 0, "swing": "left"},
            {"id": "d_bedroom", "wall_id": "w_bed_living", "center": [1.2, bedroom_y], "width": 0.8, "height": 2.1, "sill_height": 0, "swing": "right"},
            {"id": "d_bath", "wall_id": "w_kitchen_bath", "center": [5.45, service_split_y], "width": 0.75, "height": 2.1, "sill_height": 0, "swing": "left"},
        ],
        "windows": [
            {"id": "win_living", "wall_id": "w_west", "center": [0, 2.5], "width": 1.6, "height": 1.2, "sill_height": 0.9, "swing": "none"},
            {"id": "win_bedroom", "wall_id": "w_north", "center": [3.5, depth], "width": 2.0, "height": 1.2, "sill_height": 0.9, "swing": "none"},
            {"id": "win_kitchen", "wall_id": "w_east", "center": [width, 1.2], "width": 1.1, "height": 1.0, "sill_height": 1.1, "swing": "none"},
        ],
        "furniture": [
            {"id": "sofa", "type": "sofa", "room_id": "living", "position": [1.8, 2.4, 0.35], "size": [2.0, 0.85, 0.7], "rotation_deg": 0, "label": "沙发"},
            {"id": "coffee_table", "type": "table", "room_id": "living", "position": [1.8, 1.35, 0.25], "size": [1.0, 0.55, 0.5], "rotation_deg": 0, "label": "茶几"},
            {"id": "tv", "type": "tv_console", "room_id": "living", "position": [3.75, 2.1, 0.35], "size": [0.25, 1.4, 0.7], "rotation_deg": 90, "label": "电视柜"},
            {"id": "kitchen_counter", "type": "counter", "room_id": "kitchen", "position": [5.45, 0.45, 0.45], "size": [2.2, 0.6, 0.9], "rotation_deg": 0, "label": "橱柜"},
            {"id": "bed", "type": "bed", "room_id": "bedroom", "position": [2.0, round((bedroom_y + depth) / 2, 2), 0.3], "size": [2.0, 1.5, 0.6], "rotation_deg": 0, "label": "床"},
            {"id": "wardrobe", "type": "wardrobe", "room_id": "bedroom", "position": [5.7, bedroom_y + 0.75, 1.05], "size": [0.6, 1.8, 2.1], "rotation_deg": 0, "label": "衣柜"},
            {"id": "toilet", "type": "toilet", "room_id": "bath", "position": [5.95, 3.75, 0.35], "size": [0.45, 0.7, 0.7], "rotation_deg": 0, "label": "马桶"},
            {"id": "shower", "type": "shower", "room_id": "bath", "position": [4.75, 3.65, 1.0], "size": [0.9, 0.9, 2.0], "rotation_deg": 0, "label": "淋浴"},
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="?", default=DEFAULT_PROMPT)
    parser.add_argument("-o", "--output", default="output/scene.json")
    args = parser.parse_args()

    scene = one_bedroom_scene(args.prompt)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
