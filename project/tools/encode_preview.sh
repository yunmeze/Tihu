#!/bin/sh
# Convert the engine-authored movie to a browser-friendly MP4. H.264/YUV420
# compression is lossy; there is no intentional grading or composited imagery.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
INPUT=${1:-"$ROOT/captures/native_preview.avi"}
OUTPUT=${2:-"$ROOT/captures/native_preview.mp4"}
exec ffmpeg -n -i "$INPUT" -an -c:v libx264 -preset slow -crf 17 \
  -pix_fmt yuv420p -movflags +faststart "$OUTPUT"
