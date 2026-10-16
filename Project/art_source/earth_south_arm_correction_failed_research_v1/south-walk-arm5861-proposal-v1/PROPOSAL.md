# 58/61 translation-only intermediate-phase diagnostic

Status: read-only proposal; no solve, no texture deformation, no engine run. The first visible-region masks are frozen for inspection but FAIL the shared-vertex constraint preflight. Do not feed them to ARAP as final constraints.

## Intended change
Use the existing boot-corrected six-frame result. Only58/61 are candidates;57/59/60/62 remain byte-identical. Keep head, chest, shoulders and straps, belt/legs at existing positions. No rotation of fists or guessed wrist/elbow/shoulder points. Preserve the modern armor design and disclose perspective differences.

The source visible skin-patch centers are explicit center-matching hypotheses, not anatomical truth (±2 logical-pixel uncertainty). Proposed exact translations in logical pixels:
58 L(−1.40,+1.62), R(−1.86,−1.36)
61 L(+0.23,−1.36), R(−0.31,+1.26)
Multiply by4 for the output-HD mesh. Current mapping/targets and raw hashes are in CONSTRAINTS.json. These translations are not evidence of acceptance. The source cuff is a separate uncertain clothing proxy, not bare hand or wrist.

Visible distal gauntlet plus skin should move together with unchanged orientation and near-rigid shape; only visible connecting dark cloth should absorb ARAP strain. The blue/amber overlay gives a human-reviewable proposed split. It does not label a hidden joint. Full-alpha support remains present; shoulders, chest and legs must not become accidental transition material.

## Expected phase-distribution hypothesis
With neighbors frozen, source-center translation would change y deltas:
57→58: AI L+1.53/R−0.27 becomes L+3.15/R−1.63 (source+2.5/−2.5)
58→59: AI L+6.21/R−6.84 becomes L+4.59/R−5.48 (source+4/−4)
60→61: AI L−0.18/R+1.89 becomes L−1.54/R+3.15 (source−2.5/+2.5)
61→62: AI L−4.86/R+5.85 becomes L−3.50/R+4.59 (source−4/+3.5)
62→57 stays unchanged. These are arithmetic predictions from driving centers, not independent proof that motion looks better. The short trial would compare the same six-frame140ms loop before/after with only58/61 substituted.

## Frozen first-mask warning
The amber patch covers visible gauntlets/fists; blue lies below the fixed shoulder caps. But hand-drawn polygon edges clip a few real boundary pixels and many low-alpha ones. On the full-alpha pixel-cell mesh, there are284(58) and291(61) vertices incident to both proposed rigid and proposed fixed cells. A translated rigid point cannot also remain fixed. Adjacent outside pixels include high alpha, so this cannot be waived as transparent background.

Per-side outside pixels neighboring rigid cells (8-neighborhood), alpha≥1 / ≥64 / ≥128:
58L146/8/6;58R126/30/29;61L166/39/32;61R115/22/22.
These are mask preflight findings, not deformation failures. The mask files and overlay are retained exactly. They are NOT solver-ready and no solve is permitted.

## Required mask correction before a solve could be approved
1. Extend proposed rigid material support to include the entire visible gauntlet/fist boundary, including the real antialiased fringe, without taking adjacent torso material.
2. At each genuine arm–cloth attachment, reserve a visible cloth transition band; retain the shoulder/strap band fixed.
3. For weak-alpha outer support, an explicitly separate bounded fringe transition may be necessary. Do not discard it, invent new texture, couple across alpha=0 pixels, or silently unfix chest material. Any required high-alpha chest/strap release is a blocker and must be reported.
4. Recheck every shared vertex: no fixed+rigid conflict, no left+right rigid conflict, complete source alpha support, and no protected-region membership. Pixel counts alone do not prove this.
5. Only after the masks are reviewed should constrained ARAP with step/backtracking be considered. Preserve zero orientation flips and zero global boundary crossings/contacts. Stop on failure; do not relax gates or let arm edits leak to the successful leg solve.

## Independent review criteria
- Compare actual visible forearm material edges, cuff-to-skin presentation and full-loop swing distribution against both neighboring phases. Source sleeves and AI metal are different surfaces, so state uncertainty instead of claiming exact silhouette equality.
- Compare held-out plate edge lengths/widths and fist outline against the pretrial AI frame. Constancy within an explicitly rigid patch is an implementation invariant, not independent source-motion acceptance; inspect unforced transition/adjacent plate boundaries for shear.
- Leg/head/chest/shoulder/strap projected positions unchanged; no deformation-induced seam or upper-body jump.
- Full-alpha geometry gates and true1x/2x dark/gray/light sampling checks.
- Center residual is a driver check only. No claim to recover hidden palm, fist orientation, anatomy, or original full-body pose.

Next action requires review of the masks and the acknowledged preflight blocker. No new six-frame solve or GPU request is pending.
