extends "res://scripts/earth/snapshot_world.gd"
# Optional static sorting reuse. Full parent validation remains authoritative.
const Exact=preload("res://scripts/earth/snapshot_exact_cache.gd")
const SORT_SOURCE_PINS={"res://scripts/world_view.gd": "b404d8dd5e7e85a120fec00b7eb5f01e6bfc1fc37adf5e7878c1798432d4e285", "res://scripts/earth/sample_world.gd": "c9139f34e1d57b1d33086c11157850454325c88078608fe13f8a081f7ddc07b2", "res://scripts/earth/first_map_world.gd": "ac530e0da86b975b8c79f076dc08c4b4c77052744b26637b5c36be926c10f87f", "res://scripts/earth/snapshot_world.gd": "543049941f235210703bca8a67a35c227af8881aa7eda0e8ca04c99126711821"}
var sort_methods_valid=false
var sort_reuse_enabled=true
var sort_baseline:Array=[]
var sort_bytes=PackedByteArray()
var sorted_static:Array=[]
var sort_ready=false
var sort_rebuilds=0
var sort_hits=0
var sort_fallbacks=0
var sort_check_us=0
var sort_rebuild_us=0
var sort_error="unprepared"
var exact_helper=Exact.new()
func prepare_visuals()->void:
 sort_ready=false
 sort_methods_valid=true
 for path in SORT_SOURCE_PINS:
  if FileAccess.get_sha256(path)!=SORT_SOURCE_PINS[path]:sort_methods_valid=false
 super.prepare_visuals()
func refresh()->void:
 super.refresh()
 if not is_inside_tree():return
 var began=Time.get_ticks_usec()
 if sort_reuse_enabled:refresh_sort_snapshot()
 else:sort_ready=false
 sort_check_us+=Time.get_ticks_usec()-began
func refresh_sort_snapshot()->void:
 if not sort_methods_valid:sort_ready=false;sort_error="source method drift";return
 # Complete independent objects baseline. Native equality is only a cheap reject;
 # byte equality preserves all Variant type differences, including nested fields.
 if sort_ready and objects==sort_baseline and var_to_bytes(objects)==sort_bytes:
  sort_hits+=1;return
 sort_ready=false
 var began=Time.get_ticks_usec()
 if not exact_helper.safe_value(objects,[],0):sort_error="non-data/nonfinite scene objects";return
 for entry in objects:
  if not entry is Dictionary or not entry.has_all(["kind","layer","y","order"]):sort_error="unknown object shape";return
  if not (entry.layer is int or entry.layer is float) or not (entry.y is int or entry.y is float) or not (entry.order is int or entry.order is float):sort_error="unknown comparator types";return
 sort_baseline=objects.duplicate(true)
 exact_helper.freeze(sort_baseline)
 sort_bytes=var_to_bytes(sort_baseline)
 sorted_static=sort_baseline.duplicate()
 sorted_static.sort_custom(less)
 for i in range(1,sorted_static.size()):
  if equal_key(sorted_static[i-1],sorted_static[i]):sort_error="static comparator tie: original path";return
 sorted_static.make_read_only()
 sort_ready=true;sort_rebuilds+=1;sort_error=""
 sort_rebuild_us+=Time.get_ticks_usec()-began
func less(a,b)->bool:
 if a.layer!=b.layer:return a.layer<b.layer
 if a.y!=b.y:return a.y<b.y
 return a.order<b.order
func equal_key(a,b)->bool:return a.layer==b.layer and a.y==b.y and a.order==b.order
func ordered_objects()->Array:
 if not sort_reuse_enabled or not sort_ready:sort_fallbacks+=1;return super.ordered_objects()
 var hero={"kind":-1,"layer":1,"y":movement.position.y,"order":int(map.width)*int(map.height)+map.npcs.size()}
 var low=0;var high=sorted_static.size()
 while low<high:
  var mid=(low+high)>>1
  if less(sorted_static[mid],hero):low=mid+1
  else:high=mid
 if low<sorted_static.size() and equal_key(sorted_static[low],hero):sort_fallbacks+=1;return super.ordered_objects()
 var result=sorted_static.duplicate();result.insert(low,hero)
 return result
