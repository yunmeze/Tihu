# Source only for a project-owned diagnostic job. This does not grant the Godot lease.
# Set GODOT_JOB_DIR to an absolute workspace diagnostic directory before sourcing.
case "${GODOT_JOB_DIR:-}" in /*) ;; *) echo 'GODOT_JOB_DIR must be an absolute owned diagnostic directory' >&2; return 2;; esac
# Preserve an already available local X11 authority path before changing HOME.
if [ -z "${XAUTHORITY:-}" ] && [ -n "${HOME:-}" ] && [ -f "$HOME/.Xauthority" ]; then
  XAUTHORITY="$HOME/.Xauthority"; export XAUTHORITY
fi
mkdir -p "$GODOT_JOB_DIR/home" "$GODOT_JOB_DIR/xdg/config" "$GODOT_JOB_DIR/xdg/cache" "$GODOT_JOB_DIR/xdg/data" || return 2
HOME="$GODOT_JOB_DIR/home"
XDG_CONFIG_HOME="$GODOT_JOB_DIR/xdg/config"
XDG_CACHE_HOME="$GODOT_JOB_DIR/xdg/cache"
XDG_DATA_HOME="$GODOT_JOB_DIR/xdg/data"
GODOT_BIN="${GODOT_BIN:-godot}"
export HOME XDG_CONFIG_HOME XDG_CACHE_HOME XDG_DATA_HOME GODOT_BIN
command -v "$GODOT_BIN" >/dev/null 2>&1 || { echo 'Configured Godot binary not found' >&2; return 2; }
