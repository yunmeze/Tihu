from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];D=R/'diagnostics/earth_e_49_cloth_patch_v1';D.mkdir(parents=True,exist_ok=True)
old=Image.open(R/'art_source/earth_hero_e_49_control_v2/raw.png').convert('RGBA');raw=Image.open(P/'raw.png').convert('RGBA');mask=Image.open(P/'replacement-mask.png').convert('L');a=np.array(old);m=np.array(mask);s=200/raw.width
# Single isotropic scale; output height174.944, unused fraction transparent. No anisotropic resize.
patch=raw.transform((200,175),Image.Transform.AFFINE,(1/s,0,0,0,1/s,0),resample=Image.Resampling.BICUBIC)
patch.save(P/'patch-mapped-to-source-crop.png');layer=Image.new('RGBA',old.size);layer.paste(patch,(300,425))
# Feather only inside approved support, max2 raw px; premultiplied RGBA composition.
inner=np.array(mask.filter(ImageFilter.MinFilter(5)));weight=np.where(m>0,np.where(inner>0,1.,.5),0.)[:,:,None]
b=np.array(layer).astype(float);af=a[:,:,3:4]/255;bf=b[:,:,3:4]/255;outa=af*(1-weight)+bf*weight;rgb=np.where(outa>0,(a[:,:,:3]*af*(1-weight)+b[:,:,:3]*bf*weight)/np.maximum(outa,1e-9),0)
out=np.concatenate([rgb,outa*255],axis=2).round().clip(0,255).astype('uint8');out[m==0]=a[m==0];im=Image.fromarray(out);im.save(P/'old49-with-masked-cloth-patch-COMPOSITE.png');Image.fromarray((weight[:,:,0]*255).astype('uint8')).save(P/'actual-inner-feather-mask.png')
prov=np.zeros_like(a);prov[m==0]=[40,180,90,255];prov[m>0]=[230,60,200,255];Image.fromarray(prov).save(D/'pixel-provenance-green-reused-pink-patch.png')
# Lower module crop support: explicit top y476, no anatomy paint.
lower=im.copy();la=np.array(lower);la[:476,:,3]=0;lower=Image.fromarray(la);lower.save(P/'lower49-module-UNCERTIFIED.png')
sheet=Image.open(R/'art_source/earth_e_layered_parts_v1/raw.png').convert('RGBA');core=sheet.crop((0,0,512,512));arm=sheet.crop((1024,0,1536,512))
# Conservative previously reviewed exterior mask only.
bg=Image.open(R/'art_source/earth_e_parts_density_review_v1/background-only-proposed-keep-mask.png');
for tile,bb in [(core,(0,0,512,512)),(arm,(1024,0,1536,512))]:
 v=np.array(tile);v[np.array(bg.crop(bb))==0,3]=0;tile.paste(Image.fromarray(v))
def mapped(im,s,t):
 k=4*s;return im.transform((512,512),Image.Transform.AFFINE,(1/k,0,-t[0]/s,0,1/k,-t[1]/s),resample=Image.Resampling.BICUBIC)
cs=33/387;ct=[39-292*cs,16-29*cs];ars=.079;art=[36.5-226.5*ars,32-137.5*ars]
L=mapped(lower,.1028549998260168,[-1.4220149316246022,-.25108997251065546]);C=mapped(core,cs,ct);A=mapped(arm,ars,art)
# Exact disjoint core front/back mask for existing shoulder only, no new pixels.
fm=Image.new('L',core.size);fd=ImageDraw.Draw(fm);fd.polygon([(130,180),(220,170),(255,210),(225,285),(150,310),(125,260)],fill=255)
ca=np.array(core);fr=ca.copy();bk=ca.copy();fr[np.array(fm)==0,3]=0;bk[np.array(fm)>0,3]=0;fm.save(P/'core-shoulder-front-mask.png');mapped_mask=fm.transform((512,512),Image.Transform.AFFINE,(1/(4*cs),0,-ct[0]/cs,0,1/(4*cs),-ct[1]/cs),resample=Image.Resampling.NEAREST); cc=np.array(C); cb=cc.copy(); cf=cc.copy(); cb[np.array(mapped_mask)>0,3]=0; cf[np.array(mapped_mask)==0,3]=0; B=Image.fromarray(cb); F=Image.fromarray(cf)
assembled=Image.new('RGBA',(512,512));
for v in [L,B,A,F]:assembled.alpha_composite(v)
assembled.save(P/'assembled49-HD4-RESEARCH.png')
src=Image.open(R/'diagnostics/earth_e_source_shadow_index_audit_v1/49-index18-excluded-NOT-SEMANTICALLY-CERTIFIED.png').convert('RGBA').resize((512,512),Image.Resampling.NEAREST)
for name,col in [('gray',(128,128,128,255)),('light',(235,235,235,255)),('dark',(20,22,26,255))]:
 board=Image.new('RGBA',(1536,512),col);board.alpha_composite(src,(0,0));board.alpha_composite(assembled,(512,0));board.alpha_composite(mapped(im,.1028549998260168,[-1.4220149316246022,-.25108997251065546]),(1024,0));board.save(D/f'source-assembled-patched-old-{name}.png')
 board=Image.new('RGBA',(800,350),col);board.alpha_composite(old.crop((300,425,500,600)).resize((400,350)),(0,0));board.alpha_composite(im.crop((300,425,500,600)).resize((400,350)),(400,0));board.save(D/f'cloth-before-after-{name}.png')
proof={'raw_sha256':hashlib.sha256((P/'raw.png').read_bytes()).hexdigest(),'raw_size':raw.size,'uniform_raw_to_crop_scale':s,'mapped_content_height':raw.height*s,'aspect_rounding_gap_crop_px':175-raw.height*s,'outside_mask_changed_rgba_pixels':int(np.any(out[m==0]!=a[m==0],axis=1).sum()),'below_y578_changed_rgba_pixels':int(np.any(out[579:]!=a[579:],axis=2).sum()),'assembly':{'core_scale':cs,'core_translation':ct,'arm_family_scale':ars,'arm49_translation':art,'lower_scale':.1028549998260168,'lower_translation':[-1.4220149316246022,-.25108997251065546],'rotations_all_zero':True,'core_front_mask':'core-shoulder-front-mask.png','not_source_passed':True}}
(P/'COMPOSITE_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))

for nm,v in [('lower',L),('core-back',B),('near-arm',A),('core-front',F)]:v.save(D/f'layer49-{nm}.png')
joints=Image.new('RGBA',(1000,500),(128,128,128,255)); joints.alpha_composite(assembled.crop((115,100,200,245)).resize((425,725)).crop((0,0,425,500)),(0,0)); joints.alpha_composite(assembled.crop((120,170,205,260)).resize((425,450)),(500,0)); joints.save(D/'shoulder-waist-hand-joints.png')
