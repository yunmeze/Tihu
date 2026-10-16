extends RefCounted
## Narrow visual-only atlas admission, separate from R6 transaction authority.
const Preflight=preload("res://scripts/world_resource_preflight.gd")
const PINS={"res://data/monsters/a13-chicken.json": "4046ae10127843058cf369b4d4d19532d8c483f8ac331f3953d4338d6913d363", "res://assets/original/monsters/a13-chicken/manifest.json": "4d464c422c52beadfb283193a399868d7cb0537849809187c826de94e14fe0c3", "res://assets/original/monsters/a13-chicken/0.png": "ae89cdf0bd172772aae4fdd8f2419baa7dfdcca1a0d22a5a1dbce4acf28ebbfe", "res://assets/original/manifest.json": "506fba1f0fd826589046d38e4ebd5285ee9a11e3235cd78495cdd133c2e63837"}
const MANIFEST="res://assets/original/monsters/a13-chicken/manifest.json"
const UNIT={"x":49,"y":53,"name":"彩蛋鸡","definition_id":508,"texture_manifest":MANIFEST,"runtime_behavior":"entity_record_only"}
const ExactCache=preload("res://scripts/earth/snapshot_exact_cache.gd")
var exact_cache=ExactCache.new()
func snapshot_payload(packs:Dictionary,disk:Dictionary,map:Dictionary,objects:Array) -> Dictionary:
	return {"packs":packs,"disk":disk,"map":map,"objects":objects,"original":original,"chicken":chicken}
func prepare_snapshot(packs:Dictionary,disk:Dictionary,map:Dictionary,objects:Array) -> bool:
	exact_cache.clear()
	return slow_matches(packs,disk,map,objects) and exact_cache.capture(snapshot_payload(packs,disk,map,objects))
var original:Dictionary={}
var chicken:Dictionary={}
var resources_ready=false
var failure="not prepared"
func prepare() -> bool:
	exact_cache.clear()
	resources_ready=false;original.clear();chicken.clear()
	for path in PINS:
		if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=PINS[path]:failure="atlas dependency SHA";return false
	var source=Preflight.read("res://assets/original/manifest.json")
	var source_checked=Preflight.manifest("res://assets/original/manifest.json")
	var definition=Preflight.read("res://data/monsters/a13-chicken.json")
	var checked=Preflight.manifest(MANIFEST)
	if not source.ok or not source_checked.ok or not definition.ok or not checked.ok:failure="full source preflight";return false
	if not source.value.get("packs") is Dictionary or checked.packs.keys()!=["Mon/220"]:failure="unexpected pack set";return false
	if definition.value.get("definition_id")!=508 or definition.value.get("texture_manifest")!=MANIFEST or definition.value.get("name")!=UNIT.name:failure="definition identity";return false
	original=source.value.packs.duplicate(true);chicken=checked.packs["Mon/220"].duplicate(true)
	resources_ready=true;failure="";return true
func matches(packs:Dictionary,disk:Dictionary,map:Dictionary,objects:Array) -> bool:
	if resources_ready and exact_cache.matches(snapshot_payload(packs,disk,map,objects)):return true
	return slow_matches(packs,disk,map,objects)
func slow_matches(packs:Dictionary,disk:Dictionary,map:Dictionary,objects:Array) -> bool:
	if not resources_ready or disk!=original:return reject("unprepared or changed original atlas")
	for name in original:
		if not packs.has(name) or typeof(packs[name])!=TYPE_DICTIONARY or packs[name]!=original[name]:return reject("original pack changed")
	var extras=[]
	for name in packs:
		if not original.has(name):extras.append(name)
	var units=map.get("added_units",[])
	if not units is Array:return reject("unit bank structure")
	var actual=[]
	for entry in objects:
		if not entry is Dictionary:return reject("owner structure")
		if entry.get("kind")==9:actual.append(entry)
	if units.is_empty():
		if not extras.is_empty() or not actual.is_empty():return reject("unbound extra pack or owner")
		return true
	if units!=[UNIT] or extras!=["Mon/220"] or typeof(packs["Mon/220"])!=TYPE_DICTIONARY or packs["Mon/220"]!=chicken or actual.size()!=1:return reject("unproven extra pack or chicken descriptor")
	var expected={"pack":"Mon/220","index":1,"kind":9,"layer":1,"y":53.0,"origin":Vector2(49*48,53*32),"order":int(map.width)*int(map.height)+map.npcs.size()+objects.size()-1}
	if actual[0]!=expected:return reject("chicken actual owner identity")
	return true
func reject(reason:String) -> bool:
	failure=reason;return false
