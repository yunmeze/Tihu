#!/bin/sh
# Native Godot Movie Maker, 8 seconds at 30 FPS. Run from a graphical session.
# This records deterministic engine frames, not real-time GPU performance.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUTPUT=${1:-"$ROOT/captures/native_preview.avi"}
if [ "$#" -gt 0 ]; then shift; fi
mkdir -p "$(dirname -- "$OUTPUT")"
exec godot --path "$ROOT" --resolution 1152x720 \
  --write-movie "$OUTPUT" --fixed-fps 30 --quit-after 240 -- --camera=3 "$@"
