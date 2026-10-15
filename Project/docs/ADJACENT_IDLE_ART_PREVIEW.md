# E / SE / S adjacent idle preview

The optional `scenes/art_preview.tscn` includes E9–12, SE13–16 and S17–20 idle, plus E45–50, SE51–56 and S57–62 walking. Keys1/2/3 select E/SE/S; C cycles the selected idle four phases at the existing reference-adapted12tick cadence. P advances selected poses. M runs the current direction's verified two-cell walking route and returns to its own idle. Running and other directions are not replaced. The initial idle-only acceptance below preceded the E/S walk extension described in the final section.

Each direction retains its source-guided registration,128px frame and(-16,-64) actor-origin offset. E and S ordinary resource manifests accompany their unchanged PNGs. New bodies use linear sampling; source art remains nearest. E side-on narrowness and S front-on width are directional differences; local E white waist plate and S symmetric/bright chest armor differences remain accepted visual residuals.

All selected idle and SE walking frames use the same fixed ground reference(40,86), slope0, cast(148/279,-111/279), opacity.30 and blur.9. The body shader does not alter the generated artwork. A single new shadow replaces the source body/checker combination only in selected-body mode; B restores original body/head and disables the new shadow.

Native acceptance covered twelve source/new static phases, twenty sequential native samples of E→SE→S→SE→E, and a continuous240update loop. The same twenty states were checked with the shared ground shadow. E9 and S17 were also observed behind and in front of the source tree at(61,49)/(61,53). The observed root and shadow transitions had no obvious jump or second checker; this does not establish physically exact foot contact on every surface. No platform/stair receiver, extra directions, equipment layer or gameplay integration is implied. R1 and R6 remain source-character entry points.

## E/S walk extension (2026-10-15)
The optional viewer now includes E45–50 and S57–62 alongside SE51–56. M selects the current E/SE/S direction and its verified two-cell original A* route: E60,41→62,41; SE59,40→61,42; S60,41→60,43. Each takes64 movement updates and returns to that direction's idle. There is no run or other-direction replacement.

All three groups use the same fixed horizontal receiver y86, cast(148/279,-111/279), one alpha shadow before objects. E/S each passed180-update idle→two loops→idle pose review, actual64-update movement and fixed45/57 tree back61,49/front61,53. S59/62 passing-foot amplitude remains stronger; E side armor and S brighter/wider chest remain design residuals. Only tested flat-road/ground contexts are accepted; road-edge stone does not establish a platform receiver.

A missing/malformed walk texture disables the entire selected direction's new idle+walk body and its shadow together, falling back to original body/head. B restores original visuals; S disables only the candidate hero shadow. Default source gameplay and natural new-game entry are unchanged. Diagnostic scenes/screenshots are not runtime dependencies.
