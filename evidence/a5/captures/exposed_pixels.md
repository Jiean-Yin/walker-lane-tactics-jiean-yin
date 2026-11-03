# Controlled-value captures: exposed_amount (2026-11-02T22:57:39)

Godot 4.7.2-stable (official), renderer gl_compatibility, window (1280.0, 720.0). Captured with the course's capture() in `godot/debug/capture_exposed.gd`:
the driver is paused, the value set, and the frame read after `frame_post_draw`. Game state: PLAN_MOVE, turn 1.

| Point | Value | Predicted (CHANGE-BRIEF §3) | Measured RGB | Difference per channel |
|---|---|---|---|---|
| P1 head (192, 581) | 0.0 | (224, 174, 117) | (224, 174, 117) | (+0, +0, +0) |
| P2 base disc (202, 634) | 0.0 | (90, 58, 34) | (90, 58, 34) | (+0, +0, +0) |
| P1 head (192, 581) | 0.5 | (224, 137, 96) | (224, 137, 96) | (+0, +0, +0) |
| P2 base disc (202, 634) | 0.5 | (137, 62, 42) | (137, 62, 42) | (+0, +0, +0) |
| P1 head (192, 581) | 1.0 | (224, 101, 76) | (224, 100, 75) | (+0, -1, -1) |
| P2 base disc (202, 634) | 1.0 | (184, 66, 51) | (184, 66, 50) | (+0, +0, -1) |
| P1 head (192, 581) | 2.0 | (224, 27, 34) if not clamped | (224, 27, 34) | (+0, +0, +0) |
| P2 base disc (202, 634) | 2.0 | - | (255, 73, 67) | - |

After the 2.0 capture the material reads back 2.0; the driver resumed afterwards.
