"""Make frame-exact beat audio: lead silence + Kokoro narration + tail silence (PCM WAV, 48 kHz stereo).

- Footage/engine beats (shot.segments): padded to the clip's exact frame count, so nothing is retimed.
- Still beats and Remotion beats: lead + voice (+ tail) rounded up to whole frames.
- B01: 0.8 s lead (hesitant-writer head start). BOUT: 1.0 s silent tail (OUTRO-LOCK).
The narration itself is not altered (no speed change); the original mp3 stays in mp3/.
Usage (reel folder): python tools/pad_narration.py
"""
import json
import math
import subprocess
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
FPS = 30
LEAD = {"B01": 0.8}
TAIL = {"BOUT": 1.0, "B02": 0.6, "B13": 0.8, "BCRD": 0.6}


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def seg_frames(seg):
    if "a" in seg:
        return seg["b"] - seg["a"]
    return round((seg["t1"] - seg["t0"]) * FPS)


def main():
    p = REEL / "beat_sheet.json"
    sheet = json.loads(p.read_text(encoding="utf-8"))
    for b in sheet["beats"]:
        bid = b["beat_id"]
        segs = b["shot"].get("segments")
        src = REEL / f"mp3/beat-{bid}.mp3"
        voice = probe(src)
        lead = b.get("lead_silence_s", LEAD.get(bid, 0.0))
        tail = b.get("tail_silence_s", TAIL.get(bid, 0.0))
        if segs:
            n = sum(seg_frames(s) for s in segs)
        else:
            n = math.ceil((lead + voice + tail) * FPS - 1e-8)
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
                              + (" (clip length; no retiming)" if segs else ""))
        if b["shot"].get("remotion"):
            b["shot"]["remotion"]["props"].setdefault("durationSeconds", total)
            if b["shot"]["remotion"]["pattern"] in ("GodotDevWorkbench",):
                b["shot"]["remotion"]["props"]["durationSeconds"] = total
        print(bid, b["duration_note"])
    p.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
