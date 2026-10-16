import pathlib,json,hashlib,argparse
from PIL import Image
P=pathlib.Path(__file__).resolve().parent;a=argparse.ArgumentParser();a.add_argument('--project',type=pathlib.Path,default=P.parents[1]);a.add_argument('--out',type=pathlib.Path,required=True);args=a.parse_args();args.out.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((P/'ARCHIVE.json').read_text());q=json.loads((P/'REQUEST_FROZEN.json').read_text())
for n,h in json.loads((P/'SHA256.json').read_text()).items():assert sha(P/n)==h,n
for d in m['dependencies']:assert sha(args.project/d['path'])==d['sha256']
assert (P/'PROMPT_DRAFT.txt').read_text()==q['prompt'];assert q['transparent_background'] is True and len(q['referenced_image_paths'])==2
src=Image.open(args.project/'art_source/hero_s_walk_source_r8/source-59.png').convert('RGBA').resize((512,512),Image.Resampling.NEAREST);idle=Image.open(args.project/'assets/earth/hero/s_idle_v1/body.png').convert('RGBA').crop((0,0,512,512))
for image,path in zip([src,idle],m['actual_reference_project_paths']):assert image.tobytes()==Image.open(args.project/path).convert('RGBA').tobytes()
im=Image.open(P/'RAW.png').convert('RGBA');assert im.size==(1254,1254);im=im.resize((512,512),Image.Resampling.LANCZOS);im.save(args.out/'display512.png');assert sha(args.out/'display512.png')==m['mapped_png_sha256'];assert hashlib.sha256(im.tobytes()).hexdigest()==m['mapped_rgba_sha256'];print('PASS actual refs bytepins/sourceRGBA and exact wholecanvas mapping')
