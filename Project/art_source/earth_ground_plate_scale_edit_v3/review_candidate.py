"""Read-only v2/v3 material/layout review. Does not repair or install either raw."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = Path(__file__).resolve().parent
P = HERE.parents[1]
OLD = P / "art_source/earth_ground_plate_grass_edit_v2/raw.png"
NEW = HERE / "raw.png"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
old_sha, new_sha = sha(OLD), sha(NEW)
assert new_sha == "230071981a79e850b8b0dd99aa0c4fa8e69408770cde2620aa451bc609be87d3"
old, new = Image.open(OLD), Image.open(NEW)
assert old.size == new.size == (1536, 1024)
a, b = [np.asarray(im.convert("RGB")).astype(np.int16) for im in (old, new)]
protected = np.asarray(Image.open(P / "art_source/earth_ground_plate_grass_edit_v2/inputs/protected-road-mask.png")) > 0
core = ndimage.binary_erosion(protected, iterations=16)
grass = ~ndimage.binary_dilation(protected, iterations=16)
diff = np.abs(a-b)
changed = np.any(diff != 0, axis=2)

def difference(mask):
    return {"pixels": int(mask.sum()), "changed_pixels": int(changed[mask].sum()),
            "changed_fraction": float(changed[mask].mean()),
            "mean_absolute_channel_difference_0_255": float(diff[mask].mean()),
            "max_channel_difference": int(diff[mask].max()),
            "p95_max_channel_difference": float(np.percentile(diff.max(axis=2)[mask], 95))}

def grass_stats(arr):
    f=arr.astype(float)
    luma=f[:,:,0]*.2126+f[:,:,1]*.7152+f[:,:,2]*.0722
    h=grass[:,1:] & grass[:,:-1];v=grass[1:,:] & grass[:-1,:]
    gradients=np.concatenate((np.abs(np.diff(luma,axis=1))[h],np.abs(np.diff(luma,axis=0))[v]))
    return {"mean_srgb": f[grass].mean(axis=0).tolist(),
            "mean_display_luma_neighbor_difference": float(gradients.mean()),
            "limitation": "Descriptive display-space proxy; cannot establish blade scale or perceptual acceptance."}

source=[(382,834),(768,578),(960,582),(1048,636),(1048,774),(872,896)]
observed=[(386,832),(771,576),(963,579),(1052,639),(1051,772),(875,897)]
layout={"source_center_read_budget_logical":3,"v3_manual_read_uncertainty_raw":3,
        "samples":[{"source_center_raw":list(s),"v3_center_raw_approx":list(g),
                    "delta_logical":[(g[0]-s[0])/2,(g[1]-s[1])/2],
                    "distance_logical":math.hypot(g[0]-s[0],g[1]-s[1])/2}
                   for s,g in zip(source,observed)],
        "maximum_center_distance_logical":max(math.hypot(g[0]-s[0],g[1]-s[1])/2 for s,g in zip(source,observed)),
        "shape_read":"Same capped diagonal lower-field path, top short cap, upper-right chamfer, right edge, lower-right diagonal and bottom opening. No connector toward left stairs; about186 logical pixels of grass interval remains.",
        "precision_limit":"Approximate correspondence within finite original manual source-read budget. Not exact curb outer-edge/thickness registration, and not visual acceptance."}
diagnostic=new.convert("RGB").copy();draw=ImageDraw.Draw(diagnostic);draw.line(source,fill="magenta",width=2)
for i,(x,y) in enumerate(observed):
    draw.ellipse((x-3,y-3,x+3,y+3),outline="cyan",width=1);draw.text((x+7,y-15),str(i+1),fill="cyan")
diagnostic.save(HERE/"source-layout-review-diagnostic.png")
report={"status":"Parent inspected raw and rejected replacement of production v2: short-cut lawn scale not achieved. Joint same-camera comparison requested as evidence only.",
        "raw":{"v2_sha256":old_sha,"v3_sha256":new_sha,"size":[1536,1024],"mode":new.mode,"effective_texels_per_logical":[2,2],"modified_after_generation":False},
        "protected_pixels":difference(protected),"road_core_eroded_16_raw_pixels":difference(core),
        "grass_descriptive_metrics":{"v2":grass_stats(a),"v3":grass_stats(b)},
        "layout":layout,
        "manual_visual_review":{"grass":"Some dark hollows and mound contrast are reduced, but curled wire-like grass and identifiable leafy clusters still occupy most of the field. The requested fine short-cut lawn scale has not been achieved; lower contrast alone is insufficient.",
                                "pavement":"Surface material has been re-rendered; capped path layout remains visually close. Pixel differences are disclosed separately from geometric and style judgment.",
                                "content":"No person, figure-shaped shadow, building, tree, new planter or new connector observed in raw.",
                                "decision":"Preserve v2 production unchanged. No automatic fourth generation or pixel restoration/compositing."},
        "next_direction":"Prepare a new-generation input using clean original source semantic geometry and concept fine-grass/human scale references, excluding v2/v3 grass as primary imagery. Repainting road material is allowed in that proposed input; generation still needs separate approval."}
if (HERE/"review.json").exists():
    previous=json.loads((HERE/"review.json").read_text())
    if "native_evidence" in previous:report["native_evidence"]=previous["native_evidence"]
(HERE/"review.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
meta=json.loads((HERE/"generation.json").read_text());meta["status"]=report["status"];meta["review"]="review.json";(HERE/"generation.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
assert (old_sha,new_sha)==(sha(OLD),sha(NEW))
print(json.dumps({"road_core":report["road_core_eroded_16_raw_pixels"],"protected":report["protected_pixels"],"grass":report["grass_descriptive_metrics"],"max_source_center_delta_logical":layout["maximum_center_distance_logical"]},ensure_ascii=False))
