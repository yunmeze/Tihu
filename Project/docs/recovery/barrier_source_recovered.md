# Reconstructed barrier cache source, not a validated release

2026-10-17 recovery after executor replacement. This is newly reconstructed source based on retained design/code context and newly read restored repository inputs. The previous candidate directories and engine evidence are missing. No claim is made that these source bytes equal the old V2 package. No engine, GPU, gameplay or visual result is accepted for this new build.

The generated fixed-blue master is already archived at art_source/earth_barrier_drafts_v1/fixed-blue-master-8x.png. Its actual SHA and all external source identities are pinned in data/art/barrier_phase_pins_recovered.json. FileAccess reads exact PNG bytes despite the art_source .gdignore; ResourceLoader/imported image processing is not used. The master remains NOT_ART_ACCEPTED; HSV offsets approximate original relative hue motion only.

## What is present

- scripts/art/barrier_phase_cache_recovered.gd: five immutable one-shot offscreen GPU passes, atomic publication, explicit numeric-validator prerequisite, old-generation retirement, cancellation and cleanup; strict current-world/15-owner matching; original draw-slot substitution.
- shaders/art/barrier_phase_recovered.gdshader: only per-pixel HSV H rotation of the generated source artwork. No procedural light-column drawing or CPU recoloring.
- Phase/owner contract and pinned actual restored inputs.

Preparation requires scene-tree attachment. request_prepare() now resolves pinned res:// paths, rather than the lost workspace-root request signature. This is an intentional recovery API change; do not blindly reuse the lost fixture. snapshot() contains entries, input image, contract and ticket. A caller must supply a genuinely validating diagnostic_validator Callable. Without it publication fails and original source drawing must remain. No always-true production validator is supplied.

Only GL Compatibility SDR2D is supported. Shader samples stored-sRGB values at exact texel centers, rotates H, preserves S/V and alpha and writes straight RGBA with blend_disabled. The consuming original CanvasItem draws once with source-over. No default blend_mix preparation, additive composition or automatic HDR conversion. Five phases use the complete 384×736 master at logical 48×92, anchor (188,540), fullcanvas top=-52 with no old atlas crop offset. The source file has no runtime integration/caller changes and no test-only ground dependency.

The deadline uses the original elapsed >10000 ms condition, via monotonic _now_msec(). The same-ticket check runs before synchronous validator, immediately afterward and immediately before publication, as well as in _process. It cannot cancel a replacement ticket. No clock reset, deadline extension or successful late publication is allowed. Expensive verification is included in this deadline. Tests may override _now_msec in a separate fixture-only subclass; the archived source always uses Time.get_ticks_msec.

The original owner mapping, layer/y/order and authoritative world.tick remain external. Cache try_draw only accepts exactly matching original owner coordinates and currently existing unique objects, exact descriptors, map tuples and original frame. It reconstructs expected origin forward as Vector2(cell.x*48,cell.y*32)+world.screen_origin(), with no epsilon/rounding. JSON numeric comparisons do not truncate or depend on int/float Dictionary equality. Absent/modified owners return false. North9 and south6 removal conditions remain original A5/ET0 authority, never cache actions.

## Integration remains pending

No recovered proxy overlay is installed. A future separately authorized candidate should call try_draw before the existing v10 registry fallback inside the original proxy _draw_frame, preserving its original traversal/activation; if false continue unchanged fallback. Initialize preparation only after attachment; cache readiness must not alter registry activation. No 15 display child sprites or per-draw material changes.

## Missing and required validation

The previous 58 original assertions and 6 deadline assertions are requirements remembered from the old test design, not restored executable tests or new passing results. Their old 58/64 counts do not certify this recovery. Rebuild them against the new request_prepare API, then independently recount the actual fixture:
- All 5 full-image CPU/GPU stored-sRGB HSV comparisons; exact alpha and RGB<=1.01/255. CPU oracle must use read-only numerical arrays, no rewritten PNGs.
- Four full candidate validation passes were required previously (20 phase records), plus 5 deep-gray and 5 pinned-real-ground source-over cases. Test-only ground must live outside this production module.
- Independent wrong linear-HSV, double-gamma, alpha-channel square, additive and genuine double-premultiplication RGB*alpha^2+background*(1-alpha) negative controls.
- Original shared 50 Hz/8 tick/80 tick ping-pong boundaries 0,7,8,31,32,39,40,47,48,71,72,79,80; both endpoint dwells 16 ticks.
- Strict 15-owner/current objects/world identity, fractional camera/no neighbor tolerance, wrong frame/top/offset/order/duplicate rejection, north9-result non-resurrection and south6 preservation. Mock result tests do not execute A5/ET0.
- Immediate cancellation, wrong hash/missing input, validator rejection/reentrant cancellation, new-generation retirement, clear and scene exit.
- Six added deadline assertions: pre-validator expiry with periodic _process disabled must avoid entering validator, fail request, preserve active; a synchronous validator advancing a fixture clock 10001 ms and returning true must execute, fail request and preserve active. No real 10-second sleep or widened deadline.

After those isolated gates: parse/integrate the optional proxy, inspect actual original-order overlap/occlusion and scaled/subpixel alpha edges, execute authorized real A5/ET0 workflows, and review all five phase colors/transparent artwork. Source archival approval is not permission to change production or claim these gates passed.
