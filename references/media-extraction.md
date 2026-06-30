# Media Extraction Reference

How to pull teachable content out of a lecture recording or audio file.
Assumes **ffmpeg / ffprobe** is installed (e.g. `D:\ffmpeg\bin` on PATH, or replace
`ffmpeg` / `ffprobe` with the full path throughout).

---

## 1. Probe duration and streams

Always inspect the file first so you know what you are dealing with.

```bat
ffprobe -v error -show_entries format=duration,size -show_streams ^
    -of default=noprint_wrappers=1 in.mp4
```

Key fields to note:
- `duration` — total seconds; divide by 60 for a time estimate.
- `codec_type=video` / `codec_type=audio` — confirms which streams exist.
- `avg_frame_rate` — needed if you want a fixed-interval fallback (see below).

---

## 2. Extract slide frames by scene change

A scene-change filter captures the moment the teacher switches slides without
dumping every video frame.

```bat
ffmpeg -i in.mp4 ^
    -vf "select='gt(scene,0.05)',showinfo" ^
    -vsync vfr ^
    frames\slide_%04d.png
```

**Tuning the scene threshold (`0.03`–`0.1`)**

| Threshold | Effect |
|-----------|--------|
| `0.03` | Very sensitive — captures subtle pointer movements and partial transitions; produces more frames, more duplicates. |
| `0.05` | Good default for slide-based lectures with clear transitions. |
| `0.10` | Only hard cuts; may miss gradual fade-in slides or annotation reveals. |

Start at `0.05`, then inspect the `frames\` folder. If two consecutive slides share
nearly identical content, raise to `0.07`. If a slide appears to be skipped, lower
to `0.03`.

**Fixed-interval fallback**

When scene detection misses incremental bullet reveals, supplement with one frame
every 15 seconds:

```bat
ffmpeg -i in.mp4 -vf fps=1/15 frames\interval_%04d.png
```

Combine both passes, then deduplicate (next section).

**Deduplicating near-identical frames**

After extraction, use the `mpdecimate` filter or a simple perceptual-hash script.
Quick perceptual-hash approach (Python, requires `Pillow` and `imagehash`):

```python
import imagehash
from PIL import Image
from pathlib import Path

seen, keep = set(), []
for p in sorted(Path("frames").glob("*.png")):
    h = imagehash.phash(Image.open(p))
    # Hamming distance < 8 = near-duplicate
    if all(abs(h - s) >= 8 for s in seen):
        seen.add(h)
        keep.append(p)
    else:
        p.unlink()          # delete duplicate
print(f"Kept {len(keep)} unique frames.")
```

---

## 3. Extract audio for ASR (16 kHz mono WAV)

Whisper and most ASR engines work best on 16 kHz mono WAV.

```bat
ffmpeg -i in.mp4 -vn -ac 1 -ar 16000 -f wav audio.wav
```

Flag breakdown:
- `-vn` — drop video stream.
- `-ac 1` — mix to mono.
- `-ar 16000` — resample to 16 000 Hz.
- `-f wav` — force WAV container (avoids codec guessing).

---

## 4. Transcribe with faster-whisper

### Install

```bat
pip install faster-whisper
```

`faster-whisper` is backed by `ctranslate2` for efficient CPU and GPU inference;
it does **not** require PyTorch.

### Python snippet

```python
from faster_whisper import WhisperModel

# Model sizes: tiny / base / small / medium / large-v3
# device: "cpu" or "cuda"  |  compute_type: "int8" (CPU), "float16" (GPU)
model = WhisperModel("medium", device="cpu", compute_type="int8")

segments, info = model.transcribe(
    "audio.wav",
    language="zh",       # skip auto-detect for Chinese lectures
    vad_filter=True,     # voice-activity filter: skips silence
)

with open("transcript.txt", "w", encoding="utf-8") as f:
    for seg in segments:
        line = f"[{seg.start:.1f}-{seg.end:.1f}] {seg.text.strip()}"
        print(line)
        f.write(line + "\n")
```

**Model-size tradeoff**

| Model | Disk | Speed (CPU) | Quality |
|-------|------|-------------|---------|
| `small` | ~460 MB | Fast | Good for clear audio |
| `medium` | ~1.4 GB | Moderate | Recommended default |
| `large-v3` | ~3 GB | Slow | Best for noisy / accented audio |

Switch to GPU with `device="cuda"` and `compute_type="float16"` for a 5–10x
speed-up on an NVIDIA card.

**First run**: the model weights are downloaded automatically to
`~/.cache/huggingface/hub` (or `%USERPROFILE%\.cache\huggingface\hub` on Windows).
Subsequent runs are fully offline.

---

## 5. Windows / long-video notes

- Long recordings (2+ hours) can take **10–30 minutes** for scene extraction and
  **20–60 minutes** for `medium` transcription on CPU. Run both in the background:

  ```bat
  start "ffmpeg-scenes" ffmpeg -i in.mp4 -vf "select='gt(scene,0.05)',showinfo" -vsync vfr frames\slide_%%04d.png
  start "whisper-transcribe" python transcribe.py
  ```

- If `ffmpeg` is not on PATH, prefix with the full path, e.g.:

  ```bat
  D:\ffmpeg\bin\ffmpeg.exe -i in.mp4 ...
  ```

- Keep source video and output frames on the **same drive** to avoid slow cross-drive
  copies; extraction is I/O-bound.

- Windows Defender may flag the first `faster-whisper` download; allow it or
  pre-download on a trusted machine and copy the cache folder.
