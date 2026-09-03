"""Debugging hints shown when a check fails.

Both ``run_tests.py`` and ``check_my_work.py`` print the hint for each failing
function, so a red row comes with a suggestion for what to look at next rather
than just a message. Checks that share a hint are grouped, so each piece of
advice appears once.

This file is part of the test backend -- you do not need to edit it.
"""

STAGE_HINT = """\
Render the shading model one term at a time, then find the FIRST image that
looks wrong -- that is the term to debug:

    python main.py --stages --width 200 --height 112
    python main.py --stages --scene data/two-spheres-and-plane.json
    python main.py --stage shadows        # just one term, if you know which

Writes out/<scene>.stages/1-ambient.png ... 5-reflection.png. The assignment
README shows what each stage should look like for sphere-and-plane."""

GEOMETRY_HINT = """\
Check the geometry before worrying about shading -- Part 1 renders the raw
intersection results as false colour:

    python main.py --part 1 --width 320 --height 180

Writes out/<scene>.id.png, .depth.png and .normal.png. Missing objects point at
the hit test or at min_t; a flat or banded normal image points at the normal."""

HINTS = {
    # Part 1: geometry
    "viewing_ray": GEOMETRY_HINT,
    "sphere_intersect": GEOMETRY_HINT,
    "plane_intersect": GEOMETRY_HINT,
    "triangle_intersect": GEOMETRY_HINT,
    "first_hit": GEOMETRY_HINT,
    # Part 2: shading
    "reflect": STAGE_HINT,
    "point_light_direction": STAGE_HINT,
    "directional_light_direction": STAGE_HINT,
    "blinn_phong_shading": STAGE_HINT,
    "raycolor": STAGE_HINT,
}
