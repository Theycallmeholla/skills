# Output Pipeline Reference

## The Pipeline

```
walkthrough.webm   (Playwright recording)
       ↓ ffmpeg
walkthrough.mp4    (H.264, universally playable)
       ↓ ffmpeg extract frames
frames/            (PNG sequence)
       ↓ gifski
walkthrough.gif    (high-quality animated GIF)
```

---

## convert.sh

This is the full conversion script to include in every generated project:

```bash
#!/usr/bin/env bash
set -e

OUTPUT_DIR="./output"
FRAMES_DIR="$OUTPUT_DIR/frames"
INPUT="$OUTPUT_DIR/walkthrough.webm"
MP4_OUT="$OUTPUT_DIR/walkthrough.mp4"
GIF_OUT="$OUTPUT_DIR/walkthrough.gif"

# Width for GIF output. 800px is a good default; reduce if file size is a concern
GIF_WIDTH=800
GIF_FPS=15

# --- Preflight checks ---
if [ ! -f "$INPUT" ]; then
  echo "❌ Input not found: $INPUT"
  echo "   Run the walkthrough first (npx tsx src/walkthrough.ts) and make sure it saved the .webm."
  exit 1
fi
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "❌ ffmpeg not found. Install it first:"
  echo "   macOS:  brew install ffmpeg"
  echo "   Ubuntu: sudo apt install ffmpeg"
  exit 1
fi
if ! command -v gifski >/dev/null 2>&1; then
  echo "❌ gifski not found. Install it first:"
  echo "   macOS:  brew install gifski"
  echo "   Other:  cargo install gifski  (or see https://gif.ski/)"
  echo "   Or use the ffmpeg-only palette fallback documented in output-pipeline.md."
  exit 1
fi

echo "🎬 Converting webm → mp4..."
ffmpeg -i "$INPUT" \
  -c:v libx264 \
  -preset slow \
  -crf 22 \
  -movflags +faststart \
  -pix_fmt yuv420p \
  -an \
  "$MP4_OUT" -y

echo "🖼  Extracting frames for GIF..."
mkdir -p "$FRAMES_DIR"
# Clear stale frames from previous (possibly longer) runs — leftovers would get
# baked into the end of the new GIF.
rm -f "$FRAMES_DIR"/frame*.png
ffmpeg -i "$MP4_OUT" \
  -vf "fps=$GIF_FPS,scale=$GIF_WIDTH:-1:flags=lanczos" \
  "$FRAMES_DIR/frame%04d.png" -y

echo "🎨 Building GIF with gifski..."
gifski \
  --fps $GIF_FPS \
  --width $GIF_WIDTH \
  --quality 85 \
  --output "$GIF_OUT" \
  "$FRAMES_DIR"/frame*.png

# --- Verification ---
echo ""
echo "✅ Done!"
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$MP4_OUT" 2>/dev/null || echo "unknown")
FRAME_COUNT=$(ls "$FRAMES_DIR"/frame*.png 2>/dev/null | wc -l | tr -d ' ')
echo "   MP4 duration: ${DURATION}s"
echo "   Frames extracted: $FRAME_COUNT"
echo "   MP4: $MP4_OUT"
echo "   GIF: $GIF_OUT"
du -sh "$MP4_OUT" "$GIF_OUT"
```

---

## Installing Dependencies

### macOS
```bash
brew install ffmpeg gifski
```

### Ubuntu/Debian
```bash
sudo apt install ffmpeg
cargo install gifski   # or: snap install gifski
```

### Windows
- ffmpeg: https://ffmpeg.org/download.html (add to PATH)
- gifski: https://gif.ski/ (download binary, add to PATH)

---

## GIF Tuning

### File size too large?

GIFs get large fast. Levers to pull, in order of impact:

| Lever | Change | Impact |
|---|---|---|
| Width | `GIF_WIDTH=600` instead of 800 | High |
| FPS | `GIF_FPS=10` instead of 15 | High |
| Quality | `--quality 70` instead of 85 | Medium |
| Duration | Trim the walkthrough | Very high |

### Trimming the webm before converting

If you only want a portion of the walkthrough:
```bash
# Trim: start at 5s, duration 20s
ffmpeg -i walkthrough.webm -ss 5 -t 20 -c copy walkthrough-trimmed.webm
```
Then substitute `walkthrough-trimmed.webm` as input in convert.sh.

### Looping behavior

GIFs loop by default. gifski's `--repeat` value is the number of **additional** repeats after the
first play (`-1` disables looping, `0` loops forever):
```bash
gifski --repeat 0 ...    # loop forever (default)
gifski --repeat -1 ...   # play once, no loop
gifski --repeat 3 ...    # play 4 times total (1 play + 3 repeats)
```

---

## Fallback: gifski not available

If gifski isn't installed, use ffmpeg's built-in GIF palette method (lower quality but no extra install):

```bash
# Generate palette
ffmpeg -i walkthrough.mp4 \
  -vf "fps=15,scale=800:-1:flags=lanczos,palettegen=stats_mode=diff" \
  palette.png -y

# Build GIF using palette
ffmpeg -i walkthrough.mp4 -i palette.png \
  -filter_complex "fps=15,scale=800:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer" \
  walkthrough.gif -y
```

Quality is noticeably worse than gifski, but it works anywhere ffmpeg is installed.

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `walkthrough.webm` is 0 bytes | `stagehand.close()` not called before script exits | Make sure close() is in a `finally` block |
| GIF is too large (>10MB) | Walkthrough too long or too wide | Trim to under 45s; reduce `GIF_WIDTH` to 640 |
| Colors look washed out in GIF | Default dithering | Use gifski instead of ffmpeg palette method |
| MP4 won't play in browser | Wrong pixel format | Add `-pix_fmt yuv420p` to ffmpeg command (already in script above) |
| `gifski: command not found` | Not installed | See installation section above, or use ffmpeg fallback |
| Frames are blurry | Scale filter not using lanczos | Use `flags=lanczos` in ffmpeg scale filter |
| Recording is blank/black | Headless mode + GPU issue | Add `--disable-gpu` to browser launch args |

---

## File Size Expectations

Rough benchmarks at 800px wide, 15fps, gifski quality 85:

| Duration | MP4 size | GIF size |
|---|---|---|
| 15s | ~1MB | ~4MB |
| 30s | ~2MB | ~8MB |
| 60s | ~4MB | ~18MB |
| 90s | ~6MB | ~28MB |

GIFs above ~10MB are awkward to embed in docs/Notion. For anything over 45s, recommend MP4 only and tell the user to host it with a video embed.
