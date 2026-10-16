#!/bin/bash
set -eu
HERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
export ARAP_WORK_ROOT="$(dirname "$HERE")/"
export GODOT_JOB_DIR="$HERE/native-preview"
. "$HERE/../shared-runtime/godot_job_env.sh"
PROJECT="$HERE/project"
if [ "${1:-}" = check ]; then
 timeout 25 "$GODOT_BIN" --headless --audio-driver Dummy --path "$PROJECT" --script res://preview_loop.gd --check-only > "$GODOT_JOB_DIR/check.log" 2>&1
else
 timeout 25 "$GODOT_BIN" --audio-driver Dummy --path "$PROJECT" --rendering-method gl_compatibility --script res://preview_loop.gd -- --hold > "$GODOT_JOB_DIR/preview.log" 2>&1
fi
