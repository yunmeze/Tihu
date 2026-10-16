extends RefCounted
## Only the eight source LOAD collision flags are compatible; all visual fields stay exact.
const FLAG_CONTRACT="res://ground_candidate/visual_flag_compatibility.json"
const FLAG_CONTRACT_SHA="bb8972e12b26964e8acd00c03f79cb0ef6e78ff4ca349492a9bdf9f7b31a1218"
var compatible_flags:Dictionary={}
func prepare(original:Dictionary)->bool:
 compatible_flags.clear()
 if FileAccess.get_sha256(FLAG_CONTRACT)!=FLAG_CONTRACT_SHA:return false
 var contract=JSON.parse_string(FileAccess.get_file_as_string(FLAG_CONTRACT))
 if not contract is Dictionary or contract.get("schema")!="a13-ground-visual-flag-compatibility-v1":return false
 if FileAccess.get_sha256(contract.source_path)!=contract.source_sha256:return false
 if not original is Dictionary or original.loadScript.sha256_text()!=contract.load_script_sha256:return false
 if not contract.get("source_cells") is Array or contract.source_cells.size()!=8:return false
 for row in contract.source_cells:
  if row.original[1]!=-3 or row.allowed_flag!=0 or compatible_flags.has(int(row.order)):return false
  if not numbers(row.original,original.cells[int(row.order)]):return false
  compatible_flags[int(row.order)]=row.original
 return true
func matches_source(source:Dictionary,original:Dictionary)->bool:
 for key in ["id","width","height","sourceSha256"]:
  if source.get(key)!=original.get(key):return false
 if not source.get("cells") is Array or source.cells.size()!=10000:return false
 for i in 10000:
  if not source_cell_matches(source.cells[i],original.cells[i],i):return false
 return true
func source_cell_matches(actual,expected,order:int)->bool:
 if numbers(actual,expected):return true
 if not compatible_flags.has(order) or not numbers(expected,compatible_flags[order]):return false
 if not actual is Array or actual.size()!=4:return false
 for i in 4:
  if not integer(actual[i]) or actual[i]!=(0 if i==1 else expected[i]):return false
 return true
func integer(v)->bool:return (v is int or v is float) and is_finite(float(v)) and float(v)==floor(float(v))
func numbers(a,b)->bool:
 if not a is Array or a.size()!=b.size():return false
 for i in a.size():
  if not integer(a[i]) or float(a[i])!=float(b[i]):return false
 return true
