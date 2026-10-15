"""Clean source-semantic generation proposal. Never reads v2/v3 generated grass."""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
P=HERE.parents[1]
INPUTS=HERE/"inputs"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def item(p):return {"path":str(p.relative_to(P)),"sha256":sha(p),"bytes":p.stat().st_size}
def main():
    INPUTS.mkdir(exist_ok=True)
    source=P/"art_source/earth_ground_plate_source_v1/material-layout-board.png"
    concept=P/"art_source/earth_base_style_concept_v1/concept.png"
    contract=P/"art_source/earth_ground_plate_source_v1/source-layout-contract.json"
    alpha=P/"art_source/earth_ground_plate_source_v1/source-alpha-2x.png"
    actor=INPUTS/"source-layout-with-scale-actor-2x.png"
    if not actor.exists():shutil.copyfile("/workspace/shared/earth-ground-v3/layout-and-actor-2x.png",actor)
    assert Image.open(source).size==(768,512)
    plain=Image.open(source).convert("RGB").resize((1536,1024),Image.Resampling.NEAREST)
    plain.save(INPUTS/"source-layout-empty-2x.png")
    acted=Image.open(actor).convert("RGB");assert acted.size==plain.size
    different=np.any(np.asarray(acted)!=np.asarray(plain),axis=2)
    yy,xx=np.where(different)
    assert not different[:448].any() and not different[704:].any()
    assert not different[:,:832].any() and not different[:,1088:].any()
    c=Image.open(concept).convert("RGB")
    crops=[("concept-fine-lawn.png",(350,470,505,590)),("concept-quiet-green.png",(240,230,315,300)),("concept-person-scale.png",(705,510,785,640))]
    for name,box in crops:c.crop(box).save(INPUTS/name)
    board=Image.new("RGB",(410,190),(29,32,34));d=ImageDraw.Draw(board)
    d.text((10,8),"CONCEPT ONLY - native pixels, person about111px",fill="white")
    board.paste(c.crop(crops[2][1]),(10,35));board.paste(c.crop(crops[0][1]),(105,35));board.paste(c.crop(crops[1][1]),(285,35))
    d.text((105,165),"Fine lawn grain",fill="white");d.text((285,115),"Green tone",fill="white")
    board.save(INPUTS/"concept-only-material-and-scale.png")
    report={"schema":"earth-clean-ground-generation-input-plan-v1","status":"input proposal only; no generation authorized or performed",
            "source_geometry":item(source),"source_contract":item(contract),"source_alpha":item(alpha),"concept":item(concept),
            "world_bounds_xyxy":[2496,960,3264,1472],"logical_size":[768,512],"required_actual_generated_size":[1536,1024],
            "empty_layout":{**item(INPUTS/"source-layout-empty-2x.png"),"derivation":"Nearest2x semantic labels, not art upscaling and not proof of generated texel density."},
            "actor_reference":{**item(actor),"origin":"Designated runtime owner rendered same source semantic board and actual hero only, original cell61,39 / SE13 / true2x GPU output. No world objects or new shadow.","changed_pixels_vs_empty":int(different.sum()),"difference_bounds_xyxy":[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],"main_body_height_actual_px":144,"role":"Human scale only; final output contains no person or person shadow."},
            "concept_crops":[{**item(INPUTS/name),"crop_xyxy":list(box)} for name,box in crops],
            "concept_board":item(INPUTS/"concept-only-material-and-scale.png"),
            "allowed_generation_inputs":["inputs/source-layout-empty-2x.png","inputs/source-layout-with-scale-actor-2x.png","inputs/concept-only-material-and-scale.png"],
            "forbidden_visual_inputs":["Any v1/v2/v3 generated grass, full frame or patch","Previous concept/current comparison boards that include generated grass","Full original source floor texture with repeating grass","Full concept scene or full runtime scene with buildings, trees and shadows"],
            "semantic_palette":{"green":[67,117,72],"gray":[170,170,166],"magenta":[220,85,186]},
            "semantic_palette_meaning":"Grass region / paved region / uncertain curb review band. Magenta is a geometry label, not a physical magenta curb, raised rail, collision or decorative stripe.",
            "geometry_limits":{"source_manual_center_read_budget_logical":3,"curb_band_logical_width":7,"note":"Existing source-only per-frame semantic interpretation has finite-precision edge notches; do not turn those tiny review-mask steps into ornamental geometry. Same original six centerpoints and capped route remain the geometric audit authority; exact outer boundary is not claimed."},
            "material_change_scope":"Generate an entire new continuous plate. Repaint BOTH lawn and pavement material from scratch while preserving source path layout. No pixel-identity requirement to any rejected plate; no pavement restoration/compositing.",
            "production":"Current v2 registration and all64 owners remain unchanged. Any future output needs independent raw/layout and actual1x/2x joint review before new registration."}
    (HERE/"input-plan.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"actor_only_changed_pixels":int(different.sum()),"no_generated_grass_inputs":True}))
if __name__=="__main__":main()
