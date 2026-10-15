"""One common-scale ground style study. Not a seamless/tile registration."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
import numpy as np
P=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;G=P/'diagnostics/art_source/a13-ground';raw=Image.open(D/'raw.png').convert('RGB');src=Image.open(G/'road-head-context-complete-tiles.png').convert('RGB');s=480/raw.width
new=raw.transform((480,256),Image.Transform.AFFINE,(1/s,0,0,0,1/s,0),resample=Image.Resampling.BICUBIC)
b=Image.new('RGB',(960,286),(50,60,50));b.paste(src,(0,30));b.paste(new,(480,30));d=ImageDraw.Draw(b);d.text((5,8),'SOURCE assembled20 placements',fill='white');d.text((485,8),'NEW whole-region single scale',fill='white');b.save(G/'style-v1-native-scale-ab.jpg')
# Representative stone-edge centerline junctions read manually, +/-3 source px.
p=[('left_cap_corner',[192,97],[690,347]),('right_cap_corner',[288,99],[1034,348]),('right_upper_turn',[332,126],[1195,454]),('right_lower_turn',[332,195],[1192,690]),('left_frame_crossing',[0,225],[0,806]),('bottom_frame_crossing',[244,256],[869,916])]
errs=[];rows=[]
for ident,q,r in p:
 mapped=np.array(r)*s;e=float(np.linalg.norm(mapped-np.array(q)));errs.append(e);rows.append({'id':ident,'source_xy':q,'candidate_raw_xy':r,'source_read_uncertainty_px':3,'candidate_read_uncertainty_raw_px':10,'mapped_source_xy':mapped.tolist(),'residual_source_px':e})
 for v,off in [(q,0),(mapped,480)]:
  x,y=v[0]+off,v[1]+30;d.ellipse((x-3,y-3,x+3,y+3),outline='cyan',width=1)
b.save(G/'style-v1-boundary-landmarks.jpg')
r={'status':'assembled region style/geometry study only; not tile/runtime accepted','raw_sha256':hashlib.sha256((D/'raw.png').read_bytes()).hexdigest(),'source_size':list(src.size),'raw_size':list(raw.size),'registration':{'kind':'single uniform width-derived scale; zero translation; no warp/axis stretch','scale':s,'translation':[0,0],'mapped_raw_height':raw.height*s,'height_difference_vs_source':raw.height*s-256},'manual_boundary_landmarks':rows,'rms_source_px':float(np.sqrt(np.mean(np.square(errs)))),'max_source_px':max(errs),'limits':['Manual centerline readings +/-3source/10raw; not exact surveyed road edges.','DiagnosticAB uses bicubic only for viewing, does not modify raw.','This generated region is not proven seamless at rectangle edges, repeated grass, or the20original tile boundaries.','Stone edging appears cleaner and somewhat more pronounced; inspect native-scale AB instead of assuming equal stone thickness.','No building, character, plant, cast or terrain runtime installed.','No tiles cropped, no semantic masks, no whole-map replacement.']};(D/'geometry-style-diagnostic.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'scale':s,'mapped_height':raw.height*s,'rms':r['rms_source_px'],'max':r['max_source_px']}))
