import {followingPet} from './allies.js';
const FIELDS=['hp','attack','defense','magicDefense','regenFrames','attackFrames','appearance','speed','vision','attackKind','behavior'];
export const validStatuses=state=>Object.fromEntries(Object.entries(state||{}).filter(([name,s])=>['freeze','burn','poison','paralysis','corrosion'].includes(name)&&s&&s.frames>0&&s.frames<=100000&&Number.isFinite(s.power)&&s.power>0&&s.power<=100000).map(([name,s])=>[name,{frames:Math.trunc(s.frames),power:s.power,source:typeof s.source==='string'?s.source:'player'}]));
export function savePets(units=[]){return units.filter(u=>u.alive&&followingPet(u)).slice(0,3).map(u=>({monsterId:u.monsterId,hp:u.hp,summonSkill:u.summonSkill,petLevel:u.petLevel||1,petKills:u.petKills||0,healingPool:u.healingPool||0,statuses:validStatuses(u.statuses),originId:u.originId,stats:Object.fromEntries(FIELDS.map(k=>[k,u.definition[k]]))}));}
export function restorePets(state,content){
 const pets=[];for(const s of Array.isArray(state)?state:[]){const base=content.monsters[s?.monsterId];if(pets.length===3)break;if(!base||base.name==='0'||!(s.hp>0)||!['召唤骷髅','召唤神兽','诱惑之光','江湖召唤'].includes(s.summonSkill))continue;if(!['诱惑之光','江湖召唤'].includes(s.summonSkill)&&base.name!==s.summonSkill)continue;
  const definition={...base};for(const k of FIELDS)if(Number.isFinite(s.stats?.[k])&&s.stats[k]>=0&&s.stats[k]<=10000000)definition[k]=s.stats[k];
  const appearances=s.summonSkill==='召唤骷髅'?[base.appearance,200]:s.summonSkill==='召唤神兽'?[base.appearance,174]:[base.appearance];if(!appearances.includes(definition.appearance))definition.appearance=base.appearance;
  if(s.summonSkill==='召唤神兽'&&pets.some(p=>p.summonSkill===s.summonSkill)||s.summonSkill==='召唤骷髅'&&pets.filter(p=>p.summonSkill===s.summonSkill).length>=2)continue;
  pets.push({definition,monsterId:base.id,hp:Math.min(s.hp,definition.hp),alive:true,summoned:true,summonSkill:s.summonSkill,petLevel:Math.max(1,Math.min(10,Math.trunc(s.petLevel)||1)),petKills:Math.max(0,Math.min(100000,Math.trunc(s.petKills)||0)),healingPool:Math.max(0,Math.min(100000,Math.trunc(s.healingPool)||0)),statuses:validStatuses(s.statuses),originId:typeof s.originId==='string'?s.originId:undefined});
 }return pets;
}
