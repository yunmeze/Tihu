extends RefCounted
var failure=""
const ManifestCache=preload("res://scripts/earth/ground_manifest_weak_cache.gd")
var canonical_holder:RefCounted
const TextureBank=preload("res://scripts/earth/ground_texture_weak_bank.gd")
const FlagIdentity=preload("res://scripts/earth/a13_visual_flag_identity.gd")
const FLAG_CONTRACT=FlagIdentity.FLAG_CONTRACT
const FLAG_CONTRACT_SHA=FlagIdentity.FLAG_CONTRACT_SHA
var flag_identity=FlagIdentity.new()
func prepare_visual_identity(source:Dictionary)->bool:
 var original=JSON.parse_string(FileAccess.get_file_as_string("res://data/maps/A13.json"))
 return original is Dictionary and flag_identity.prepare(original) and flag_identity.matches_source(source,original)
func source_cell_matches(actual,expected,order:int)->bool:
 return flag_identity.source_cell_matches(actual,expected,order)
const REG="res://ground_candidate/registration.json"
func reject(why:String)->Dictionary:
 failure=why;canonical_holder=null
 return {}
func integer(v)->bool:return (v is int or v is float) and is_finite(float(v)) and float(v)==floor(float(v))
func numbers(a,b)->bool:
 if not a is Array or a.size()!=b.size():return false
 for i in a.size():
  if not integer(a[i]) or float(a[i])!=float(b[i]):return false
 return true
func texture(diffuse:Texture2D,linear:bool)->CanvasTexture:
 var t=CanvasTexture.new();t.diffuse_texture=diffuse;t.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR if linear else CanvasItem.TEXTURE_FILTER_NEAREST;t.texture_repeat=CanvasItem.TEXTURE_REPEAT_DISABLED;return t
func bank(path:String,reg:Dictionary,size:Vector2i,construction:String)->ImageTexture:
 if not reg.pins.has(path):return null
 return TextureBank.acquire(path,reg.pins[path],size,construction)
func identity(row:Dictionary,i:int,world)->bool:
 if row.get("category")!="floor" or not integer(row.get("floor_stream_index")) or row.floor_stream_index!=i:return false
 if i>=world.floors.size():return false
 var f=world.floors[i];var cell=[f.origin.x/48,f.origin.y/32]
 if row.get("pack")!=f.pack or not integer(row.get("index")) or row.index!=f.index or not numbers(row.get("cell"),cell):return false
 if not numbers(row.get("world_origin"),[f.origin.x,f.origin.y]):return false
 var index=int(cell[0])*int(world.map.height)+int(cell[1])
 if not source_cell_matches(world.map.cells[index],row.get("source_cell"),index):return false
 var expected_key="%s:%d@%d,%d"%[f.pack,f.index,cell[0],cell[1]]
 return row.get("key")==expected_key and row.get("source_frame")==world.packs[f.pack].frames[str(f.index)]
const REG_SHA="c5e372450acf9f1ef44c26e1c9f93eea27e31c0f21dc1cd74904355cf98d72bb"
func prepare(world,reg:Dictionary={},manifest:Dictionary={})->Dictionary:
 failure=""
 if FileAccess.get_sha256(REG)!=REG_SHA:return reject("registration pin")
 var canonical=JSON.parse_string(FileAccess.get_file_as_string(REG))
 if not reg.is_empty() and reg!=canonical:return reject("registration mutation")
 if reg.is_empty():reg=canonical
 if reg.is_empty() or reg.get("schema")!="ground-modern-candidate-v1":return reject("registration schema")
 for path in reg.pins:
  if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=reg.pins[path]:return reject("pin "+path)
 if reg.get("visual_flag_compatibility")!={"path":FLAG_CONTRACT,"sha256":FLAG_CONTRACT_SHA}:return reject("flag compatibility registration")
 if not prepare_visual_identity(world.map):return reject("map visual source identity")
 var holder=ManifestCache.acquire(ManifestCache.PATH,reg.pins.get(ManifestCache.PATH,""))
 if holder==null:return reject("canonical manifest content")
 canonical_holder=holder
 var canonical_manifest=holder.data
 if not manifest.is_empty() and manifest!=canonical_manifest:return reject("manifest mutation")
 manifest=canonical_manifest
 if manifest.is_empty() or manifest.floors.size()!=2553 or world.floors.size()!=2553:return reject("floor count")
 var seen={};var c={};var images={};var frames={};var counts={"C":0,"grass":0,"current":0,"source":0};var streams=[]
 if reg.C.size()!=24:return reject("C count")
 for row in reg.C:
  if not integer(row.get("floor_stream_index")) or row.floor_stream_index<0 or row.floor_stream_index>=2553:return reject("C stream index")
  if not identity(row,int(row.floor_stream_index),world) or c.has(row.key):return reject("C identity duplicate")
  c[row.key]=true
 for i in manifest.floors.size():
  var row=manifest.floors[i]
  if not identity(row,i,world) or seen.has(row.key):return reject("source identity "+str(i))
  seen[row.key]=true
  var kind="C" if c.has(row.key) else ("grass" if row.reuse else ("current" if row.current else "source"))
  counts[kind]+=1;streams.append({"key":row.key,"kind":kind,"row":row})
  if kind=="source":continue
  if not numbers(row.world_bounds,[row.world_origin[0],row.world_origin[1],row.world_origin[0]+96,row.world_origin[1]+64]) or not numbers(row.source_frame.crop,[0,0]) or not numbers(row.source_frame.original,[96,64]) or not numbers(row.source_frame.offset,[0,0]):return reject("complete rectangle")
 if counts!={"C":24,"grass":907,"current":39,"source":1583}:return reject("partition count")
 # Every visual identity and rectangle passed before any atlas/image allocation.
 for item in streams:
  if item.kind=="source":continue
  var row=item.row
  var frame_key=row.pack+":"+str(row.index)
  if frames.has(frame_key):continue
  if not images.has(row.atlas):
   var image=Image.load_from_file(row.atlas)
   if image==null:return reject("atlas rawload")
   images[row.atlas]=image
  var r=row.source_frame.rect;var im=images[row.atlas].get_region(Rect2i(r[0],r[1],r[2],r[3]));im.convert(Image.FORMAT_RGBA8)
  if im.get_size()!=Vector2i(96,64):return reject("tile size")
  var data=im.get_data();var hash=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(data)
  if hash.finish().hex_encode()!=row.source_rgba_sha256:return reject("source rgba")
  for j in range(3,data.size(),4):
   if data[j]!=255:return reject("source opacity")
  frames[frame_key]=true
 var textures={}
 for key in ["soil.png","grass.png","overlay413.png","overlayG3.png"]:
  var diffuse=bank("res://ground_candidate/"+key,reg,Vector2i(1536,1024) if key.begins_with("overlay") else Vector2i(768,768),"png-rgba8-v1")
  if diffuse==null:return reject("verified image bank "+key)
  textures[key]=texture(diffuse,true)
 var field=bank("res://ground_candidate/field.rf32",reg,Vector2i(961,705),"rf32-961x705-v1")
 if field==null:return reject("verified field bank")
 if reg.overlays.size()!=4:return reject("overlay count")
 for key in reg.overlays:
  if not c.has(key) or not reg.overlays[key] in ["overlay413.png","overlayG3.png"]:return reject("overlay identity")
 var grass=bank(manifest.tile,reg,Vector2i(2304,2304),"png-rgba8-tile3x3-v1")
 if grass==null:return reject("verified tiled grass bank")
 var union_image=bank(manifest.union,reg,Vector2i(1728,1920),"png-rgba8-v1")
 if union_image==null:return reject("verified union bank")
 var mat=ShaderMaterial.new();mat.shader=load("res://ground_candidate/ground.gdshader")
 if mat.shader==null:return reject("shader load")
 mat.set_shader_parameter("soil_tex",textures['soil.png'].diffuse_texture);mat.set_shader_parameter("grass_tex",textures['grass.png'].diffuse_texture);mat.set_shader_parameter("continuous_data",field)
 return {"streams":streams,"textures":textures,"grass":texture(grass,true),"union":texture(union_image,true),"material":mat,"overlays":reg.overlays,"counts":counts,"floors":world.floors.duplicate(true),"cells":world.map.cells.duplicate(true)}
