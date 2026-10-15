# Selected SE idle + walk preview

`res://scenes/art_preview.tscn` now combines selected idle13–16 and walk51–56. It remains optional; R1 source gameplay and R6 natural new-game entry are unchanged. Walk/run in other directions and combat are not replaced.

The walk atlas in `assets/scifi/hero/se_walk_v3/body.png` is byte-identical to registered v3 SHA256 `7c386900fe579018ef38cf00c7e160622abebef476f3ccebd9c6fd94923bcf38`. All ten frames use128×128 regions and actor-origin offset(-16,-64). New body filtering is linear; source and map art remain nearest. Body pixels are never changed by the shadow helper.

## Controls
- P: advance the ten selected idle/walk phases.
- M: reset to the explicitly bounded art-demo start(59,40) and follow original A* to(61,42), then idle. This is a preview route, not a gameplay teleport command.
- C: selected idle12tick cycle. Walk uses the existing reference-adapted7tick schedule; original EXE timing parity is not claimed.
- B: complete original body/head, which disables the new shadow. S: new shadow on/off. L: new-body filter comparison.
- F1/F4: prior road-edge/interior fixed views; F2/F3: tree-back/front. F5: temple stair with source body. Position presets cancel an active route.
- T: original/selected temple cutouts. No new building cast shadow or platform receiver has been accepted.

## One continuous receiver

All ten selected frames use the same explicit fixed receiver line: reference(40,86) in image coordinates, slope0, cast(148/279,-111/279), opacity0.30, blur0.9. The value86 is the actual native-reviewed working value, not the theoretical envelope minimax86.5. It does not force each swinging boot to contact the ground. The earlier R5 two-sole idle projection is retained as historical evidence and generic API, but this combined viewer intentionally uses a single plane across movement changes.

Native comparisons covered both87.5 and86 across ten poses and identical one-cell movement updates. The selected86 kept the idle shadow more gathered near the feet without an obvious gait shadow jump. The longer original-flags route59,40→60,41→61,42 was advanced64 updates and also run continuously. Its sampled updates1/8/15/22/29/36/43/50/57 show51–56 then51–53, followed by idle; frame56→51 occurs during actual translation. Fixed phase51 and54 tree-back/front checks retained original ordering. No second checker shadow was present in new-body mode.

All three route cells have original[0,0,0,0]; the route passes near a painted road edge and ends near foreground foliage. This is bounded flat-ground evidence, not proof for buildings, stairs, all ground surfaces or all camera positions. Small soft separation near phase51 remains a2D approximation rather than a physically reconstructed contact state. v3 thigh/armor and foot-pose residuals remain documented in art_source. No further body correction was made to fit the shadow.

Selected normal-path assets, manifests, helper/shader and art_preview form the dependency closure. Temporary diagnostic viewers, test scripts and screenshots are not required for users to open it.
