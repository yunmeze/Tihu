import {instanceItem} from './native-stats.js';
import {effectPack,impactType,MONSTER_EFFECTS} from './projectiles.js';
const skills={'基本剑术':[1],'剑气斩':[2],'火龙斩':[1,72],'半月斩':[3],'烈火斩':[4],'冰封斩':[5],'自然之力':[1],'灵魂火符':[6,28],'回生术':[7],'治愈术':[8],'隐身术':[9],'召唤骷髅':[12],'召唤神兽':[13],'施毒术':[10],'侵蚀术':[11],'火球术':[14,24],'爆裂火球':[15,25],'雷电术':[18,56],'火墙':[19],'魔法盾':[21],'御冰术':[16,26],'地狱雷光':[90],'强冰术':[17,27],'冰咆哮':[20],'诱惑之光':[22],'炼尸咒':[91]};
export function neededEffectPacks(player,units=[],effects=[],content){
 const types=new Set([1]),names=new Set((player.autoSkills||[]).map(e=>e.name));if(player.activeSkill)names.add(player.activeSkill);for(const name of ['剑气斩','火龙斩'])if(player.skills?.some(s=>s.name===name&&s.level>0))names.add(name);
 for(const name of names)for(const t of skills[name]||[])types.add(t);
 const attached=instanceItem(content?.items[player.equipment?.weapon],player.equipmentMeta?.weapon)?.rawFields?.[30];for(const type of attached===18?[18,56]:attached===19?[19]:attached===20?[20]:[])types.add(type);
 if(player.magicShieldFrames>0)types.add(21);
 for(const u of units){const k=u.definition.attackKind,t=MONSTER_EFFECTS[k];if(t){types.add(t);types.add(impactType(t));}for(const type of k===21||k===22?[46,47,48,49]:k===23?[48,26]:k===24?[46,47,24,25]:k===25?[37]:k===26?[38]:k===27?[39,47,25]:k===28?[47,49,25,27,40]:[])types.add(type);}
 const packs=new Set([...types].map(t=>effectPack(t)).filter(Boolean));for(const e of effects){const p=effectPack(e.type,e.variant);if(p)packs.add(p);}if(names.has('雷电术')&&player.skills?.some(s=>s.name==='雷电术'&&s.level>=5))packs.add(effectPack(18,'lightningWide'));return packs;
}
