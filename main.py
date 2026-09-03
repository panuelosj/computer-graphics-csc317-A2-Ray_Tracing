#!/usr/bin/env python3
"""Assignment 2 demo backend (ray casting + ray tracing).

Loads a JSON scene and renders it with your ``src/`` functions, writing the
results next to this script under ``out/``:

* Part 1 (ray casting): false-colour ``id``, ``depth`` and ``normal`` images.
* Part 2 (ray tracing): the lit RGB image (as ``.png`` and ``.ppm``).

Usage:
    python main.py                                  # default scene, 320x180
    python main.py --scene data/two-spheres-and-plane.json
    python main.py --height 360                     # bigger; width follows the camera
    python main.py --part 2                         # only the lit render
    python main.py --stages                         # one image per shading term
    python main.py --scene data/bunny.json --accel  # BVH-assisted (mesh scenes)
    python main.py --headless                       # (default) just write files

The ``--headless`` flag is the default-safe path: it never opens a window, it
only writes images, so it works in CI / over SSH.
"""

import argparse
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# `cgcommon` (shared helpers) normally sits next to this file. If several
# assignments are checked out together it lives two levels up instead.
if not os.path.isdir(os.path.join(HERE, "cgcommon")):
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from cgcommon.image import save_png, write_ppm
from backend.scene import (
    load_scene, load_scene_settings, render_part1, render_part2, render_stage,
    image_size, STAGES, STAGE_BLURB,
)

from src.viewing_ray import viewing_ray
from src.first_hit import first_hit
from src.raycolor import raycolor
from src.blinn_phong_shading import blinn_phong_shading


def main(argv=None):
    parser = argparse.ArgumentParser(description="A2 ray tracer demo.")
    parser.add_argument("--scene", default=os.path.join(HERE, "data", "sphere-and-plane.json"))
    parser.add_argument(
        "--width", type=int, default=None,
        help="image width in pixels. Omit it and the width is derived from "
             "the scene camera's aspect ratio, so pixels stay square",
    )
    parser.add_argument(
        "--height", type=int, default=None,
        help="image height in pixels (default 180, or derived from --width)",
    )
    parser.add_argument("--part", type=int, default=0, choices=[0, 1, 2],
                        help="0 = both parts (default), 1 = casting, 2 = tracing")
    parser.add_argument("--headless", action="store_true",
                        help="write images without opening a window (default behaviour)")
    parser.add_argument(
        "--stages", action="store_true",
        help="render the shading model one term at a time (ambient, +diffuse, "
             "+specular, +shadows, +reflection) — the fastest way to see which "
             "term is wrong",
    )
    parser.add_argument(
        "--stage", default=None, choices=list(STAGES), metavar="NAME",
        help="render just one stage (implies --stages)",
    )
    parser.add_argument(
        "--accel", dest="accel", action="store_true", default=None,
        help="force soup acceleration ON for this run, whatever "
             "the scene file says (see \"accelerate\" in the scene JSON)",
    )
    parser.add_argument(
        "--no-accel", dest="accel", action="store_false",
        help="force it OFF, e.g. to time the honest brute-force cost",
    )
    args = parser.parse_args(argv)
    if args.stage:
        args.stages = True

    camera, objects, lights = load_scene(args.scene)
    settings = load_scene_settings(args.scene)
    # The scene decides; --accel / --no-accel override it for one run.
    use_accel = settings["accelerate"] if args.accel is None else args.accel
    accelerated = []
    if use_accel:
        from backend.accel import accelerate
        accelerated = accelerate(objects)
    # The scene's camera describes the image plane in scene units; the pixel
    # grid has to match its shape or the picture comes out stretched.
    W, H = image_size(camera, args.width, args.height)
    out_dir = os.path.join(HERE, "out")
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(args.scene))[0]

    print(f"Scene {base!r}: {len(objects)} objects, {len(lights)} lights, {W}x{H}")
    if use_accel:
        src = "scene file" if args.accel is None else "command line"
        print(f"  acceleration ON (from the {src}); the image is unchanged")

    if args.stages:
        wanted = [args.stage] if args.stage else list(STAGES)
        stage_dir = os.path.join(out_dir, f"{base}.stages")
        os.makedirs(stage_dir, exist_ok=True)
        print("  Rendering one image per shading term. Compare them in order:")
        print("  the FIRST one that looks wrong is the term to debug.\n")
        for k, stage in enumerate(wanted, start=1):
            t0 = time.time()
            img = render_stage(camera, objects, lights, W, H, stage,
                               viewing_ray, first_hit, blinn_phong_shading,
                               raycolor)
            name = f"{k}-{stage}.png" if not args.stage else f"{stage}.png"
            save_png(os.path.join(stage_dir, name), img)
            print(f"    {stage:<11} {STAGE_BLURB[stage]}")
            print(f"    {'':<11} -> out/{base}.stages/{name}  ({time.time()-t0:.1f}s)")
        print(f"\n  All stages written to out/{base}.stages/.")
        print("  Reference versions of these images are in the assignment README.")
        return 0

    if args.part in (0, 1):
        t0 = time.time()
        id_img, depth_img, normal_img = render_part1(
            camera, objects, W, H, viewing_ray, first_hit
        )
        save_png(os.path.join(out_dir, f"{base}.id.png"), id_img)
        save_png(os.path.join(out_dir, f"{base}.depth.png"), depth_img)
        save_png(os.path.join(out_dir, f"{base}.normal.png"), normal_img)
        write_ppm(os.path.join(out_dir, f"{base}.id.ppm"), id_img)
        print(f"  Part 1 (casting) wrote id/depth/normal PNGs in {time.time()-t0:.1f}s")

    if args.part in (0, 2):
        t0 = time.time()
        rgb = render_part2(camera, objects, lights, W, H, viewing_ray, raycolor)
        save_png(os.path.join(out_dir, f"{base}.rgb.png"), rgb)
        write_ppm(os.path.join(out_dir, f"{base}.rgb.ppm"), rgb)
        print(f"  Part 2 (tracing) wrote {base}.rgb.png in {time.time()-t0:.1f}s")

    if use_accel and accelerated:
        from backend.accel import describe
        print(describe(accelerated))
    print(f"\nDone. Open the PNGs in {os.path.relpath(out_dir, HERE)}/ to view your results.")


if __name__ == "__main__":
    main()
