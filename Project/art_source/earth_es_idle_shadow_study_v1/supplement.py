"""Extra CPU uncertainty and conservative overlap bounds; no raster image output."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[2];H=Path(__file__).parent;D=P/'diagnostics/earth-es-idle-shadow-study-v1'
j=json.loads((H/'measurements.json').read_text());out={}
rv=json.loads((P/'assets/earth/shadows/receiver_v2/manifest.json').read_text());fg=json.loads((P/'assets/earth/shadows/fangzhang_flat_v1/manifest.json').read_text())
# Current runtime descriptor identity matches numerical study before reuse.
base=json.loads((P/'art_source/earth_shadow_next_stage_v1/measurements.json').read_text());regs={r['name']:r for r in base['records']}
for key,old in [('lingyunzi','lingyunzi0'),('first_tree','first_tree')]:
 r=rv['casters'][key];assert r['shadow']['reference_logical']==regs[old]['reference_logical'];assert r['shadow']['slope']==regs[old]['slope'];assert r['world_body_origin']==regs[old]['world_origin']
 for path,sha in r['inputs'].items():assert hashlib.sha256((P/path[6:]).read_bytes()).hexdigest()==sha
# Full static support envelopes are conservative opportunity/overlap bounds, not opacity pixels.
statics={k:np.array(Image.open(P/rv['casters'][k]['envelope']['path'][6:]))>0 for k in ['lingyunzi','first_tree']}
# Fang old gate uses a sample-sized envelope.
assert fg['shadow']['reference_logical']==regs['fangzhang0']['reference_logical']
assert fg['shadow']['slope']==regs['fangzhang0']['slope']
assert hashlib.sha256((P/fg['envelope']['texture'][6:]).read_bytes()).hexdigest()==fg['envelope']['sha256']
statics['fangzhang']=np.array(Image.open(P/fg['envelope']['texture'][6:]))>0
for d in ['e','s']:
 r=j['directions'][d];a=np.array(Image.open(P/f'assets/earth/hero/{d}_idle_v1/body.png'))[:,:,3];s=r['fixed_line']['slope'];b=r['fixed_line']['intercept'];below=[]
 for i in range(4):
  aa=a[:,512*i:512*(i+1)];y,x=np.nonzero(aa>=128);h=s*((x+.5)/4)+b-(y+.5)/4
  below.append({'source_id':r['ids'][i],'opaque_below_proxy_line_fraction':float((h<0).mean()),'opaque_min_proxy_height':float(h.min()),'opaque_max_proxy_height':float(h.max()),'note':'negative proxy height retained; no clipping or foot pinning'})
 pts=np.array([f['visible_bottom_edge_points_logical']for f in r['frames']]);mean=pts.mean(0);dx=abs(mean[1,0]-mean[0,0]);dy=abs(mean[1,1]-mean[0,1]);mag=[(dy-1.5)/(dx+2),(dy+1.5)/(dx-2)];srange=[-mag[1],-mag[0]] if s<0 else mag
 z=np.load(D/f'{d}-four-phase-envelope.npz');env=z['envelope'];off=z['offset_logical'];potential={}
 for name,other in statics.items():
  candidates=[]
  for cell in r['eligible_integer_cells_in_scan_x50_69_y28_47']:
   bx,by=((np.array(cell)*[48,32]+[-16,-64]+off-[2496,960])*2).astype(int);n=int((other[by:by+env.shape[0],bx:bx+env.shape[1]]&env).sum())
   if n:candidates.append({'cell':cell,'overlap_d2_envelope_cells':n})
  candidates.sort(key=lambda x:-x['overlap_d2_envelope_cells']);potential[name]={'eligible_positions_with_envelope_overlap':len(candidates),'largest_five':candidates[:5]}
 out[d]={'opaque_plane_diagnostics':below,'proxy_uncertainty_pair_mean_slope_interval':srange,'uncertainty_method':'adversarial +/-1 x and +/-0.75 y per visible proxy; combine pair means as systematic bounds, not confidence interval or alternate approved line','helper_absolute_slope_limit':2,'slope_uncertainty_exceeds_helper_limit':bool(max(abs(v)for v in srange)>2),'static_envelope_potential_overlap':potential}
report={'status':'CPU uncertainty bounds only; no additional permission or receiver area','runtime_static_descriptor_comparison':True,'directions':out,'receiver':j['receiver'],'limitation':'Envelope overlap is an upper-bound opportunity, not actual visible shadow pixels. Actual alpha overlaps in measurements.json use 9-tap CPU kernel. Static shaders can be gated independently off.'}
(H/'uncertainty-and-overlap.json').write_text(json.dumps(report,indent=2)+'\n');(D/'uncertainty-and-overlap.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(out,indent=2))
