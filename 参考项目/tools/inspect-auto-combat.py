"""Read original controls/passive evidence and identify the requested Web policy."""
from pathlib import Path
import json,hashlib,re
root=Path(__file__).resolve().parent.parent
helpfile=root/'reference/LP传奇单机版-重生v1.2.2E/Help/Game_Index.htm'
data=helpfile.read_bytes();plain=re.sub(r'\s+',' ',re.sub('<[^>]*>',' ',data.decode('utf-8')))
assert all(x in plain for x in ['F1','F8 自定义技能键','数字1 - 6 自定义恢复道具快捷键','单次/持续物理攻击'])
extended=json.loads((root/'reports/native-extended-combat-source.json').read_text(encoding='utf-8'))
permanent=json.loads((root/'public/assets/data/permanent.json').read_text(encoding='utf-8'))
report={
 'passed':True,'sourceExeSha256':extended['exeSha256'],
 'sourceHelp':helpfile.relative_to(root).as_posix(),'sourceHelpSha256':hashlib.sha256(data).hexdigest(),
 'originalInput':{'physicalAttack':'player left click/hold for single/continuous physical attack','activeSkills':'player-defined F1-F8 skill keys','restorationSlots':6,'lockingInsights':[r for r in permanent['insights'] if r['name'].startswith('仇恨记忆')]},
 'originalPassives':['基本剑术','剑气斩','火龙斩','自然之力'],
 'sourcePassiveRules':{k:extended['remainingSkills'][k] for k in ['basicSwordHit','swordEnergy','fireDragon','naturalPower']},
 'portraitAdaptation':{'origin':'explicit user request; automatic multi-skill policy rather than native player input','activeSlots':6,'beltSlots':6,'skillActivationFromSkillPage':True,'HUDEnabledToggles':True,'passivesExcluded':True,'removeToFreeConfiguredSlot':True,'legacySelectionAndHotkeysMigratedOnce':True,'skillAndBeltKeyBindingsRemoved':True,
 'rules':['critical healing before summons; moderate healing when no healing pool','refill learned summons to native per-kind/totals with reachable spawn placement','shield only when absent; invisibility only without an attack target/threat','ranged attacks at a distant target; melee at contact; valid MP/range/line of sight','area spells for clustered targets; cheaper single-target spells when isolated','poison/corrosion/firewall not repeatedly cast while already applied','temptation uses native eligibility and two-second retry policy','refine a nearby corpse after combat when not already walking to loot','manual paths and loot walk take priority over utility casts; UI/background pause via existing game loop'],'nativeSkillManaPowersTimingAndEffectsUnchanged':True},
 'wechatDeviceTested':False,'fullNativeEquivalent':False,
}
(root/'reports/native-auto-combat-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print({'originalControlsVerified':True,'helpSha256':report['sourceHelpSha256'],'activeSlots':6,'beltSlots':6})
