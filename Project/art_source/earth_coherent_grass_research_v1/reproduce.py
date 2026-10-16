"""Rebuild conservative coherent-grass research union without diagnostic dependencies."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent
P=O.parents[1]

def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p))>0
def js(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def up(a):return np.repeat(np.repeat(a,2,0),2,1)

def reproduce(output, contact_refresh=False):
    prov=js(O/'ARCHIVE_PROVENANCE.json')
    for path,digest in prov['input_sha256'].items():assert sha(P/path)==digest,path
    output=Path(output).resolve();assert not output.exists(),'Refusing overwrite';output.mkdir(parents=True)
    # Reconstruct corrected shared plates from tracked source art and frozen patch.
    old=rgba(P/'art_source/earth_ground_plate_clean_regen_v4/raw.png')
    south=rgba(P/'art_source/earth_south_ground_candidate_v1/raw.png')
    patch=rgba(P/'art_source/earth_ground_source_corrected_research_v1/03_source_corrected_contact.png')
    fixed=mask(P/'art_source/earth_ground_cross_seam_revision_plan_v3/PROPOSED_fixed_replace_mask.png')
    y,x=np.where(fixed);inside=(x>=192)&(y+672<1024);old[y[inside]+672,x[inside]-192]=patch[y[inside],x[inside]]
    inside=y>=224;south[y[inside]-224,x[inside]]=patch[y[inside],x[inside]]
    south[:128,192:]=old[896:1024,:1344]
    initial=js(P/'assets/earth/environment/ground_plate_v4/registration.json')
    southern=js(P/'art_source/earth_south_ground_input_plan_v1/source_owner_evidence.json')
    source_map=js(P/'data/maps/A13.json');manifest=js(P/'assets/original/manifest.json')
    owners=[]
    for item in initial['owners']:owners.append((item,item['world_top_left'],item['shared_region_px'],old))
    for item in southern['owners']:
        if item['status']=='frozen_existing_v4':continue
        owners.append((item,item['world_bounds_xyxy'][:2],item['proposed_whole_canvas_region_px'],south))
    owners.sort(key=lambda row:row[0]['stable_source_order']);assert len(owners)==121
    base=Image.new('RGBA',(1728,1920));coverage=np.zeros((960,864),bool)
    grassbase=np.zeros_like(coverage);tan=np.zeros_like(coverage)
    pages={};frames={}
    for item,world,region,plate in owners:
        n=item['frame_index'];cx,cy=item['cell'];order=cx*source_map['height']+cy
        assert order==item['stable_source_order'] and source_map['cells'][order]==item['source_cell']
        pack=manifest['packs'][item['pack']];frame=pack['frames'][str(n)]
        page=P/pack['pages'][frame['page']]['file'][6:]
        if page not in pages:pages[page]=rgba(page)
        fx,fy,fw,fh=frame['rect'];native=pages[page][fy:fy+fh,fx:fx+fw];frames[n]=native
        assert native.shape==(64,96,4) and (native[:,:,3]==255).all()
        assert [cx*48+frame['crop'][0],cy*32+frame['crop'][1]]==world
        xx,yy=world[0]-2400,world[1]-960
        assert not coverage[yy:yy+64,xx:xx+96].any();coverage[yy:yy+64,xx:xx+96]=True
        if n in [398,399,406,407]:grassbase[yy:yy+64,xx:xx+96]=True
        if n in [586,587,594,595]:tan[yy:yy+64,xx:xx+96]=True
        gx,gy,gw,gh=region;base.paste(Image.fromarray(plate[gy:gy+gh,gx:gx+gw]),(2*xx,2*yy))
    assert coverage.sum()==743424
    base=np.array(base);Image.fromarray(base).save(output/'base-union.png')
    bake=js(O/'BAKE_PROVENANCE.json');assert sha(output/'base-union.png')==bake['base_sha256']
    # Recreate manual conservative interior labels. All unlabeled pixels stay uncertain.
    review=js(O/'SOURCE_INTERIOR_POLYGONS.json');labels=np.zeros((960,864),np.uint8)
    touched=np.zeros_like(coverage);earth=np.zeros_like(coverage);codes={'grass':1,'road':2,'curb':3,'earth':4}
    assert np.array_equal(frames[597],frames[588])
    assert hashlib.sha256(frames[588].tobytes()).hexdigest()==review['byte_identical_frame_proof']['RGBA_sha256']
    for record in review['frames']:
        n=record['frame_id'];native=frames[n]
        assert hashlib.sha256(native.tobytes()).hexdigest()==record['source_RGBA_sha256']
        local=np.zeros((64,96),np.uint8)
        for name,polygons in record['manual_interior_polygons_source_pixel_centers'].items():
            for polygon in polygons:
                im=Image.new('1',(96,64));ImageDraw.Draw(im).polygon([tuple(p) for p in polygon],fill=1);a=np.array(im)
                assert not local[a].any();local[a]=codes[name]
        actual=[item['key'] for item,_,_,_ in owners if item['frame_index']==n]
        assert actual==[item['key'] for item in record['owner_occurrences']]
        for item,world,_,_ in owners:
            if item['frame_index']!=n:continue
            xx,yy=world[0]-2400,world[1]-960;labels[yy:yy+64,xx:xx+96]=local;touched[yy:yy+64,xx:xx+96]=True
            if n in [385,386,388]:earth[yy:yy+64,xx:xx+96]=True
    mixed=touched&(labels==1)&~earth
    proposed=up(grassbase|mixed)
    # Independently rebuild original authored curb and preserve all frozen contact supports.
    oldcurb=mask(P/'art_source/earth_ground_material_layers_plan_v1/DOMAIN_curb_BINARY.png')
    plan=js(P/'art_source/earth_ground_cross_seam_revision_plan_v3/PLAN.json')
    Y,X=np.indices(fixed.shape,dtype=float);X+=.5;Y+=.5
    u=np.clip((Y-72)/28,0,1);smooth=1-u*u*(3-2*u);dx=4.5*smooth;dw=-3*smooth;distance=np.full(X.shape,np.inf)
    for aa,bb in zip(plan['source_center_polyline_localraw'],plan['source_center_polyline_localraw'][1:]):
        vx,vy=bb[0]-aa[0],bb[1]-aa[1];t=np.clip(((X-dx-aa[0])*vx+(Y-aa[1])*vy)/(vx*vx+vy*vy),0,1)
        distance=np.minimum(distance,np.hypot(X-dx-aa[0]-t*vx,Y-aa[1]-t*vy))
    width=np.where(Y<100,18-10*u,8)+dw;curb=np.where((Y>=72)&(Y<100),fixed&(distance<=width/2),oldcurb)
    protects={'earth_transition':up(earth),'boundary_uncertainty':up(touched&(labels==0)),'road_interior':up(touched&(labels==2)),'curb_interior':up(touched&(labels==3)),'tan_base':up(tan)}
    locals={'authored_curb':curb,'seam':mask(P/'art_source/earth_ground_source_corrected_research_v1/seam_support.png'),'lip':mask(P/'art_source/earth_ground_source_corrected_research_v1/lip_support.png'),'grass_contact':mask(P/'art_source/earth_ground_source_corrected_research_v1/grass_contact_support.png')}
    for name,local in locals.items():
        a=np.zeros((1920,1728),bool);a[672:1824,:1536]=local;protects[name]=a
    blocked=protects['earth_transition'].copy()
    for name in locals:blocked|=protects[name]
    core=proposed&~blocked
    assert core.sum()==2373576 and not (core&~up(coverage)).any()
    assert all(not (core&p).any() for p in protects.values())
    assert np.array_equal(core,mask(O/'grass-core-conservative.png'))
    Image.fromarray(core.astype('uint8')*255).save(output/'grass-core-conservative.png')
    assert sha(output/'grass-core-conservative.png')=='d40582eddfc1b8b86c57aabcdf420c954e7f96cc7e2b1c53b2493f8674b9cb84'
    # Material-only changes:1254->1024 LANCZOS, encoded-sRGB affine,1024->768 LANCZOS.
    raw=Image.open(O/'raw.png').convert('RGB');assert raw.size==(1254,1254)
    tile=raw.resize((1024,1024),Image.Resampling.LANCZOS);a=np.array(tile,float)/255
    ref=np.array(Image.open(P/'art_source/earth_ground_grass_material_g_v2/INPUT_approved_wide_grass_native2x.png').convert('RGB'),float)/255
    gain=ref.std((0,1))/a.std((0,1));bias=ref.mean((0,1))-gain*a.mean((0,1))
    calibration=js(O/'PALETTE_TRANSFORM.json')
    assert np.allclose(gain,calibration['gain_rgb'],atol=1e-14) and np.allclose(bias,calibration['bias_rgb'],atol=1e-14)
    transformed=a*gain+bias;assert not ((transformed<0)|(transformed>1)).any()
    corrected=Image.fromarray(np.floor(255*np.clip(transformed,0,1)+.5).astype('uint8'))
    tile=corrected.resize((768,768),Image.Resampling.LANCZOS);tile.save(output/'tile-period384.png')
    assert sha(output/'tile-period384.png')==bake['tile_sha256']
    y,x=np.indices(core.shape);field=np.array(tile)[(1920+y)%768,(4800+x)%768]
    result=base.copy();result[core,:3]=field[core];changed=np.any(result!=base,axis=2)
    assert not changed[~core].any() and np.array_equal(result[:,:,3],base[:,:,3])
    assert all(not (changed&p).any() for p in protects.values())
    assert np.array_equal(result,rgba(O/'coherent-grass-union-RESEARCH.png'))
    Image.fromarray(result).save(output/'coherent-grass-union-RESEARCH.png')
    digest=sha(output/'coherent-grass-union-RESEARCH.png');assert digest==bake['after_sha256']
    if contact_refresh:
        refresh=js(O/'OPTIONAL_CONTACT_REFRESH.json')
        local_path=P/'art_source/earth_ground_source_corrected_research_v1/grass_contact_support.png'
        params_path=P/'art_source/earth_ground_source_corrected_research_v1/FROZEN_PARAMETERS_UNCHANGED.json'
        assert sha(local_path)==refresh['original_support_sha256'] and sha(params_path)==refresh['parameters_sha256']
        support=protects['grass_contact'];assert support.sum()==3283
        Image.fromarray(support.astype('uint8')*255).save(output/'optional-contact-support.png')
        assert sha(output/'optional-contact-support.png')==refresh['mapped_support_sha256']
        k=js(params_path)['grass_contact']['k'];assert k==refresh['k_linear_RGB']==0.5314862566564135
        cy,cx=np.where(support);fresh=np.array(tile)[(1920+cy)%768,(4800+cx)%768]/255.
        linear=np.where(fresh<=.04045,fresh/12.92,((fresh+.055)/1.055)**2.4)
        shaded=linear*k;encoded=np.where(shaded<=.0031308,shaded*12.92,1.055*shaded**(1/2.4)-.055)
        assert encoded.min()>=0 and encoded.max()<=1
        variant=result.copy();variant[cy,cx,:3]=np.floor(255*encoded+.5).astype('uint8')
        delta=np.any(variant!=result,axis=2)
        assert delta.sum()==3282 and not delta[~support].any() and np.array_equal(variant[:,:,3],result[:,:,3])
        assert all(not(delta&protects[n]).any() for n in ['seam','lip','authored_curb'])
        Image.fromarray(variant).save(output/'OPTIONAL-contact-refreshed-union-RESEARCH.png')
        variant_sha=sha(output/'OPTIONAL-contact-refreshed-union-RESEARCH.png');assert variant_sha==refresh['after_sha256']
        assert sha(output/'coherent-grass-union-RESEARCH.png')==bake['after_sha256']
        print(json.dumps({'optional_contact_refresh':True,'sha256':variant_sha,'byte_identical':True,'support_pixels':3283,'changed_pixels':3282,'outside_support_changed':0,'baseline_preserved':True}))
    print(json.dumps({'RGBA_different_pixels':0,'byte_identical':True,'sha256':digest,'owners':121,'core_pixels':int(core.sum()),'changed_pixels':int(changed.sum()),'protection_overlaps':{k:int((core&v).sum()) for k,v in protects.items()}}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--contact-refresh',action='store_true',help='Also emit separate exact-support contact-material variant')
    args=parser.parse_args();reproduce(args.output,args.contact_refresh)
