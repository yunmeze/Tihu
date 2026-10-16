#!/bin/bash
set -eu
HERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
export ARAP_WORK_ROOT="$(dirname "$HERE")/"
export GODOT_JOB_DIR="$HERE"
. "$HERE/../shared-runtime/godot_job_env.sh"
cd "$GODOT_JOB_DIR/project"
if [ "${1:-}" = check ]; then
 timeout 25 "$GODOT_BIN" --headless --audio-driver Dummy --path "$PWD" --script res://export_mesh.gd --check-only > "$GODOT_JOB_DIR/check.log" 2>&1
else
 timeout 75 "$GODOT_BIN" --audio-driver Dummy --path "$PWD" --rendering-method gl_compatibility --script res://export_mesh.gd > "$GODOT_JOB_DIR/render.log" 2>&1
fi
