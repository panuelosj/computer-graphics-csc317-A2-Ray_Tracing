"""Unit checks for Assignment 2 (Ray Tracing).

Each check exercises one function in ``src/`` against the golden fixtures in
``tests/golden/a2_golden.npz``. The same checks are used by ``run_tests.py``
(for students) and by the grader. Marks per check mirror the marking scheme.
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ASSIGN = os.path.dirname(HERE)
sys.path.insert(0, ASSIGN)   # so `backend` resolves

from cgcommon.testkit import Check, fixture_path, data_dir
from cgcommon.imagediff import report as _image_report
from backend.scene import (
    Camera, Ray, first_hit_demo_scene, soup_demo_scene, load_scene,
    render_part2,
)

_GOLDEN = None


def golden():
    global _GOLDEN
    if _GOLDEN is None:
        path = fixture_path(os.path.join(HERE, "golden", "a2_golden.npz"))
        _GOLDEN = np.load(path)
    return _GOLDEN


def _scene_variant(g):
    """Which demo-scene geometry this fixture was baked against."""
    return str(g["scene_variant"]) if "scene_variant" in g.files else "public"


def _scene_path(g):
    """Path to the .json scene this fixture was baked against."""
    name = str(g["scene_name"]) if "scene_name" in g.files else "sphere-and-plane.json"
    return os.path.join(data_dir(os.path.join(ASSIGN, "data")), name)


# --- individual checks ------------------------------------------------------

def check_viewing_ray():
    from src.viewing_ray import viewing_ray
    g = golden()
    cam = Camera(eye=g["cam_eye"], u=g["cam_u"], v=g["cam_v"], w=g["cam_w"],
                 d=float(g["cam_d"]), width=float(g["cam_width"]),
                 height=float(g["cam_height"]))
    W, H = int(g["vr_W"]), int(g["vr_H"])
    for r, (i, j) in enumerate(g["vr_pix"]):
        ray = viewing_ray(cam, int(i), int(j), W, H)
        assert np.allclose(ray.origin, g["vr_origin"][r], atol=1e-9), \
            f"viewing_ray: wrong origin for pixel {(int(i), int(j))}"
        assert np.allclose(ray.direction, g["vr_dir"][r], atol=1e-9), \
            f"viewing_ray: wrong direction for pixel {(int(i), int(j))}"


def check_sphere_intersect():
    from src.sphere_intersect import sphere_intersect
    g = golden()
    center, radius = g["sph_center"], float(g["sph_radius"])
    for r in range(len(g["sph_hit"])):
        ray = Ray(g["sph_ro"][r], g["sph_rd"][r])
        hit, t, n = sphere_intersect(center, radius, ray, float(g["sph_min_t"][r]))
        assert bool(hit) == bool(g["sph_hit"][r]), f"sphere_intersect: wrong hit flag on ray {r}"
        if g["sph_hit"][r]:
            assert np.isclose(t, g["sph_tt"][r], atol=1e-7), f"sphere_intersect: wrong t on ray {r}"
            assert np.allclose(n, g["sph_n"][r], atol=1e-7), f"sphere_intersect: wrong normal on ray {r}"


def check_plane_intersect():
    from src.plane_intersect import plane_intersect
    g = golden()
    for r in range(len(g["pl_hit"])):
        ray = Ray(g["pl_ro"][r], g["pl_rd"][r])
        hit, t, n = plane_intersect(g["pl_point"], g["pl_normal"], ray, float(g["pl_min_t"][r]))
        assert bool(hit) == bool(g["pl_hit"][r]), f"plane_intersect: wrong hit flag on ray {r}"
        if g["pl_hit"][r]:
            assert np.isclose(t, g["pl_tt"][r], atol=1e-7), f"plane_intersect: wrong t on ray {r}"
            assert np.allclose(n, g["pl_n"][r], atol=1e-7), f"plane_intersect: wrong normal on ray {r}"


def check_triangle_intersect():
    from src.triangle_intersect import triangle_intersect
    g = golden()
    for r in range(len(g["tri_hit"])):
        ray = Ray(g["tri_ro"][r], g["tri_rd"][r])
        hit, t, n = triangle_intersect(g["tri_a"], g["tri_b"], g["tri_c"], ray, float(g["tri_min_t"][r]))
        assert bool(hit) == bool(g["tri_hit"][r]), f"triangle_intersect: wrong hit flag on ray {r}"
        if g["tri_hit"][r]:
            assert np.isclose(t, g["tri_tt"][r], atol=1e-7), f"triangle_intersect: wrong t on ray {r}"
            # normal may point either way; compare up to sign
            assert (np.allclose(n, g["tri_n"][r], atol=1e-7) or
                    np.allclose(n, -g["tri_n"][r], atol=1e-7)), \
                f"triangle_intersect: wrong normal on ray {r}"


def check_first_hit():
    from src.first_hit import first_hit
    g = golden()
    objects = first_hit_demo_scene(_scene_variant(g))
    for r in range(len(g["fh_hit"])):
        ray = Ray(g["fh_ro"][r], g["fh_rd"][r])
        hit, hit_id, t, n = first_hit(ray, 1.0, objects)
        assert bool(hit) == bool(g["fh_hit"][r]), f"first_hit: wrong hit flag on ray {r}"
        if g["fh_hit"][r]:
            assert int(hit_id) == int(g["fh_id"][r]), (
                f"first_hit: wrong hit_id on ray {r} "
                "(remember: return the CLOSEST hit, not the first object that hits)"
            )
            assert np.isclose(t, g["fh_tt"][r], atol=1e-7), f"first_hit: wrong t on ray {r}"
            assert np.allclose(n, g["fh_n"][r], atol=1e-7), f"first_hit: wrong normal on ray {r}"
    # triangle-soup dispatch
    soup_objects = soup_demo_scene(_scene_variant(g))
    for r in range(len(g["sp_hit"])):
        ray = Ray(g["sp_ro"][r], g["sp_rd"][r])
        hit, hit_id, t, n = first_hit(ray, 1.0, soup_objects)
        assert bool(hit) == bool(g["sp_hit"][r]), (
            f"first_hit: wrong hit flag on soup ray {r} (is the Soup case handled?)"
        )
        if g["sp_hit"][r]:
            assert int(hit_id) == int(g["sp_id"][r]), f"first_hit: wrong hit_id on soup ray {r}"
            assert np.isclose(t, g["sp_tt"][r], atol=1e-7), f"first_hit: wrong t on soup ray {r}"


def check_reflect():
    from src.reflect import reflect
    g = golden()
    for r in range(len(g["rf_d"])):
        out = reflect(g["rf_d"][r], g["rf_n"][r])
        assert np.allclose(out, g["rf_out"][r], atol=1e-9), f"reflect: wrong result on case {r}"


def check_point_light_direction():
    from src.point_light_direction import point_light_direction
    g = golden()
    for r in range(len(g["pld_pos"])):
        d, max_t = point_light_direction(g["pld_pos"][r], g["pld_q"][r])
        assert np.allclose(d, g["pld_d"][r], atol=1e-9), f"point_light_direction: wrong direction on case {r}"
        assert np.isclose(max_t, g["pld_maxt"][r], atol=1e-9), f"point_light_direction: wrong max_t on case {r}"


def check_directional_light_direction():
    from src.directional_light_direction import directional_light_direction
    g = golden()
    for r in range(len(g["dld_dir"])):
        d, max_t = directional_light_direction(g["dld_dir"][r], g["dld_q"][r])
        assert np.allclose(d, g["dld_d"][r], atol=1e-9), f"directional_light_direction: wrong direction on case {r}"
        assert np.isinf(max_t), "directional_light_direction: max_t should be infinity"


def check_blinn_phong_shading():
    from src.first_hit import first_hit
    from src.blinn_phong_shading import blinn_phong_shading
    g = golden()
    scene_path = _scene_path(g)
    _, objs, lights = load_scene(scene_path)
    eye = g["bp_eye"]
    for r, tgt in enumerate(g["bp_targets"]):
        ray = Ray(eye.copy(), tgt - eye)
        hit, hid, t, n = first_hit(ray, 1.0, objs)
        assert hit, f"blinn_phong_shading: setup ray {r} should hit (check first_hit)"
        rgb = blinn_phong_shading(ray, hid, t, n, objs, lights)
        assert np.allclose(rgb, g["bp_rgb"][r], atol=1e-6), \
            f"blinn_phong_shading: colour differs from reference on ray {r}"


def check_raycolor():
    from src.viewing_ray import viewing_ray
    from src.raycolor import raycolor
    g = golden()
    scene_path = _scene_path(g)
    camera, objs, lights = load_scene(scene_path)
    W, H = int(g["rc_W"]), int(g["rc_H"])
    img = render_part2(camera, objs, lights, W, H, viewing_ray, raycolor)
    expected = g["rc_img"]
    if img.shape != expected.shape:
        raise AssertionError(
            "raycolor: rendered image has wrong shape"
            + _image_report("raycolor", img, expected, ASSIGN)
        )
    err = np.mean(np.abs(img.astype(np.int64) - expected.astype(np.int64)))
    if err >= 0.5:
        raise AssertionError(
            f"raycolor: rendered image too far from reference (mean abs err "
            f"{err:.3f}) — check shadows and mirror reflections in particular"
            + _image_report(
                "raycolor", img, expected, ASSIGN,
                note="try `python main.py --stages` to see which shading term "
                     "goes wrong first",
            )
        )


def get_checks():
    """Return the ordered list of checks for this assignment."""
    return [
        Check("viewing_ray", 12, check_viewing_ray, "perspective viewing ray through a pixel"),
        Check("sphere_intersect", 12, check_sphere_intersect, "ray-sphere intersection"),
        Check("plane_intersect", 8, check_plane_intersect, "ray-plane intersection"),
        Check("triangle_intersect", 12, check_triangle_intersect, "ray-triangle intersection"),
        Check("first_hit", 10, check_first_hit, "closest hit over all objects"),
        Check("reflect", 6, check_reflect, "mirror reflection of a direction"),
        Check("point_light_direction", 6, check_point_light_direction, "direction to a point light"),
        Check("directional_light_direction", 6, check_directional_light_direction, "direction to a directional light"),
        Check("blinn_phong_shading", 14, check_blinn_phong_shading, "Blinn-Phong shading with shadows"),
        Check("raycolor", 14, check_raycolor, "recursive ray colour with reflections"),
    ]
