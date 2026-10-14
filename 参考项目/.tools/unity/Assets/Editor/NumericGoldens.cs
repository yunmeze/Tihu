using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
[Serializable]public class ItemAffix {public ItemStatRoll Stat;}
[Serializable]public class ItemInstance {public string ItemId;public List<ItemStatRoll> BaseStats;public List<ItemAffix> Affixes;}
[Serializable]public class EquipmentState {public ItemInstance Weapon,Helmet,Armor,Ring,Trinket;}
[Serializable]public class BalanceSettings {public float LevelDamagePercent,LevelMaxHealthPercent,HeroBaseHealthRegen;}
public static class BalanceSettingsService {public static BalanceSettings Current;}
public static class NumericGoldens {
 [Serializable]public class Case {public PlayerStatsComponent hero;public EquipmentState nativeEquipment;public SkillTreeBonusState bonus;public int level;}
 [Serializable]public class Cases {public Case[] cases;public BalanceSettings balance;}
 [Serializable]public class Output {public PlayerStatsComponent[] stats;}
 public static void Run(){var root=Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));var data=JsonUtility.FromJson<Cases>(File.ReadAllText(Path.Combine(root,".tools/numeric-cases.json")));BalanceSettingsService.Current=data.balance;var list=new List<PlayerStatsComponent>();foreach(var c in data.cases){var stats=c.hero;GoldenHeroStatsService.Recalculate(ref stats,c.nativeEquipment,c.bonus,c.level);list.Add(stats);}File.WriteAllText(Path.Combine(root,"reports/numeric-native-goldens.json"),JsonUtility.ToJson(new Output{stats=list.ToArray()}));Debug.Log("NUMERIC GOLDENS "+list.Count);EditorApplication.Exit(0);}
}
