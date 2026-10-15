"""Source-layout/material audit only; no raw modifications or production writes."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage

HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
RAW=HERE/"raw.png"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected="a44d861c4485cb8596fb42681441675d1b9cefb3d8c48261113325c14492ae2f"
assert sha(RAW)==expected
im=Image.open(RAW);assert im.size==(1536,1024)
source=[(382,834),(768,578),(960,582),(1048,636),(1048,774),(872,896)]
observed=[(385,833),(771,576),(959,576),(1050,637),(1050,769),(874,896)]
samples=[{"source_center_raw":list(s),"v4_center_raw_approx":list(g),"delta_logical":[(g[0]-s[0])/2,(g[1]-s[1])/2],"distance_logical":math.hypot(g[0]-s[0],g[1]-s[1])/2} for s,g in zip(source,observed)]
protected=np.asarray(Image.open(P/"art_source/earth_ground_plate_grass_edit_v2/inputs/protected-road-mask.png"))>0
grass=~ndimage.binary_dilation(protected,iterations=16)
def stats(path):
    a=np.asarray(Image.open(path).convert("RGB")).astype(float);luma=a[:,:,0]*.2126+a[:,:,1]*.7152+a[:,:,2]*.0722
    h=grass[:,1:]&grass[:,:-1];v=grass[1:,:]&grass[:-1,:]
    g=np.concatenate((np.abs(np.diff(luma,axis=1))[h],np.abs(np.diff(luma,axis=0))[v]))
    return {"mean_srgb":a[grass].mean(axis=0).tolist(),"mean_display_luma_neighbor_difference":float(g.mean())}
diagnostic=im.convert("RGB").copy();draw=ImageDraw.Draw(diagnostic);draw.line(source,fill="magenta",width=2)
for i,(x,y) in enumerate(observed):draw.ellipse((x-3,y-3,x+3,y+3),outline="cyan",width=1);draw.text((x+7,y-15),str(i+1),fill="cyan")
diagnostic.save(HERE/"source-layout-review-diagnostic.png")
report={"status":"Parent viewed raw and native joint2x and approved v4 as the independent Earth sample candidate. Warm highlight/lighting review remains; not global final-art approval.",
        "raw":{"sha256":expected,"size":[1536,1024],"mode":im.mode,"world_bounds_xyxy":[2496,960,3264,1472],"effective_texels_per_logical":[2,2],"modified_after_generation":False},
        "generation_input_check":"Only clean source semantic geometry, same-geometry actual actor-scale reference and concept-only material/scale panel; no v2/v3 grass supplied to imagegen.",
        "source_layout":{"samples":samples,"maximum_center_distance_logical":max(s["distance_logical"] for s in samples),"source_manual_read_uncertainty_logical":3,"v4_manual_read_uncertainty_raw":3,
                         "edge_case":"Third/top-right cap-center read is approximately(959,576) versus source(960,582), 3.041 logical pixels. Given original±3 logical and current±1.5 logical reading uncertainty, this is a boundary-precision caveat, not a proven hard failure or proof of exact alignment.",
                         "parent_disposition":"Approved as bounded independent-sample candidate after native joint2x review with this uncertainty disclosed; do not warp or regenerate for this read.",
                         "shape":"Same capped diagonal route, bottom opening and approximately186-logical-pixel grass gap before left stairs. No new connector, step, planter or obstacle. New top curb is somewhat more horizontal; edge thickness and exact outer silhouette are finite-precision visual reads."},
        "material_review":{"grass":"Object scale clearly changed: dense large curled leaf rosettes and deep tuft-pits are largely replaced by much finer short grass/granular ground texture and broad flat variation. Still warm/yellow-highlighted; needs joint actual1x/2x visual judgment, no independent color reroll.",
                           "pavement":"Entire neutral engineered slab surface, seams and small flush drain details were regenerated, as explicitly authorized. No pixel-identity claim to v2/v3 and no restoration/compositing.",
                           "content":"No person, person shadow, building, tree, flowerbed, new raised planter or large object cast observed."},
        "grass_descriptive_metrics":{"v2":stats(P/"art_source/earth_ground_plate_grass_edit_v2/raw.png"),"v3":stats(P/"art_source/earth_ground_plate_scale_edit_v3/raw.png"),"v4":stats(RAW),"limitation":"Display-space descriptive proxies only. Cannot establish blade length, perceptual quietness, physical lighting or final acceptance."},
        "runtime_boundary":"Parent approved separate ground_plate_v4 direct64-owner export and designated runtime owner switching the independent Earth sample default to v4; keep P original-source fallback and retain old v2 files. No automatic further generation."}
old_path=HERE/"review.json"
if old_path.exists():
    old=json.loads(old_path.read_text())
    if "native_evidence" in old:report["native_evidence"]=old["native_evidence"]
(HERE/"review.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
assert sha(RAW)==expected
print(json.dumps({"max_center_delta_logical":report["source_layout"]["maximum_center_distance_logical"],"grass":report["grass_descriptive_metrics"]}))
