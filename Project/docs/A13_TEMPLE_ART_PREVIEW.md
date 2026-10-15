# A13 temple working art preview

Open `res://scenes/art_preview.tscn` and press T to toggle the original/main-temple candidate. F5 shows the temple stair with the original SE hero; existing idle body/shadow controls remain available. The default R1 and natural-opening R6 scenes are unchanged.

The selected `assets/scifi/environment/a13_temple_v2/registration.json` uses 27 original-size transparent cutouts and three explicit empty owners. All 30 original Building keys are suppressed together, including empty owners. Only those keys are replaced. Source flags, layer, sort Y and stable source order remain unchanged. Each crop uses its compensated world origin and the same whole-building scale. Nearest filtering is intentional; body linear filtering is separate.

Native source/technical-v1/technical-v2 comparisons covered 66,34; 66,35; 66,36; 65,35; 73,35; 73,36; 74,36; 74,37. The original A* movement actually traversed all eight targets in 896 updates, including the 16-cell route around the building. At stationary comparison points the original South frame17 was explicitly held for a consistent diagnostic pose. This is not a claim of all-phase depth validation.

Technical-v1 is rejected: treating narrow stair risers as foreground cut the hero's shins. Technical-v2 includes the source-supported continuous stair treads and narrow risers in the support layer. The remaining right-boot outer edge occlusion at 66,36 is from the actual stair cheek, and is retained as a documented design difference. The right stair sample poses do not exhibit the v1 shin cuts.

Full raw versus split native nearest raster comparison, with hero/scene hidden and labels excluded, differed at 64 pixels by at most 2 RGB levels for each partition. This is not bit-exact GPU parity; no visible partition gaps were observed. Offline inverse raw assembly is separately byte-exact.

No new building cast shadow has been accepted or added. The body shadow remains a flat-ground-only pilot; this building preview does not establish platform receivers. Roof/rail/stair proportions differ from the source. Original source art remains available with T.
