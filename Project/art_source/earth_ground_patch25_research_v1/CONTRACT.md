# One full-patch design experiment: proposed, no generation

## Minimum actual refs
1.REF01_SOURCE_LAYOUT_480x320.png, bytecopy of exact25-owner sourcefloor assembly. Sole location/distribution reference.
2.REF02_QUIET_GRASS_384.png, bytecopy acceptedquietgrass logical1x. Material-only.
3.REF03_COMPACT_SOIL_384.png, bytecopy acceptedG1candidate logical1x. Material-only.
All actual inputs viewed. REF_MANIFEST.json freezes hashes/sizes. No buildings/native screenshot, no annotation diagram and no earlier mixed-result context image is an imagegenref. Keeping three separate images avoids a newly designed layout board and gives both actual materials the same logical scale. PROMPT_PROPOSED.txt is complete.

## Geometry / ownership scope
Sourceworld[1248,1216,1728,1536], full480x320logical,3:2. Request960x640dense2. Whole uniform window mapping only; wrongaspect is rejected or referred back, never stretched/cropped. Output is an independent full design candidate, not runtime materials,25owner replacements or a seamless384phase extension. No extraction, masks, painting or source geometry changes authorized. Later ownercut/exterior join qualification would be separate work.

## Frozen mixed-region evidence
MIXED_REGIONS_FROZEN.json enumerates ALL10mixed owners and their exact patchbounds. Each has conservative manually read cleargrass and clearsoil sample rectangles in source-local96x64coordinates. All remaining pixels are explicitly uncertain, including irregular interpenetration, isolatedflecks and diffuse edge. Rectangles are evaluation samples, not a segmentation mask or assertion of exact physical boundary.
REGION_READ_REVIEW_ONLY.png labels yellow=clearsoil,green=cleargrass,magenta=mixedowner domain. It is a source evidence diagram, NOT new boundary art or a production composite. SourceIDs412/409 have no defensible clearsoil sample in these conservative reads; their remainingtan/olive details stay uncertain. Marking everyowner with a forcedtwo-class split would invent certainty.
The majority of some mixedowners remains uncertain on purpose. Preserve gross orientation and source context; do not require individual mottled pixels to match. The ordinarypuregrass owners and13pureearthowners remain knownmacroregions, with their unchanged exactrectangles listed in../PATCH.json.

## Predeclared1x/2x visual gates
1. Full source/output side-by-side at480x320 and960x640, samefullwindow. Top/left broadbareearth remains; source's upper-rightgrassentry and largerlowergrassregion remain at their existing extents and connectedness. Interveningsoil is not converted into a grassbridge. No new road/path or artificial rectangularsoilvariants.
2. Check every cleargrass/soil sample rectangle remains its category in the new fullimage; uncertain regions are compared visually for mixededgeorientation/relativeextent, not thresholded into an exact contour. Large erosion/dilation outside those regions fails. The10sourceownerboxes are read locations only; generatededges should not reveal their grid.
3. Retain threeG3featurepatches atlocalrectangles[96,64,192,128],[0,128,96,192],[0,192,96,256]. Compare the visible upper-leftchip clusters and lower-centralshortmarks by broad location/scale/count hierarchy, not granularRGBA. No guessed interpretation as tiretrack/obstacle; no enlargedstone accessories.
4. Materials should retain approvedquietgrass andsoil finegrain scale/color family at1x. No macrograssblades or pebblefield. Stats may describe mean/contrast perclearregion, but mixedregion means must not replace artjudgment or be recolored to pass.
5. Inspect all fourpatchboundaries: enteringgrass/soil must matchsourcegeometry. Do not demand oppositeedgesrepeat, and do not claim phasecontinuity with either384tile. Adjacentoutsideworld remains untreated and may require separatetransitiondesign.
6. Accept/reject wholecandidate. No alpha/keyedmask blending, warpedboundary, program-paintednewart, recolor, hiddenoldparts or posthoc silhouettecut to rescue a failedlayout. Failure stays archived, no automaticretry.

## Current status
Only exact source/material copies, source annotations and writtencontract exist. No generation, newboundary synthesis, productionedit, Godot or Git. Root reviews thiscontract,actualrefs andprompt before any call.
