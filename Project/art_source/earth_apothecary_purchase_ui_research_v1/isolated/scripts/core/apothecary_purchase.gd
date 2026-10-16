extends RefCounted
## Isolated single-item purchase. No I/O, UI, NPC entry point, healing, or save changes.
## Trusted session owner supplies CURRENT context; never accept it from a UI payload.
const Inventory=preload("res://scripts/core/inventory_state.gd")
const Profile=preload("res://scripts/core/default_warrior.gd")
const SCRIPT_SHA="78fdc3d3044ef40d2d7de1cb36804de64349131d22e3c9036391b723db3ae2ad"
const POLICY={"max_weight":25,"equipment_slots":["helmet","necklace","armor","boots","braceletLeft","braceletRight","ringLeft","ringRight","shield","weapon"],"weight_locations":["bag","equipment"]}
# ID, exact name, price, weight, type, icon, HP, MP. Other source raw words are zero.
const STOCK=[
 [3,"强效金创药",35,1,3,9,80,0],[4,"绝强金创药",60,1,3,10,110,0],
 [42,"精炼金创药",120,2,3,76,150,0],[8,"强效魔法药",30,1,3,16,0,100],
 [9,"绝强魔法药",55,1,3,17,0,130],[44,"精炼魔法药",110,2,3,77,0,180],
 [13,"强效金创药包",210,7,6,23,0,0],[14,"绝强金创药包",360,7,6,24,0,0],
 [18,"强效魔法药包",180,7,6,30,0,0],[19,"绝强魔法药包",330,7,6,31,0,0],
 [43,"精炼金创药包",760,12,6,101,0,0],[45,"精炼魔法药包",660,12,6,108,0,0]]
const CONTEXT_KEYS=["map_id","source_index","record","script_sha","world","epoch","conversation_revision","inventory_revision"]

static func prepare(authority:Variant,records:Variant,context:Variant,intent:Variant)->Dictionary:
 if not shape(intent,["item_id"]) or typeof(intent.item_id)!=TYPE_STRING:return fail("invalid_intent")
 var rules=adapt_catalogue(records)
 if not rules.ok:return rules
 if not rules.prices.has(intent.item_id):return fail("not_in_stock")
 var checked=validate_authority(authority,rules)
 if not checked.ok:return checked
 if not valid_context(context,checked.inventory.revision):return fail("invalid_context")
 # Original failure precedence for a well-formed source/state: slot, load, gold.
 if checked.inventory.bag_slots.find(null)<0:return fail("bag_full")
 var weight:int=rules.catalogue[intent.item_id].weight
 if checked.total_weight>25-weight:return fail("weight_limit")
 var price:int=rules.prices[intent.item_id]
 if authority.character.gold<price:return fail("insufficient_gold")
 var action={"type":"acquire","item_id":intent.item_id,
  "properties":{"raw_proficiency":null,"weight":null},
  "provenance":{"grant":"a13_source2_purchase_one","script_sha":SCRIPT_SHA,"source_record":2}}
 var staged=Inventory.stage(checked.inventory,action,rules.catalogue,POLICY,checked.inventory.revision)
 if not staged.ok:return staged
 var bought=Inventory.commit(checked.inventory,staged.transaction,rules.catalogue,POLICY)
 if not bought.ok:return bought
 var candidate:Dictionary=authority.duplicate(true)
 candidate.inventory=bought.inventory
 candidate.character.gold-=price
 var final_check=validate_authority(candidate,rules)
 if not final_check.ok:return final_check
 var ticket={"base_authority":authority.duplicate(true),"context":context.duplicate(true),
  "intent":intent.duplicate(true),"catalogue_stamp":rules.stamp,"candidate":candidate,
  "instance_id":bought.instance_id}
 freeze(ticket)
 return {"ok":true,"ticket":ticket}

static func commit(current_authority:Variant,records:Variant,current_context:Variant,ticket:Variant)->Dictionary:
 if not shape(ticket,["base_authority","context","intent","catalogue_stamp","candidate","instance_id"]):return fail("invalid_ticket")
 # Guard bounded JSON before deep comparisons; never recurse into untrusted cycles.
 if not Profile._bounded(ticket,0,[0]):return fail("invalid_ticket")
 if not Profile._bounded(current_authority,0,[0]) or not Profile._bounded(current_context,0,[0]):return fail("invalid_current_state")
 if current_authority!=ticket.base_authority or current_context!=ticket.context:return fail("stale_ticket")
 var replay=prepare(current_authority,records,current_context,ticket.intent)
 if not replay.ok:return replay
 if replay.ticket!=ticket:return fail("ticket_mismatch")
 return {"ok":true,"authority":replay.ticket.candidate.duplicate(true),
  "instance_id":replay.ticket.instance_id,"next_conversation_revision":int(current_context.conversation_revision)+1}

static func adapt_catalogue(records:Variant)->Dictionary:
 if not Profile._bounded(records,0,[0]) or typeof(records)!=TYPE_ARRAY or records.size()!=13:return fail("unsupported_catalogue")
 var by_id={}
 for record in records:
  if typeof(record)!=TYPE_DICTIONARY or not exact_int(record.get("id"),0,719):return fail("invalid_template")
  var id=str(int(record.id))
  if by_id.has(id):return fail("duplicate_template")
  by_id[id]=record
 if not by_id.has("252"):return fail("missing_cloth")
 var cloth=Profile.adapt_cloth(by_id["252"])
 if not cloth.ok:return cloth
 var catalogue:Dictionary=cloth.catalogue.duplicate(true)
 var prices={}
 for row in STOCK:
  var id=str(row[0])
  if not by_id.has(id):return fail("missing_stock_template")
  var record:Dictionary=by_id[id]
  if record.get("name")!=row[1]:return fail("template_mismatch")
  for pair in [["price",2],["weight",3],["type",4],["icon",5],["hp",6],["mp",7]]:
   if not exact_int(record.get(pair[0]),row[pair[1]],row[pair[1]]):return fail("template_mismatch")
  if typeof(record.get("rawFields"))!=TYPE_ARRAY or record.rawFields.size()!=39:return fail("template_mismatch")
  for i in 39:
   var expected:int={0:row[4],1:row[5],4:row[6],5:row[7],38:row[3]}.get(i,0)
   if not exact_int(record.rawFields[i],expected,expected):return fail("template_mismatch")
  # Purchase-only catalogue: generic consume is not authorized by this API.
  catalogue[id]={"weight":row[3],"equipment_slots":[],"consumable":false}
  prices[id]=row[2]
 var result={"ok":true,"catalogue":catalogue,"prices":prices,"cloth":by_id["252"].duplicate(true),"stamp":JSON.stringify([catalogue,prices]).sha256_text()}
 freeze(result)
 return result

static func validate_authority(authority:Variant,rules:Dictionary)->Dictionary:
 if not Profile._bounded(authority,0,[0]) or not shape(authority,Profile.STATE_KEYS):return fail("invalid_authority")
 var inventory=Inventory.validate(authority.inventory,rules.catalogue,POLICY)
 if not inventory.ok:return inventory
 var inv:Dictionary=inventory.inventory
 if not inv.recovery_ids.is_empty():return fail("unsupported_carry_location")
 # Every instance is located exactly once by Inventory.validate, including equipment.
 # No unknown equipment/overrides may be silently omitted from weight calculation.
 var armor:Variant=inv.equipment_slots.armor
 if armor==null or inv.instances[armor].item_id!="252":return fail("unsupported_equipment")
 for slot in inv.equipment_slots:
  if slot!="armor" and inv.equipment_slots[slot]!=null:return fail("unsupported_equipment")
 for id in inv.instances:
  var item:Dictionary=inv.instances[id]
  if item.item_id=="252" and id!=armor:return fail("unsupported_cloth_location")
  if item.properties.weight!=null and item.properties.weight!=rules.catalogue[item.item_id].weight:return fail("unsupported_weight_override")
  if item.item_id!="252" and item.properties.raw_proficiency!=null:return fail("unsupported_potion_properties")
 # Explicit 13-template adapter: validate complete inventory first, then use the
 # unchanged original cloth-only profile solely to validate non-inventory fields.
 # This detached projection is never returned or published as player inventory.
 var projected:Dictionary=authority.duplicate(true)
 projected.inventory=inv.duplicate(true)
 for id in inv.instances:
  if id!=armor:projected.inventory.instances.erase(id)
 projected.inventory.bag_slots.fill(null)
 var profile=Profile.project(projected,rules.cloth,POLICY)
 if not profile.ok:return profile
 var initial=Profile.create("apothecary-validation",rules.cloth,POLICY)
 if not initial.ok:return initial
 var c:Dictionary=authority.character
 var baseline:Dictionary=initial.state.character
 for key in baseline:
  if key not in ["name","gold","hp","mp"] and c[key]!=baseline[key]:return fail("unsupported_character_profile")
 return {"ok":true,"inventory":inv,"total_weight":inventory.total_weight}

static func valid_context(c:Variant,inventory_revision:int)->bool:
 if not Profile._bounded(c,0,[0]) or not shape(c,CONTEXT_KEYS):return false
 if c.map_id!="A13" or typeof(c.source_index)!=TYPE_INT or c.source_index!=2 or c.script_sha!=SCRIPT_SHA:return false
 for key in ["world","epoch","conversation_revision","inventory_revision"]:
  if typeof(c[key])!=TYPE_INT or c[key]<0 or c[key]>=Inventory.MAX_INTEGER:return false
 if c.world==0 or c.inventory_revision!=inventory_revision:return false
 var r:Variant=c.record
 if not shape(r,["x","y","appearance","direction","name","script"]):return false
 if r.name!="老药师" or typeof(r.script)!=TYPE_STRING or r.script.sha256_text()!=SCRIPT_SHA:return false
 for pair in [["x",20],["y",26],["appearance",2],["direction",2]]:
  if not exact_int(r[pair[0]],pair[1],pair[1]):return false
 return true

static func exact_int(v:Variant,low:int,high:int)->bool:
 return typeof(v) in [TYPE_INT,TYPE_FLOAT] and is_finite(float(v)) and v==floor(float(v)) and v>=low and v<=high
static func shape(v:Variant,keys:Array)->bool:
 return typeof(v)==TYPE_DICTIONARY and v.size()==keys.size() and v.has_all(keys)
static func freeze(v:Variant)->void:
 if v is Dictionary:
  for child in v.values():freeze(child)
  v.make_read_only()
 elif v is Array:
  for child in v:freeze(child)
  v.make_read_only()
static func fail(code:String)->Dictionary:return {"ok":false,"error":code}
