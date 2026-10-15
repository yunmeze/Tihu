# Two A13 NPCs: optional art preview

The optional `scenes/art_preview.tscn` viewer adds J (both selected NPCs new/source),
K (only their two ground shadows on/off), and F7 (camera/actor view near both NPCs).
The default source scene and natural-new-game scene are unchanged. This stage does
not replace dialogue, clicking, collision, scripts, or NPCs in gameplay.

Only A13 record 0, 方丈 at (64,37), appearance21/direction2, and record1, 凌云子
at (62,36), appearance9/direction1 are eligible. Same names or appearances elsewhere
are not replacement keys. Both resources and receiver configurations must prepare
successfully before either original checker-bearing NPC sprite is suppressed.
A failure returns both complete NPC sprites to source and removes both new shadows.

The shared preview clock advances at 50 updates/second; each four-phase loop uses
17 updates/phase. Source IDs261–264 share Fangzhang's one rectangle; IDs113–116 use
Lingyunzi's four rectangles. Candidate bodies use linear filtering and the unchanged
128×160 registration with draw offset(-32,-104). Source textures remain nearest.
The source stable layer/y/order is preserved by splitting the object draw pass at
both exact NPC entries and the hero, then interleaving the bodies in that order.

Each NPC has one alpha-projected ground shadow, after floor and before all objects.
Fangzhang uses fixed frame-local reference(44,118), slope12/17. Lingyunzi uses
(56,125), slope0. Both use cast(148/279,-111/279), opacity0.30, blur0.9. These are
bounded 2D receiver proxies; no phase refit, body recoloring, extra contact ellipse,
source checker overlay, or platform/elevation solution is implied.

## Native acceptance evidence

The isolated GPU comparison used actual window and viewport1024×768, one screen
pixel per canvas pixel. It captured updates0,17,34,51,68,85,102,119,136, including
two complete loops and the final3→0 boundary. The fixed NPC region is byte-identical
at corresponding phases separated by68 updates and at0/136. Fixed-phase new shadow
on/off and source comparisons showed single soft shadows on the visible grass in
front of the original temple. Both NPCs retained their normal front/back ordering
against a source hero at four explicitly positioned technical fixtures. Those
positions are not a walking-route test. No stair/platform receiver was accepted.

Parent and NPC-owner visual review accepted this bounded result. Fangzhang's
staggered sole depths and Lingyunzi's richer gold ornaments remain design evidence,
not a claim of anatomical or physical reconstruction. The old pose-only images
were captured at a scaled1082×812 viewport; the shadow-stage images correct that
sampling limitation and do not relabel the old captures.

## Promoted closure

The ordinary viewer starts at fixed1024×768 for reproducible1× inspection. F8 only
hides/shows its instruction label. The promoted checks cover both full phase maps,
four actor/NPC order cases, shadow-only disable, source restore, one missing body
forcing both NPCs back to source, restored resources, and missing manifest refusal.
The isolated cold project was updated incrementally with normal assets/scripts,
re-imported and tested; this is not a fresh empty-cache archive claim. R1 movement
and the R6 complete opening candidate regression were rerun successfully. The
parent can independently repeat a clean Git-only archive after saving this stage.

Resource preparation validates the declared expected SHA, dimensions, source keys,
frame mapping and receiver parameters. It does not recompute the PNG byte hash at
every runtime load; exact source-to-promoted PNG bytes were independently checked
at promotion. Imported/exported texture loading is not described as a cryptographic
content verification. Malformed metadata types are rejected before consumption.
