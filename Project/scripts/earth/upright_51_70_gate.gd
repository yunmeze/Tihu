extends RefCounted
## Controlled prepare/reset lifecycle. No per-draw GPU readback or arbitrary-update protection.
const Identity=preload("res://scripts/earth/instance_identity_guard.gd")
const OwnerBank=preload("res://scripts/earth/plant_texture_weak_bank.gd")
const RawBank=preload("res://scripts/earth/upright_raw_weak_bank.gd")
var _plant_token:Dictionary={}
var _ground_token:Dictionary={}
var _plant_generation=-1
var _ground_generation=-1
const FlagIdentity=preload("res://scripts/earth/a13_visual_flag_identity.gd")
var _flag_identity=FlagIdentity.new()
var _source_identity:Dictionary={}
const ID="upright_tree_51_70"
signal revoked
var reg:Dictionary={}
var body:Texture2D
var receiver:Texture2D
var blocked:PackedStringArray=[]
var error="unprepared"
var generation=0
var _owners:Dictionary={}
var _floor_material:ShaderMaterial
var _ground_streams:Array=[]
var _canonical_holder:RefCounted
var _body_rid:RID
var _receiver_rid:RID
func fail(why:String) -> bool:
 error=why;return false
func reset() -> void:
 _source_identity={};_flag_identity.compatible_flags.clear();_plant_token={};_ground_token={};_plant_generation=-1;_ground_generation=-1
 generation+=1;reg={};body=null;receiver=null;_owners.clear();_floor_material=null;_ground_streams=[];_canonical_holder=null;revoked.emit()
func prepare(contract:Dictionary,world,deny:PackedStringArray=[]) -> bool:
 reset();blocked=deny
 if contract.get("caster")!=ID:return fail("caster identity")
 for path in contract.pins:
  if path in blocked or not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=contract.pins[path]:return fail("pin "+path)
 reg=contract
 _source_identity=reg.map_identity.duplicate(false)
 _source_identity["cells"]=reg.map_cells
 if not _flag_identity.prepare(_source_identity) or not _flag_identity.matches_source(world.map,_source_identity):return fail("actual A13 compatible cells")
 if world.floors.size()!=reg.floor_stream.size():return fail("floor stream size")
 for i in world.floors.size():
  var f=world.floors[i];var expected=reg.floor_stream[i]
  if f.pack!=expected.pack or f.index!=expected.index or f.origin!=Vector2(expected.origin[0],expected.origin[1]):return fail("actual floor stream")
 if not world.plant_reuse_groups.has(ID):return fail("modern complete tree absent")
 var group=world.plant_reuse_groups[ID]
 if group.contract!=reg.tree:return fail("tree contract mismatch")
 if not world.plant_reuse_guard.live_valid(group,world.map,world.objects,world.packs):return fail("tree body source qualification")
 for record in reg.tree.owners:
  var order=int(record.stable_source_order)
  if not world.plant_reuse_owners.has(order):return fail("active owner missing")
  var active=world.plant_reuse_owners[order]
  if active.pack!=record.pack or active.index!=record.index or active.origin!=Vector2(record.world_top_left[0],record.world_top_left[1]) or active.size!=Vector2(record.texture_size[0],record.texture_size[1])*float(record.scale) or active.empty!=record.empty:return fail("body draw registration")
  if not active.texture is CanvasTexture:return fail("body texture wrapper")
  var diffuse=active.texture.diffuse_texture
  if diffuse==null:return fail("body diffuse")
  # Existing immutable bank proves RGBA at load. Bind exact returned identity.
  var proven=OwnerBank.acquire(record.texture,record.texture_sha256,Vector2i(record.texture_size[0],record.texture_size[1]))
  if proven==null or proven!=diffuse:return fail("owner bank identity proof")
  _owners[order]={"wrapper":active.texture,"diffuse":diffuse,"rid":diffuse.get_rid(),"size":diffuse.get_size(),"origin":active.origin,"draw_size":active.size,"empty":active.empty}
 if not world.floor_pass.candidate_enabled or world.floor_pass.candidate.is_empty():return fail("explicit modern ground snapshot required")
 _floor_material=world.floor_pass.candidate.material
 _canonical_holder=world.floor_pass.candidate_guard.canonical_holder
 if _canonical_holder==null or not readonly_json(_canonical_holder.data):return fail("canonical ground not recursively readonly")
 var canonical=_canonical_holder.data.floors
 var streams=world.floor_pass.candidate.streams
 if streams.size()!=canonical.size():return fail("canonical stream count")
 for i in streams.size():
  var item=streams[i]
  if not item is Dictionary or not item.has_all(["key","kind","row"]) or not is_same(item.row,canonical[i]):return fail("canonical row identity")
  if not item.key is String or not item.kind is String or item.key!=canonical[i].key:return fail("stream key/kind")
  var snapshot={"key":item.key,"kind":item.kind,"row":canonical[i]}
  snapshot.make_read_only();_ground_streams.append(snapshot)
 _ground_streams.make_read_only()
 _plant_token=world.tree_plant_token
 _ground_token=world.floor_pass.ground_token
 _plant_generation=int(_plant_token.get("generation",-1));_ground_generation=int(_ground_token.get("generation",-1))
 if not _plant_token.get("active",false) or not _ground_token.get("active",false):return fail("inactive lifecycle")
 body=RawBank.acquire()
 var mask=Image.load_from_file(reg.receiver_path)
 if body==null or mask==null or mask.get_size()!=Vector2i(1208,388):return fail("input dimensions/proof")
 receiver=ImageTexture.create_from_image(mask);_body_rid=body.get_rid();_receiver_rid=receiver.get_rid()
 return valid(world)
func valid(world) -> bool:
 if not _plant_token.get("active",false) or not _ground_token.get("active",false):return fail("lifecycle revoked")
 if int(_plant_token.get("generation",-1))!=_plant_generation or int(_ground_token.get("generation",-1))!=_ground_generation:return fail("generation mutated")
 if world.tree_plant_token!=_plant_token or world.floor_pass.ground_token!=_ground_token:return fail("generation changed")
 if body==null or receiver==null or reg.is_empty():return fail("unbound")
 if body.get_rid()!=_body_rid or receiver.get_rid()!=_receiver_rid or body.get_size()!=Vector2(1162,1353) or receiver.get_size()!=Vector2(1208,388):return fail("controlled texture identity")
 for path in reg.pins:
  if path in blocked or not FileAccess.file_exists(path):return fail("missing "+path)
 if not _flag_identity.matches_source(world.map,_source_identity):return fail("map mutation outside eight allowed flags")
 if world.floors.size()!=reg.floor_stream.size():return fail("floor count mutation")
 for i in world.floors.size():
  var f=world.floors[i];var expected=reg.floor_stream[i]
  if f.pack!=expected.pack or f.index!=expected.index or f.origin!=Vector2(expected.origin[0],expected.origin[1]):return fail("floor identity mutation")
 if not world.floor_pass.candidate_enabled or world.floor_pass.candidate.is_empty():return fail("ground revoked")
 if world.floor_pass.candidate.material!=_floor_material or world.floor_pass.material!=_floor_material or not streams_match(world):return fail("ground snapshot changed; reprepare required")
 for pack in reg.frames:
  if not world.packs.has(pack):return fail("missing source pack")
  for index in reg.frames[pack]:
   if world.packs[pack].frames.get(index)!=reg.frames[pack][index]:return fail("source frame changed")
  if world.packs[pack].pages!=reg.pages[pack]:return fail("source atlas pages changed")
 if not world.prefer_plant_reuse or not world.plant_reuse_groups.has(ID):return fail("tree inactive")
 var group=world.plant_reuse_groups[ID]
 if group.contract!=reg.tree or not world.plant_reuse_guard.live_valid(group,world.map,world.objects,world.packs):return fail("tree qualification revoked")
 for record in reg.tree.owners:
  var order=int(record.stable_source_order)
  if not world.plant_reuse_owners.has(order) or not _owners.has(order):return fail("missing tree owner")
  var current=world.plant_reuse_owners[order];var bound=_owners[order]
  if current.pack!=record.pack or current.index!=record.index or current.texture!=bound.wrapper or current.texture.diffuse_texture!=bound.diffuse or bound.diffuse.get_rid()!=bound.rid or bound.diffuse.get_size()!=bound.size or current.origin!=bound.origin or current.size!=bound.draw_size or current.empty!=bound.empty:return fail("tree owner binding changed")
 var counts={}
 for entry in world.objects:
  var order=entry.get("order")
  if not counts.has(order):counts[order]=[]
  counts[order].append(entry)
 for owner in reg.source_owners:
  var order=int(owner.stable_source_order)
  if not counts.has(order) or counts[order].size()!=1:return fail("local foreground absent/duplicate")
  if not Identity.entry(counts[order][0],owner.source_cell[2],owner.pack,owner.index,owner.layer,owner.sort_y,order,Vector2(owner.cell[0]*48,owner.cell[1]*32)):return fail("local foreground identity changed")
 error="admitted local ground-only";return true

func readonly_json(value,depth:int=0)->bool:
 if depth>32:return false
 if value is Dictionary:
  if not value.is_read_only():return false
  for key in value:
   if not readonly_json(value[key],depth+1):return false
 elif value is Array:
  if not value.is_read_only():return false
  for item in value:
   if not readonly_json(item,depth+1):return false
 return true
func streams_match(world)->bool:
 if _canonical_holder==null or world.floor_pass.candidate_guard.canonical_holder!=_canonical_holder:return false
 var streams=world.floor_pass.candidate.get("streams",[])
 var canonical=_canonical_holder.data.floors
 if streams.size()!=_ground_streams.size() or canonical.size()!=_ground_streams.size():return false
 for i in _ground_streams.size():
  var item=streams[i];var bound=_ground_streams[i]
  if not item is Dictionary or not item.has_all(["key","kind","row"]):return false
  if item.key!=bound.key or item.kind!=bound.kind:return false
  if not is_same(item.row,bound.row) or not is_same(item.row,canonical[i]):return false
 return true
