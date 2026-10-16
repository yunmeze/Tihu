exec(open(__file__.replace('compare.py','measure.py')).read().split('allres={}')[0])
x=json.loads((P/'MEASUREMENTS.json').read_text())
for phase,v in x.items():
 src=Image.open(E/phase/'input-context.png').convert('RGBA');raw=Image.open(E/phase/'mapped-UNMASKED.png').convert('RGBA');s=v['uniform_scale_source_to_mapped_raw'];tx,ty=v['translation_source_to_mapped_raw'];tar=rgb(raw)
 aligned=raw.transform((512,512),Image.Transform.AFFINE,(s,0,tx,0,s,ty),resample=Image.Resampling.BICUBIC)
 v['inverse_registration_measurement_only']={'mapped_raw_scale_to_context':1/s,'mapped_raw_translation_to_context':[-tx/s,-ty/s],'raw_pixel_to_HD4_density':512/1254/s,'raw_pixel_to_logical_density':128/1254/s}
 for r in v['rows']:
  b=r['box'];patch=src.crop(b);center=np.array(r['predicted_center']);p=rgb(patch.resize((round(patch.width*s),round(patch.height*s)),Image.Resampling.BICUBIC));rx=p.shape[1]/2+12;ry=p.shape[0]/2+12;reg=(int(center[0]-rx),int(center[1]-ry),int(center[0]+rx),int(center[1]+ry));score,xy=match(tar,p,reg);r['global_scale_ncc']=score;r['global_scale_local_center']=xy;r['global_scale_heldout_center_residual_logical']=float(np.linalg.norm(np.array(xy)-center)/4);r['local_scale_difference_percent']=100*(r['local_diagnostic_scale']/s-1)
 for bg,col in [('gray',(128,128,128)),('light',(228,228,228)),('dark',(35,35,35))]:
  board=Image.new('RGBA',(1536,512),col+(255,));board.alpha_composite(src);board.alpha_composite(aligned,(512,0));over=Image.blend(src,aligned,0.5);board.alpha_composite(over,(1024,0));ImageDraw.Draw(board).text((5,5),'INPUT | GLOBAL SIMILARITY TECHNICAL ALIGNMENT | 50% OVERLAY - NOT ASSET',fill='white');board.save(D/f'{phase}-global-similarity-technical-{bg}.png')
(P/'MEASUREMENTS.json').write_text(json.dumps(x,indent=2)+'\n')
for phase,v in x.items():
 print(phase,v['inverse_registration_measurement_only'])
 for r in v['rows']:print(r['name'],'scale delta%',round(r['local_scale_difference_percent'],2),'fixedNCC',round(r['global_scale_ncc'],3),'residual logical',round(r['global_scale_heldout_center_residual_logical'],3))
