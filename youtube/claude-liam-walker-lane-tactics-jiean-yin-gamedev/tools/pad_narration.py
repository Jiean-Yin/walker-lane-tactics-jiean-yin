"""Make frame-exact beat audio: lead silence + Kokoro narration + tail silence (PCM WAV).

- Gameplay beats: padded to the clip's exact frame count, so the compositor never retimes the action.
- B01: 0.8 s lead silence (hesitant-writer head start). BOUT: 1.0 s silent tail (OUTRO-LOCK).
The narration itself is not altered (no speed change); the original mp3 stays in mp3/.
Usage (reel folder): python tools/pad_narration.py
"""
import json
import math
import subprocess
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
FPS = 30
LEAD = {"B01": 0.8, "B03": 0.3, "B09": 0.3, "B11": 0.15, "B13": 0.25}
TAIL = {"BOUT": 1.0}


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def main():
    p = REEL / "beat_sheet.json"
    sheet = json.loads(p.read_text(encoding="utf-8"))
    for b in sheet["beats"]:
        bid = b["beat_id"]
        frames = (b.get("shot") or {}).get("frames")
        if bid not in LEAD and bid not in TAIL and not frames:
            continue
        if b.get("kind") == "source_report":
            continue
        src = REEL / f"mp3/beat-{bid}.mp3"
        voice = probe(src)
        lead = LEAD.get(bid, 0.0)
        if frames:
            n = frames[1] - frames[0]
        else:
            n = math.ceil((lead + voice + TAIL.get(bid, 0.0)) * FPS - 1e-8)
        total = n / FPS
        if lead + voice > total + 1e-6:
            raise SystemExit(f"{bid}: narration {voice:.2f}s + lead {lead}s exceeds {total:.3f}s")
        out = REEL / f"mp3/beat-{bid}-timed.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af",
                        f"adelay={int(round(lead * 1000))}:all=1,apad", "-t", f"{total:.6f}", "-ar", "48000",
                        "-ac", "2", "-c:a", "pcm_s16le", str(out)], check=True)
        b["voice_duration_s"] = round(voice, 3)
        b["lead_silence_s"] = lead
        b["audio_file"] = f"mp3/beat-{bid}-timed.wav"
        b["actual_duration_s"] = total
        b["clip_frames"] = n
        b["duration_note"] = (f"voice {voice:.3f}s + lead {lead}s, padded with silence to {n} frames = {n}/{FPS} s"
                              + (" (clip length; no retiming)" if frames else ""))
        print(bid, b["duration_note"])
    p.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
