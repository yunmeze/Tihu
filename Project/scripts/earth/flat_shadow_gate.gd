extends RefCounted
## Common ten-frame area footprint against a conservative, source-bound mask.
const Guard=preload("res://scripts/earth/asset_guard.gd")
const PATH="res://assets/earth/shadows/se_flat_v1/manifest.json"
const MANIFEST_SHA="3c7ac445562535c706cd58ebef625880308860ddfa012686fee600223beaec48"
var ready=false
var width=0
var height=0
var forbidden_prefix=PackedInt32Array()
var spans:Array[Vector3i]=[]
var envelope_offset=Vector2.ZERO
func prepare(path:String=PATH) -> bool:
	ready=false;spans.clear();forbidden_prefix.clear()
	if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=MANIFEST_SHA:return false
	var parser=JSON.new()
	if parser.parse(FileAccess.get_file_as_string(path))!=OK or not parser.data is Dictionary:return false
	var reg:Dictionary=parser.data
	# SHA-locked manifest carries a complete source-project dependency binding.
	for input in reg.runtime_input_sha256:
		var resource="res://"+input
		if not FileAccess.file_exists(resource) or FileAccess.get_sha256(resource)!=reg.runtime_input_sha256[input]:return false
	var allowed=read_mask(reg.allowed)
	var envelope=read_mask(reg.envelope)
	if allowed==null or envelope==null:return false
	width=allowed.get_width();height=allowed.get_height()
	if width!=1536 or height!=1024:return false
	var data=allowed.get_data();forbidden_prefix.resize((width+1)*height)
	for y in height:
		var total=0;var row=y*(width+1);forbidden_prefix[row]=0
		for x in width:
			var value=data[y*width+x]
			if value!=0 and value!=255:return false
			if value==0:total+=1
			forbidden_prefix[row+x+1]=total
	var e=envelope.get_data();var ew=envelope.get_width()
	for y in envelope.get_height():
		var start=-1
		for x in range(ew+1):
			var active=x<ew and e[y*ew+x]>0
			if active and start<0:start=x
			elif not active and start>=0:spans.append(Vector3i(start,x,y));start=-1
	envelope_offset=Vector2(reg.envelope.offset_logical[0],reg.envelope.offset_logical[1])
	ready=not spans.is_empty()
	return ready
func read_mask(record:Dictionary) -> Image:
	var tex=Guard.texture(record.texture,record.texture_size,record.sha256)
	if tex==null:return null
	var im=tex.get_image()
	if im==null:return null
	if im.is_compressed() and im.decompress()!=OK:return null
	im.convert(Image.FORMAT_L8)
	return im
func allows(actor_cell:Vector2) -> bool:
	if not ready or not actor_cell.is_finite() or absf(actor_cell.x)>4096 or absf(actor_cell.y)>4096:return false
	var base=(actor_cell*Vector2(48,32)+Vector2(-16,-64)+envelope_offset-Vector2(2496,960))*2
	for span in spans:
		# Every mask texel denotes an AREA, so fractional movement tests all
		# overlapped destination cells instead of rounded center samples.
		var x0=floori(base.x+span.x);var x1=ceili(base.x+span.y)
		var y0=floori(base.y+span.z);var y1=ceili(base.y+span.z+1)
		if x0<0 or x1>width or y0<0 or y1>height:return false
		for y in range(y0,y1):
			var row=y*(width+1)
			if forbidden_prefix[row+x1]!=forbidden_prefix[row+x0]:return false
	return true
