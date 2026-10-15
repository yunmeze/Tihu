# Golden tree v1: one generated candidate

One built-in imagegen call, original seven-piece source composite as sole geometry input. Raw/prompt/input hashes are frozen. Parent inspected the grey preview and accepted the natural golden leaf/bark working style for registration; native tree and cast are not accepted yet.

Root-preserving single uniform scale0.2472072097078169, translation in original source canvas[-4.109190434492817,-2.581624682367874]. Raw wood contact[498,1224] maps to source[119,300]/world[2761,1090]. Manual uncertainty ±8raw/±4source. Six crown branch landmarks RMS2.77/max4.49source px, not a pixel-identical silhouette claim. Taller/thicker leaf clusters and cleaned bark are explicit design differences.

Root/crown natural-scale comparison is ignored diagnostics/art_source/a13-first-tree/candidate-v1-native-scale-ab.jpg. The source large right checker cast is not tree geometry and has not been replicated. New raw contains no ground apron or cast. Highlights are cleaner and brighter gold than the old pixel texture; no neon or mechanical parts added.

Requested padding was not fully achieved: strong alpha>32 is inset, but alpha1 reaches top/left/bottom. Every raw pixel is preserved; no threshold/keying/alpha cleanup. If a future import needs larger bounds, only exact transparent padding with compensation may be considered, never clipping.

## Seven-owner optional diagnostic
`technical_v1/registration.json` SHA95ae55adad59accdd09dd8118afdf9e51e43016f45eed79d26acec4a5429bd2c.
The raw is split by actual original world x-column boundaries, 48px each, with one common scale+translation. Owner292 remains layer1/y34; other six remain layer1/y37. All original source keys are suppressed for this instance only. Do not trim new leaves to low-resolution source alpha. Do not move whole tree to root order.

Owner298 formerly contained only baked cast. New corresponding column has124 alpha-positive pixels with maximumalpha1 and no alpha>32. They are retained unchanged; this is not a new cast shadow and not grounds to generate a replacement piece.

Independent reverse assembly of all RGBA bytes, original key metadata, unique coverage and sampling bounds pass. Each crop has compensated world_top_left. First diagnostic should use nearest/no mipmaps and compare full raw vs split at identical registration, then normal-depth original A* probes57,32 (behind all),57,35 (ahead of trunk but behind outer crown slices),59,38 (ahead of all), starting61,39. Full route and NPC/flag evidence in frozen source contract. No forced move if original path rejects. Old cast disappears with the original seven pieces; a new single ground cast is a later independent gate.

Reproduce: measure_candidate.py, partition_candidate.py, verify_partition.py in this directory. No runtime/default integration or original file changes are included.
