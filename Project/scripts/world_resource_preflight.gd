extends RefCounted
## Detached rendering dependency closure; never mutates the source map.
const GROUPS={1:"Map/Res/Debris",2:"Map/Res/Plant",3:"Map/Res/Wall",4:"Map/Res/Building",5:"Map/Res/Dynamic",8:"Data4"}
static func fail(message:String)->Dictionary:return {"ok":false,"error":message}
static func read(path:String)->Dictionary:
	if not FileAccess.file_exists(path):return fail("Missing JSON: "+path)
	var parser=JSON.new()
	if parser.parse(FileAccess.get_file_as_string(path))!=OK:return fail("Invalid JSON: "+path)
	if not parser.data is Dictionary:return fail("JSON object required: "+path)
	return {"ok":true,"value":parser.data}
static func number(v)->bool:return (v is int or v is float) and is_finite(float(v)) and float(v)==floor(float(v)) and abs(float(v))<=2147483647
static func pair(v,positive:bool=false)->bool:
	return v is Array and v.size()==2 and number(v[0]) and number(v[1]) and (not positive or (v[0]>0 and v[1]>0))
static func texture(path,size)->Dictionary:
	if not path is String or not path.begins_with("res://") or not pair(size,true):return fail("Invalid texture declaration")
	if not ResourceLoader.exists(path):return fail("Unimported texture: "+path)
	var tex=load(path)
	if not tex is Texture2D or tex.get_size()!=Vector2(size[0],size[1]):return fail("Texture size/type mismatch: "+path)
	return {"ok":true}
static func frame(f,size,packed:bool)->bool:
	if not f is Dictionary or not pair(f.get("offset")) or not pair(f.get("original"),true):return false
	var r=f.get("rect")
	if not r is Array or r.size()!=4:return false
	for n in r:
		if not number(n):return false
	if r[0]<0 or r[1]<0 or r[2]<=0 or r[3]<=0 or r[0]+r[2]>size[0] or r[1]+r[3]>size[1]:return false
	if packed:
		var c=f.get("crop")
		if not pair(c) or c[0]<0 or c[1]<0 or c[0]+r[2]>f.original[0] or c[1]+r[3]>f.original[1]:return false
	return true
static func manifest(path:String)->Dictionary:
	var parsed=read(path)
	if not parsed.ok:return parsed
	var packs=parsed.value.get("packs")
	if not packs is Dictionary or packs.is_empty():return fail("Missing packs: "+path)
	for name in packs:
		var pack=packs[name]
		if not pack is Dictionary or not pack.get("pages") is Array or not pack.get("frames") is Dictionary:return fail("Malformed pack: "+str(name))
		for page in pack.pages:
			if not page is Dictionary:return fail("Malformed page")
			var checked=texture(page.get("file"),page.get("size"))
			if not checked.ok:return checked
		for key in pack.frames:
			var f=pack.frames[key]
			if not f is Dictionary or not number(f.get("page")) or f.page<0 or f.page>=pack.pages.size():return fail("Invalid frame page: "+str(name)+"/"+str(key))
			if not frame(f,pack.pages[int(f.page)].size,true):return fail("Invalid frame geometry: "+str(name)+"/"+str(key))
	return {"ok":true,"packs":packs}
static func check(map:Dictionary)->Dictionary:
	var path=map.get("texture_manifest","res://assets/original/manifest.json")
	if not path is String:return fail("Invalid map manifest path")
	var checked=manifest(path)
	if not checked.ok:return checked
	var packs=checked.packs
	var required:Dictionary={}
	for cell in map.cells:
		if cell[0]!=0:required[("Map/Res/FloorBig" if cell[0]<0 else "Map/Res/FloorSmall")+":"+str(absi(int(cell[0])))]=true
		var kind=int(cell[2]);var index=int(cell[3])
		if index>0 and GROUPS.has(kind):
			for i in (5 if kind in [5,8] else 1):required[GROUPS[kind]+":"+str(55+i if kind==8 else index+i)]=true
	for npc in map.npcs:
		if not npc is Dictionary or not number(npc.get("appearance")) or npc.appearance<0 or npc.appearance>32767 or not number(npc.get("direction")) or npc.direction<0 or npc.direction>2:return fail("Invalid NPC appearance/direction")
		if not npc.get("name") is String or not npc.get("script") is String or not number(npc.get("x")) or not number(npc.get("y")):return fail("Invalid NPC metadata")
		for i in 4:required["Npc:"+str(1+int(npc.appearance)*12+int(npc.direction)*4+i)]=true
	for key in required:
		var pieces=key.split(":")
		if not packs.has(pieces[0]) or not packs[pieces[0]].frames.has(pieces[1]):return fail("Missing referenced frame: "+key)
	var hp=read("res://data/hero/movement.json")
	if not hp.ok:return hp
	if not hp.value.get("layers") is Dictionary or hp.value.layers.size()!=2:return fail("Expected exactly body and head layers")
	for name in ["body","head"]:
		var layer=hp.value.layers.get(name)
		if not layer is Dictionary or not layer.get("frames") is Dictionary:return fail("Missing hero layer: "+name)
		checked=texture(layer.get("atlas"),layer.get("atlas_size"))
		if not checked.ok:return checked
		for id in range(1,129):
			if not frame(layer.frames.get(str(id)),layer.atlas_size,false):return fail("Invalid hero frame: "+name+"/"+str(id))
	for unit in map.get("added_units",[]):
		if not unit is Dictionary or not unit.get("texture_manifest") is String or not number(unit.get("definition_id")) or int(unit.definition_id)!=508:return fail("Invalid added unit display fields")
		checked=manifest(unit.texture_manifest)
		if not checked.ok:return checked
		if not checked.packs.has("Mon/220") or not checked.packs["Mon/220"].frames.has("1"):return fail("Missing chicken display frame")
	return {"ok":true}
