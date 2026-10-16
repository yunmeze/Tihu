extends Control
const Session=preload("res://scripts/session_adapter.gd")
const Core=preload("res://scripts/core/apothecary_purchase.gd")
var session=Session.new()
var panel:Control
var price:Label
var diagnostics:Label
var status:String="未交易"
func _ready()->void:
 texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
 var result=session.initialize()
 if not result.ok:
  _label(str(result),Vector2(20,20),Vector2(700,80));return
 _label("原资源布局参考 · 独立测试角色 · 非最终 HD 皮肤",Vector2(24,14),Vector2(710,26))
 _label("仅初始等级1普通战士／布衣／负重25；测试金币2000。\n面板全局(24,90)为诊断展示位置，并非已证原屏幕坐标。",Vector2(24,42),Vector2(710,44))
 panel=Control.new();panel.position=Vector2(24,90);panel.size=Vector2(329,147);add_child(panel)
 var background=TextureRect.new();background.texture=_texture("panel");background.size=panel.size;background.mouse_filter=Control.MOUSE_FILTER_IGNORE;panel.add_child(background)
 for i in 16:
  var slot=Button.new();slot.flat=true;slot.position=Vector2(26+35*(i%8),27+35*(i/8));slot.size=Vector2(32,32);slot.focus_mode=Control.FOCUS_NONE
  slot.add_theme_stylebox_override("normal",StyleBoxEmpty.new());slot.add_theme_stylebox_override("hover",StyleBoxEmpty.new());slot.add_theme_stylebox_override("pressed",StyleBoxEmpty.new())
  if i<Core.STOCK.size():
   var icon=TextureRect.new();icon.texture=_texture("item_"+str(Core.STOCK[i][0]));icon.size=Vector2(32,32);icon.mouse_filter=Control.MOUSE_FILTER_IGNORE;slot.add_child(icon)
   slot.tooltip_text=str(Core.STOCK[i][1])+" / "+str(Core.STOCK[i][2])+" 金币（诊断信息，非原Tooltip复刻）"
  slot.pressed.connect(select_slot.bind(i));panel.add_child(slot)
 var buy=TextureButton.new();buy.texture_normal=_texture("buy");buy.position=Vector2(236,105);buy.size=Vector2(67,21);buy.pressed.connect(purchase);panel.add_child(buy)
 # Price label is explicitly diagnostic until the original label bounds/font are decoded.
 price=_label("",Vector2(380,100),Vector2(350,65))
 diagnostics=_label("",Vector2(380,175),Vector2(350,100))
 var close=Button.new();close.text="关闭（诊断控件）";close.position=Vector2(24,250);close.pressed.connect(close_shop);add_child(close)
 var reopen=Button.new();reopen.text="重开独立商店";reopen.position=Vector2(215,250);reopen.pressed.connect(open_shop);add_child(reopen)
 # Display-only compatibility for source private-use indentation; source/script SHA stay unchanged.
 _label("原菜单文本参考：以下内容不交互，治疗尚未支持。\n"+session.reference_menu().replace("\ue810"," "),Vector2(24,305),Vector2(705,220))
 open_shop()
func _texture(name:String)->ImageTexture:
 return ImageTexture.create_from_image(Image.load_from_file("res://assets/"+name+".png"))
func _label(text:String,pos:Vector2,bounds:Vector2)->Label:
 var label=Label.new();label.text=text;label.position=pos;label.size=bounds;label.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;label.add_theme_font_size_override("font_size",14);add_child(label);return label
func select_slot(index:int)->void:
 session.select_slot(index);refresh()
func purchase()->void:
 var result=session.buy_selected();status="单件购买成功" if result.ok else "未交易："+str(result.get("error",result));refresh()
func close_shop()->void:
 session.close_shop();refresh()
func open_shop()->void:
 session.open_shop();refresh()
func refresh()->void:
 var snap=session.snapshot();panel.visible=snap.open
 print("OWNED_UI_STATE "+JSON.stringify(snap))
 price.text="诊断选择：无" if snap.selected<0 else "诊断选择："+str(Core.STOCK[snap.selected][1])+"\n售价："+str(Core.STOCK[snap.selected][2])+" 金币"
 diagnostics.text="金币：%d  独立实例：%d\n会话 revision：%d\n%s"%[snap.authority.character.gold,snap.authority.inventory.instances.size(),snap.revision,status]
