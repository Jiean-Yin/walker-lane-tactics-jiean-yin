# MASTERCHECK

| field | value |
|---|---|
| master | lane-tactics-pitch-a8.mp4 |
| resolution | 3840×2160 |
| fps | 24 |
| pix_fmt | yuv420p |
| audio_streams | 1 |
| video_codec | h264 |
| duration_s | 152.734 |
| is_short | False |
| failures | 1 |
| verdict | **FAIL** |

## Notes

- duration: clock_check import failed ([Errno 2] No such file or directory: '<brutalist>/runtime/scripts/clock_check.py') — skipped (the toolkit checkout has no clock_check.py, so the gate's duration assertion did not run; the master is 152.7 s, the sum of the beats as built)

## Failures

- frame at t=76s: bottom-left dark=100.0% (top_pct=0.0%) — possible review-label overlay; use `art final` not `art run` to produce the master

GATE MASTER: FAIL
