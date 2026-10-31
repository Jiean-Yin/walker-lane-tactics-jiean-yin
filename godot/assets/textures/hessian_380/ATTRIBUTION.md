# Hessian 380 — texture credits and provenance

| | |
|---|---|
| Asset | **Hessian 380** (fine burlap), Poly Haven |
| Source page | https://polyhaven.com/a/hessian_380 |
| Authors and roles | colormass (photography), Rico Cilliers (processing), as listed by Poly Haven |
| Published | 2025-09-05 (Poly Haven API) |
| Real-world size of one tile | about 274 × 274 mm (Poly Haven API `dimensions`) |
| Licence | **CC0** ("effectively Public Domain"; no credit required): https://polyhaven.com/license |
| Licence and credits checked | 2026-10-31, by Claude Code for Jiean Yin, from the licence page and `https://api.polyhaven.com/info/hessian_380` |
| Downloaded | 2026-10-31, from `https://dl.polyhaven.org/file/ph-assets/Textures/<format>/1k/hessian_380/`, 1K resolution |

The course asks for provenance even though the licence does not ask for credit.

## Files

| File | Role | What its numbers mean | Format | Bytes | SHA-256 |
|---|---|---|---|---|---|
| `hessian_380_diff_1k.jpg` | colour (albedo) | sRGB-encoded colour of the cloth | JPEG, 1024 × 1024, 8-bit RGB | 944,914 | `5727302df3a9c845e6320ff186ac13fc7d0f1ffcd6fda71667e808e09379fe6f` |
| `hessian_380_rough_1k.png` | data: roughness | 0 = glossy, 1 = fully rough, stored linearly | PNG, 1024 × 1024, 16-bit greyscale | 1,990,268 | `33908953756e87f9cd9d5a632dc3fecce7f410b4a983f04825e003325de6920e` |
| `hessian_380_nor_gl_1k.png` | data: tangent-space normal map, **OpenGL convention (`_nor_gl`, green = up)**, the one Godot expects and the one the game uses | each channel maps −1…1 to 0…1; 0.5, 0.5, 1 means "no tilt" | PNG, 1024 × 1024, 16-bit RGB | 5,718,543 | `c7d36fe0e0beeebcbbb6b8a55e62b73cef56c890e683bb295fcf9e3495aaf3a3` |
| `hessian_380_nor_dx_1k.png` | data: the same normal map in the **DirectX convention (`_nor_dx`, green flipped)**, used **only** to calibrate `godot/tests/normal_map_check.gd`; no material binds it | as above, green inverted | PNG, 1024 × 1024, 16-bit RGB | 5,717,470 | `0ed7d737bcdc6b7c33df01eba168a35963e9b4a16316a19b28d918fd853d0e53` |

The files are kept exactly as downloaded (the assignment forbids changing source texture files). The JPEG's EXIF block carries a path from Poly Haven's own processing tool; it is their metadata, not this project's.
