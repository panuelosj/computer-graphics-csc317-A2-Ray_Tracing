# Public test data: A2-Ray_Tracing

These are the exact arrays the public unit checks compare your
functions against — the inputs they feed in and the outputs they
expect back. Everything here is generated from
`a2_golden.npz`; nothing here is secret, and you
are meant to look at it when a check fails.

* `arrays/<name>.txt` — the values, in readable form.
* `images/<name>.png` — the same array as a viewable image, for
  the entries that are pictures.

To load an array yourself:

```python
import numpy as np
g = np.load('tests/golden/a2_golden.npz')
print(g.files)          # every available name
img = g['<name>']       # one array
```

Regenerate this folder with `python export_expected.py <assignment>` from the repository root.

| entry | what it is | values | picture |
|---|---|---|---|
| `bp_eye` | shape (3,), dtype float64, range [0, 5] | [bp_eye.txt](arrays/bp_eye.txt) | — |
| `bp_rgb` | shape (6, 3), dtype float64, range [0.02, 1.85282] | [bp_rgb.txt](arrays/bp_rgb.txt) | — |
| `bp_targets` | shape (6, 3), dtype float64, range [-1.4875, 1.9125] | [bp_targets.txt](arrays/bp_targets.txt) | — |
| `cam_d` | shape (), dtype float64, range [3, 3] | [cam_d.txt](arrays/cam_d.txt) | — |
| `cam_eye` | shape (3,), dtype float64, range [0, 5] | [cam_eye.txt](arrays/cam_eye.txt) | — |
| `cam_height` | shape (), dtype float64, range [1, 1] | [cam_height.txt](arrays/cam_height.txt) | — |
| `cam_u` | shape (3,), dtype float64, range [0, 1] | [cam_u.txt](arrays/cam_u.txt) | — |
| `cam_v` | shape (3,), dtype float64, range [0, 1] | [cam_v.txt](arrays/cam_v.txt) | — |
| `cam_w` | shape (3,), dtype float64, range [0, 1] | [cam_w.txt](arrays/cam_w.txt) | — |
| `cam_width` | shape (), dtype float64, range [1.77778, 1.77778] | [cam_width.txt](arrays/cam_width.txt) | — |
| `dld_d` | shape (2, 3), dtype float64, range [-0.436436, 1] | [dld_d.txt](arrays/dld_d.txt) | — |
| `dld_dir` | shape (2, 3), dtype float64, range [-2, 1] | [dld_dir.txt](arrays/dld_dir.txt) | — |
| `dld_maxt` | shape (2,), dtype float64 | [dld_maxt.txt](arrays/dld_maxt.txt) | — |
| `dld_q` | shape (2, 3), dtype float64, range [-2, 3] | [dld_q.txt](arrays/dld_q.txt) | — |
| `fh_hit` | shape (6,), dtype bool | [fh_hit.txt](arrays/fh_hit.txt) | — |
| `fh_id` | shape (6,), dtype int64, range [-1, 2] | [fh_id.txt](arrays/fh_id.txt) | — |
| `fh_n` | shape (6, 3), dtype float64, range [0, 1] | [fh_n.txt](arrays/fh_n.txt) | — |
| `fh_rd` | shape (6, 3), dtype float64, range [-5, 3] | [fh_rd.txt](arrays/fh_rd.txt) | — |
| `fh_ro` | shape (6, 3), dtype float64, range [-3, 10] | [fh_ro.txt](arrays/fh_ro.txt) | — |
| `fh_tt` | shape (6,), dtype float64, range [1, 5] | [fh_tt.txt](arrays/fh_tt.txt) | — |
| `pl_hit` | shape (4,), dtype bool | [pl_hit.txt](arrays/pl_hit.txt) | — |
| `pl_min_t` | shape (4,), dtype float64, range [0.5, 0.5] | [pl_min_t.txt](arrays/pl_min_t.txt) | — |
| `pl_n` | shape (4, 3), dtype float64, range [0, 1] | [pl_n.txt](arrays/pl_n.txt) | — |
| `pl_normal` | shape (3,), dtype float64, range [0, 1] | [pl_normal.txt](arrays/pl_normal.txt) | — |
| `pl_point` | shape (3,), dtype float64, range [-1, 0] | [pl_point.txt](arrays/pl_point.txt) | — |
| `pl_rd` | shape (4, 3), dtype float64, range [-1, 1] | [pl_rd.txt](arrays/pl_rd.txt) | — |
| `pl_ro` | shape (4, 3), dtype float64, range [0, 5] | [pl_ro.txt](arrays/pl_ro.txt) | — |
| `pl_tt` | shape (4,), dtype float64, range [3, 3] | [pl_tt.txt](arrays/pl_tt.txt) | — |
| `pld_d` | shape (2, 3), dtype float64, range [-4, 10] | [pld_d.txt](arrays/pld_d.txt) | — |
| `pld_maxt` | shape (2,), dtype float64, range [1, 1] | [pld_maxt.txt](arrays/pld_maxt.txt) | — |
| `pld_pos` | shape (2, 3), dtype float64, range [-3, 10] | [pld_pos.txt](arrays/pld_pos.txt) | — |
| `pld_q` | shape (2, 3), dtype float64, range [0, 1] | [pld_q.txt](arrays/pld_q.txt) | — |
| `rc_H` | shape (), dtype int64, range [18, 18] | [rc_H.txt](arrays/rc_H.txt) | — |
| `rc_W` | shape (), dtype int64, range [32, 32] | [rc_W.txt](arrays/rc_W.txt) | — |
| `rc_img` | shape (18, 32, 3), dtype uint8, range [0, 255] | [rc_img.txt](arrays/rc_img.txt) | [view](images/rc_img.png) |
| `rf_d` | shape (3, 3), dtype float64, range [-1, 1] | [rf_d.txt](arrays/rf_d.txt) | — |
| `rf_n` | shape (3, 3), dtype float64, range [0, 1] | [rf_n.txt](arrays/rf_n.txt) | — |
| `rf_out` | shape (3, 3), dtype float64, range [-0.6, 1] | [rf_out.txt](arrays/rf_out.txt) | — |
| `scene_name` | shape (), dtype <U21 | [scene_name.txt](arrays/scene_name.txt) | — |
| `scene_variant` | shape (), dtype <U6 | [scene_variant.txt](arrays/scene_variant.txt) | — |
| `sp_hit` | shape (3,), dtype bool | [sp_hit.txt](arrays/sp_hit.txt) | — |
| `sp_id` | shape (3,), dtype int64, range [-1, 1] | [sp_id.txt](arrays/sp_id.txt) | — |
| `sp_n` | shape (3, 3), dtype float64, range [0, 1] | [sp_n.txt](arrays/sp_n.txt) | — |
| `sp_rd` | shape (3, 3), dtype float64, range [-1, 0] | [sp_rd.txt](arrays/sp_rd.txt) | — |
| `sp_ro` | shape (3, 3), dtype float64, range [-0.5, 5] | [sp_ro.txt](arrays/sp_ro.txt) | — |
| `sp_tt` | shape (3,), dtype float64, range [5, 5] | [sp_tt.txt](arrays/sp_tt.txt) | — |
| `sph_center` | shape (3,), dtype float64, range [0, 0] | [sph_center.txt](arrays/sph_center.txt) | — |
| `sph_hit` | shape (4,), dtype bool | [sph_hit.txt](arrays/sph_hit.txt) | — |
| `sph_min_t` | shape (4,), dtype float64, range [0, 1] | [sph_min_t.txt](arrays/sph_min_t.txt) | — |
| `sph_n` | shape (4, 3), dtype float64, range [0, 1] | [sph_n.txt](arrays/sph_n.txt) | — |
| `sph_radius` | shape (), dtype float64, range [1, 1] | [sph_radius.txt](arrays/sph_radius.txt) | — |
| `sph_rd` | shape (4, 3), dtype float64, range [-1, 1] | [sph_rd.txt](arrays/sph_rd.txt) | — |
| `sph_ro` | shape (4, 3), dtype float64, range [0, 5] | [sph_ro.txt](arrays/sph_ro.txt) | — |
| `sph_tt` | shape (4,), dtype float64, range [1, 4] | [sph_tt.txt](arrays/sph_tt.txt) | — |
| `tri_a` | shape (3,), dtype float64, range [-1, 0] | [tri_a.txt](arrays/tri_a.txt) | — |
| `tri_b` | shape (3,), dtype float64, range [-1, 1] | [tri_b.txt](arrays/tri_b.txt) | — |
| `tri_c` | shape (3,), dtype float64, range [0, 1] | [tri_c.txt](arrays/tri_c.txt) | — |
| `tri_hit` | shape (4,), dtype bool | [tri_hit.txt](arrays/tri_hit.txt) | — |
| `tri_min_t` | shape (4,), dtype float64, range [1, 1] | [tri_min_t.txt](arrays/tri_min_t.txt) | — |
| `tri_n` | shape (4, 3), dtype float64, range [0, 1] | [tri_n.txt](arrays/tri_n.txt) | — |
| `tri_rd` | shape (4, 3), dtype float64, range [-1, 1] | [tri_rd.txt](arrays/tri_rd.txt) | — |
| `tri_ro` | shape (4, 3), dtype float64, range [0, 5] | [tri_ro.txt](arrays/tri_ro.txt) | — |
| `tri_tt` | shape (4,), dtype float64, range [5, 5] | [tri_tt.txt](arrays/tri_tt.txt) | — |
| `vr_H` | shape (), dtype int64, range [9, 9] | [vr_H.txt](arrays/vr_H.txt) | — |
| `vr_W` | shape (), dtype int64, range [16, 16] | [vr_W.txt](arrays/vr_W.txt) | — |
| `vr_dir` | shape (5, 3), dtype float64, range [-3, 0.833333] | [vr_dir.txt](arrays/vr_dir.txt) | — |
| `vr_origin` | shape (5, 3), dtype float64, range [0, 5] | [vr_origin.txt](arrays/vr_origin.txt) | — |
| `vr_pix` | shape (5, 2), dtype int64, range [0, 15] | [vr_pix.txt](arrays/vr_pix.txt) | — |
