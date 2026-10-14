using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using UnityEditor;
using UnityEngine;
using UnityEngine.UIElements;
public sealed class OriginalUIBakeWindow : EditorWindow {}
public static class UIBake {
 [Serializable] public class Element {public string name,type,text,image,bgMode;public string[] classes;public float x,y,w,h,fontSize,letterSpacing,opacity,sl,sr,st,sb,sliceScale;public Color color,background,tint;public string align,overflow;public int parent;public bool visible;}
 [Serializable] public class Zone {public string _displayName;public int _progressKillGoal,_itemVisualTier,_itemLevelFloor,_itemLevelCap;}
 [Serializable] public class Data {public Zone[] zones;}
 [Serializable] public class Layout {public string name;public Element[] elements;}
 [Serializable] public class Collection {public Layout[] layouts,chineseLayouts;}
 [Serializable] public class Pair {public string source,target;}
 [Serializable] public class Translations {public Pair[] pairs;}
 [Serializable] public class WindowTexts {public string name;public Pair[] texts;}
 [Serializable] public class LocaleBindings {public WindowTexts[] windows;}
 [Serializable] public class Bindings {public LocaleBindings en;public LocaleBindings zh;}
 [Serializable] public class HeroRow {public string group,name,value;}
 [Serializable] public class HeroRows {public HeroRow[] rows;}
 static OriginalUIBakeWindow window;static int frames;
 static readonly string[] names={"FarmWindow","InventoryWindow","LootReviewInventoryWindow","SkillTreeWindow","ZoneWindow","SettingsWindow","CombatSkillsWindow","DifficultyWindow","LootFilterWindow","SkillNodeCard","ZoneRow","DifficultyCard"};
 public static void Run(){AssetDatabase.Refresh();EditorApplication.delayCall+=Begin;}
 static void Begin(){window=ScriptableObject.CreateInstance<OriginalUIBakeWindow>();window.position=new Rect(0,0,640,960);window.Show();EditorApplication.update+=Wait;}
 static void Wait(){if(++frames<20)return;EditorApplication.update-=Wait;try{Bake();window.Close();EditorApplication.Exit(0);}catch(Exception e){Debug.LogException(e);window.Close();EditorApplication.Exit(1);}}
 static void Bake(){
  var english=BakeLocale(false);var chinese=BakeLocale(true);
  File.WriteAllText(Path.GetFullPath(Path.Combine(Application.dataPath,"../../../public/assets/ui/native-layout.json")),JsonUtility.ToJson(new Collection{layouts=Array.FindAll(english,l=>!l.name.StartsWith("Review")&&l.name!="HeroFullWindow"),chineseLayouts=Array.FindAll(chinese,l=>!l.name.StartsWith("Review")&&l.name!="HeroFullWindow")}));
  File.WriteAllText(Path.GetFullPath(Path.Combine(Application.dataPath,"../../../public/assets/ui/progression-layout.json")),JsonUtility.ToJson(new Collection{layouts=Array.FindAll(english,l=>l.name.StartsWith("Review")||l.name=="HeroFullWindow"),chineseLayouts=Array.FindAll(chinese,l=>l.name.StartsWith("Review")||l.name=="HeroFullWindow")}));
 }
 static Layout[] BakeLocale(bool chinese){
  var result=new List<Layout>();var translations=new Dictionary<string,string>();
  string bindingText=File.ReadAllText(Path.GetFullPath(Path.Combine(Application.dataPath,"../../../.tools/ui-bindings.json"))).Replace("\"zh-CN\":","\"zh\":");
  var allBindings=JsonUtility.FromJson<Bindings>(bindingText);var bindings=chinese?allBindings.zh:allBindings.en;
  if(chinese){foreach(var pair in JsonUtility.FromJson<Translations>(File.ReadAllText(Path.GetFullPath(Path.Combine(Application.dataPath,"../../../.tools/i18n-ui.json")))).pairs)translations[pair.source]=pair.target;}
  var jobs=new List<string>(names);jobs.Add("HeroInventoryWindow");jobs.Add("HeroFullWindow");for(int n=1;n<=12;n++)jobs.Add("Review"+n);
  foreach(string name in jobs){
   var root=window.rootVisualElement;root.Clear();root.style.width=640;root.style.height=960;root.style.flexDirection=FlexDirection.Column;
   var asset=AssetDatabase.LoadAssetAtPath<VisualTreeAsset>("Assets/OriginalUI/"+(name=="HeroInventoryWindow"||name=="HeroFullWindow"||name.StartsWith("Review")?"LootReviewInventoryWindow":name)+".uxml");if(asset==null)throw new Exception("Missing tree "+name);asset.CloneTree(root);
   if(name=="HeroInventoryWindow"||name=="HeroFullWindow"){
    root.Q("EquipmentGrid").AddToClassList("loot-review-side-panel-hidden");root.Q("HeroStatsPanel").RemoveFromClassList("loot-review-side-panel-hidden");root.Q("HeroStatsPanel").style.display=DisplayStyle.Flex;
    var rows=JsonUtility.FromJson<HeroRows>(File.ReadAllText(Path.GetFullPath(Path.Combine(Application.dataPath,name=="HeroFullWindow"?"../../../.tools/hero-full-ui.json":"../../../.tools/hero-ui.json"))));
    var rowTemplate=AssetDatabase.LoadAssetAtPath<VisualTreeAsset>("Assets/OriginalUI/LootReviewHeroStatRow.uxml");var groupTemplate=AssetDatabase.LoadAssetAtPath<VisualTreeAsset>("Assets/OriginalUI/LootReviewHeroStatGroupHeader.uxml");
    foreach(var data in rows.rows){if(data.group!=""){var group=groupTemplate.CloneTree().Q("HeroStatGroupHeader");group.RemoveFromHierarchy();group.Q<Label>("HeroStatGroupName").text=data.group;root.Q("HeroStatsList").Add(group);}var row=rowTemplate.CloneTree().Q("HeroStatRow");row.RemoveFromHierarchy();row.Q<Label>("HeroStatName").text=data.name;row.Q<Label>("HeroStatValue").text=data.value;root.Q("HeroStatsList").Add(row);}
   }
   if(name.StartsWith("Review")){
    int count=int.Parse(name.Substring(6));root.Q<Label>("CardTitleText").text=chinese?"腐朽战斧":"Rotten Longaxe";
    foreach(string key in new[]{"CardMetaText","CardPowerText"}){var label=root.Q<Label>(key);label.style.display=DisplayStyle.Flex;label.text=key=="CardMetaText"?(chinese?"稀有 武器":"Rare Weapon"):(chinese?"战力 42":"Power 42");}
    for(int n=0;n<12;n++){var row=root.Q("StatRow"+n);row.style.display=n<count?DisplayStyle.Flex:DisplayStyle.None;if(n<count){root.Q<Label>("StatName"+n).text=chinese?"伤害 10 (+3)":"Damage 10 (+3)";if(n<3)root.Q("StatName"+n).AddToClassList("loot-review-card-flow-icon-inset");}}
   }
   if(name=="FarmWindow"){
    var button=AssetDatabase.LoadAssetAtPath<VisualTreeAsset>("Assets/OriginalUI/ToolbarButton.uxml");
    string[] upper={"Inventory","Skills","Combat"},lower={"Zones","LootFilter","Difficulty","Settings"};
    foreach(string id in upper)AddToolbar(button,root.Q("FarmToolbarUpperRow"),id);
    foreach(string id in lower)AddToolbar(button,root.Q("FarmToolbarLowerRow"),id);
    root.Q("PlayerHealthLiquidClip").style.height=118;
    root.Q("EnemyHealthModule").style.left=218;
    root.Q("EnemyHealthModule").style.width=204;root.Q("EnemyHealthModule").style.flexShrink=0;
   }
   if(name=="CombatSkillsWindow")root.Q<Label>("TitleLabel").text="Combat Skills";
   if(name=="ZoneWindow"){
    var data=JsonUtility.FromJson<Data>(File.ReadAllText(Path.GetFullPath(Path.Combine(Application.dataPath,"../../../.tools/ui-data.json"))));
    var template=AssetDatabase.LoadAssetAtPath<VisualTreeAsset>("Assets/OriginalUI/ZoneRow.uxml");int i=0;
    foreach(var z in data.zones){var row=template.CloneTree().Q("ZoneRowRoot");row.RemoveFromHierarchy();row.name="zone-"+(i++);row.Q<Label>("ZoneName").text=z._displayName;row.Q<Label>("ZoneStatus").text="0 / "+z._progressKillGoal;row.Q<Label>("ZoneLoot").text="Tier "+z._itemVisualTier+" visuals, ilvl "+z._itemLevelFloor+"-"+z._itemLevelCap;root.Q("ZoneList").Add(row);}
   }
   if(name!="FarmWindow"){var panel=root.Q<VisualElement>(className:"management-window");if(panel!=null){panel.style.position=Position.Absolute;panel.style.left=0;panel.style.top=0;panel.style.width=640;panel.style.height=480;}}
   foreach(var binding in bindings.windows)if(binding.name==name)foreach(var pair in binding.texts){string[] path=pair.source.Split('/');VisualElement parent=path.Length==2?root.Q(path[0]):root;var text=parent?.Q<TextElement>(path[path.Length-1]);if(text!=null)text.text=pair.target;}
   if(chinese){var font=AssetDatabase.LoadAssetAtPath<Font>("Assets/OriginalUI/Chinese.ttf");foreach(var v in root.Query<VisualElement>().ToList()){if(v is TextElement text&&translations.TryGetValue(text.text,out var value))text.text=value;if(v is Toggle toggle&&translations.TryGetValue(toggle.label??"",out var label))toggle.label=label;v.style.unityFont=font;v.style.unityFontDefinition=FontDefinition.FromFont(font);}}
   var p=root.panel;if(p==null)throw new Exception("No native layout panel");var meth=p.GetType().GetMethod("ValidateLayout",BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic);if(meth==null)throw new Exception("ValidateLayout unavailable");meth.Invoke(p,null);
   var elements=new List<Element>();Collect(root,root,elements,-1,true);result.Add(new Layout{name=name,elements=elements.ToArray()});Debug.Log("LAYOUT "+name+" "+elements.Count+" elements");
   if(name=="SkillTreeWindow"){
    var tooltip=root.Q("SkillTreeTooltip");tooltip.style.display=DisplayStyle.Flex;tooltip.Q<Label>("SkillTreeTooltipTitle").text=chinese?"伤害":"Damage";tooltip.Q<Label>("SkillTreeTooltipDescription").text=chinese?"+10% 伤害":"+10% Damage";tooltip.Q<Label>("SkillTreeTooltipPrice").text=chinese?"价格：75":"Price: 75";meth.Invoke(p,null);var values=new List<Element>();Collect(tooltip,tooltip,values,-1,true);result.Add(new Layout{name="SkillTooltip",elements=values.ToArray()});
   }
  }
  return result.ToArray();
 }
 static void AddToolbar(VisualTreeAsset asset,VisualElement row,string id){var container=asset.CloneTree();container.style.flexShrink=0;container.style.flexGrow=0;container.name="toolbar-"+id;row.Add(container);}
 static void Collect(VisualElement v,VisualElement root,List<Element> list,int parent,bool displayed){
  var s=v.resolvedStyle;displayed=displayed&&s.display!=DisplayStyle.None&&s.visibility==Visibility.Visible;var b=v.worldBound;var o=root.worldBound;var image=s.backgroundImage;var texture=image.texture!=null?image.texture.name:image.sprite!=null?image.sprite.name:"";
  var classes=new List<string>(v.GetClasses());
  string overflow=v.style.overflow.value.ToString();if(v.name=="FarmWindowHudPanel"||v.name=="SkillTreeViewport"||v is ScrollView||classes.Contains("unity-scroll-view__content-viewport")||classes.Contains("difficulty-body"))overflow="Hidden";
  int id=list.Count;list.Add(new Element{name=v.name,type=v.GetType().Name,text=v is TextElement t?t.text:"",image=texture,bgMode=s.backgroundSize.sizeType.ToString(),classes=classes.ToArray(),x=b.x-o.x,y=b.y-o.y,w=b.width,h=b.height,fontSize=s.fontSize,letterSpacing=s.letterSpacing,opacity=s.opacity,color=s.color,background=s.backgroundColor,tint=s.unityBackgroundImageTintColor,sl=s.unitySliceLeft,sr=s.unitySliceRight,st=s.unitySliceTop,sb=s.unitySliceBottom,sliceScale=s.unitySliceScale,align=s.unityTextAlign.ToString(),overflow=overflow,parent=parent,visible=displayed});
  for(int n=0;n<v.hierarchy.childCount;n++)Collect(v.hierarchy[n],root,list,id,displayed);
 }
}

