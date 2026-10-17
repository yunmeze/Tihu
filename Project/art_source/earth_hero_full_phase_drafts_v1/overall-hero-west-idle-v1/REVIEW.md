# West idle first drafts

Three built-in image_gen calls, one each for SW/W/NW; no retries. Source IDs 21–24 / 25–28 / 29–32. Each has four distinct complete generated frames. Original exact movement metadata, both atlases, original composite frames, E/SE/S identity references and prompt arguments are saved alongside raw outputs.

## Visual review
- Black/charcoal modern combat uniform, gray armor, dark hair and red shoulder plates remain visibly consistent with current HD E/SE/S identity.
- SW faces lower-left, W faces left, NW shows rear three-quarter/back of head without a misplaced face. No absent frames or severe anatomy failure observed.
- Four separately generated idle poses, including visible arm/head/breathing variation; no frame duplication or mirroring was used. Exact original micro-motion fidelity still requires animation review; W phase 2 head dip may be larger than original.
- The model returned 1254² despite requesting 1024². All raw images are retained unchanged. Each source cell is 627², all uniformly resized to 364², then whole-cell translated into 512² output slots. Common scale 364/627, public density 4, logical canvas 128²/root [16,64], draw offset [-16,-64]. Direction translation constant across phases.
- Output visible heights approximate 278–291 px, comparable to existing HD sprites. Raw alpha contains isolated almost-transparent pixels away from the body; preserved, not erased. Alpha>127 was used only for bbox measurement.
- Bottom-edge registration diagnostics versus original composite: SW −12 px all phases; W +7/+3/+3/+3 px; NW −2 px all phases. Original reference includes checker shadow, so these diagnostics are not anatomical foot measurements or justification to move the logical root. This needs review during direction switching.

## Scope
Art-only next-batch candidates, NOT accepted runtime coverage. No Godot run, runtime integration, main/shadow/v6 changes or Git operations. Registration contract records raw/output sizes, regions, scale, translation, phases, hashes and diagnostic offsets. No local warping, procedural character drawing or Blender.
