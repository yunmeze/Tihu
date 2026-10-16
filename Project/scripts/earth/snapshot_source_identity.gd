extends RefCounted
# Metadata/NPC changes do not prove geometry. Unknown changed geometry fails closed.
static func compatible(source:Dictionary,original:Dictionary) -> bool:
	for key in ["id","width","height","sourceSha256"]:
		if source.get(key)!=original.get(key):return false
	if not source.get("cells") is Array or not original.get("cells") is Array or source.cells.size()!=10000 or original.cells.size()!=10000:return false
	for i in 10000:
		var a=source.cells[i];var b=original.cells[i]
		if not a is Array or a.size()!=4 or a[0]!=b[0] or a[2]!=b[2] or a[3]!=b[3]:return false
	return true
