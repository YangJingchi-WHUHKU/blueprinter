# Text2Blender T2S Feasibility Prototype

This directory contains a minimal implementation of the route:

```text
Chinese user prompt -> scene.json -> Blender Python -> scene.glb -> web model-viewer
```

The route is feasible. The hard runtime dependency for actual GLB export is a
working Blender executable.

## Quick Start

Generate a structured scene:

```bash
python3 scripts/parse_prompt.py "生成一个45平米一居室，有卧室、客厅、开放式厨房、卫生间" -o output/scene.json
```

Export to GLB after installing Blender:

```bash
blender --background --python scripts/blender_generate.py -- output/scene.json web/scene.glb
```

The Blender script downloads and caches higher-detail CC0 model assets from
Poly Haven under `assets/polyhaven/` on first run. The generated scene currently
uses imported glTF assets for the sofa, bed, coffee table, stove, cabinet,
bookshelf, ceiling lamp, potted plant, and vase. The current bathroom fixtures
are explicitly registered procedural assets.

Open the viewer:

```bash
python3 -m http.server 8000 -d web
```

Then visit `http://localhost:8000`.

## Files

- `scripts/parse_prompt.py`: deterministic prompt-to-scene prototype.
- `scripts/blender_generate.py`: Blender Python script that builds floors, walls,
  doors, windows, imports cached Poly Haven assets, and exports GLB.
- `schema/scene.schema.json`: scene JSON contract for the LLM output.
- `examples/one_bedroom_45sqm.scene.json`: expected output for the sample prompt.
- `web/index.html`: `<model-viewer>` page for previewing `scene.glb`.

## Integration Notes

For production, replace `scripts/parse_prompt.py` with an LLM call that returns the
same schema. Keep the deterministic parser as a fallback, fixture generator, and
regression test baseline.
