extends RefCounted
const Core=preload("res://scripts/core/apothecary_purchase.gd")
const Profile=preload("res://scripts/core/default_warrior.gd")
var _authority:Dictionary={}
var _records:Array=[]
var _source:Dictionary={}
var _revision:int=0
var _open:bool=false
var _selected:int=-1
func initialize()->Dictionary:
 _records=JSON.parse_string(FileAccess.get_file_as_string("res://data/records.json"))
 _source=JSON.parse_string(FileAccess.get_file_as_string("res://data/source.json"))
 var rules=Core.adapt_catalogue(_records)
 if not rules.ok:return rules
 if _source.map_id!="A13" or _source.source_index!=2:return Core.fail("invalid_source")
 var created=Profile.create("owned-shop",_records[0],Core.POLICY)
 if not created.ok:return created
 _authority=created.state
 # Explicit test purse only, never read/publish a game save.
 _authority.character.gold=2000
 if not Core.valid_context(_context(),_authority.inventory.revision):return Core.fail("invalid_source")
 var names:Array=[]
 var reading:bool=false
 for line in str(_source.record.script).replace("\r","").split("\n"):
  if line.to_lower()=="#buy":reading=true;continue
  if line.to_lower()=="#endbuy":break
  if reading:names.append(line)
 if names.size()!=Core.STOCK.size():return Core.fail("invalid_stock")
 for i in names.size():
  if names[i]!=Core.STOCK[i][1]:return Core.fail("invalid_stock")
 return {"ok":true}
func open_shop()->void:
 _revision+=1;_open=true;_selected=-1
func close_shop()->void:
 _revision+=1;_open=false;_selected=-1
func select_slot(index:int)->void:
 _selected=index if _open and index>=0 and index<Core.STOCK.size() else -1
func prepare_selected()->Dictionary:
 if not _open:return Core.fail("shop_closed")
 if _selected<0:return Core.fail("no_selection")
 return Core.prepare(_authority,_records,_context(),{"item_id":str(Core.STOCK[_selected][0])})
func commit_ticket(ticket:Dictionary)->Dictionary:
 if not _open:return Core.fail("shop_closed")
 var result=Core.commit(_authority,_records,_context(),ticket)
 if result.ok:
  _authority=result.authority;_revision=result.next_conversation_revision
 return result
func buy_selected()->Dictionary:
 var prepared=prepare_selected()
 if not prepared.ok:return prepared
 return commit_ticket(prepared.ticket)
func snapshot()->Dictionary:
 return {"authority":_authority.duplicate(true),"revision":_revision,"open":_open,"selected":_selected}
func reference_menu()->String:
 var text:String=str(_source.record.script).replace("\r","")
 return text.substr(text.find("#endbuy")+7).split("#end")[0]
func _context()->Dictionary:
 return {"map_id":_source.map_id,"source_index":2,"record":_source.record.duplicate(true),"script_sha":str(_source.record.script).sha256_text(),"world":1,"epoch":1,"conversation_revision":_revision,"inventory_revision":_authority.inventory.revision}
