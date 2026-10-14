import {PASSIVE_SKILLS} from './skill-roles.js';
import {classAllowsSkill} from './skill-classes.js';
export const AUTO_SKILL_LIMIT=6,AUTO_SKILL_MODEL='six-slot-v1';
export function autoSkillAllowed(player,content,name){const r=content.skills.records.find(r=>r.name===name);return !PASSIVE_SKILLS.has(name)&&classAllowsSkill(r,player.class)&&player.skills.some(s=>s.name===name&&s.level>0);}
export function normalizeAutoSkills(player,content){
 const source=Array.isArray(player.autoSkills)?player.autoSkills:[player.activeSkill,...(player.skillHotkeys||[])].filter(Boolean).map(name=>({name,enabled:true})),seen=new Set();
 player.autoSkills=source.filter(e=>e&&autoSkillAllowed(player,content,e.name)&&!seen.has(e.name)&&seen.add(e.name)).slice(0,AUTO_SKILL_LIMIT).map(e=>({name:e.name,enabled:e.enabled!==false}));player.autoSkillModel=AUTO_SKILL_MODEL;delete player.skillHotkeys;return player;
}
export const autoSkillMode=player=>player.autoSkillModel===AUTO_SKILL_MODEL;
export function activateAutoSkill(player,content,name){
 normalizeAutoSkills(player,content);if(!autoSkillAllowed(player,content,name))return {ok:false,reason:PASSIVE_SKILLS.has(name)?'被动技能自动生效':'尚未学会此职业技能'};
 const entry=player.autoSkills.find(e=>e.name===name);if(entry){entry.enabled=true;return {ok:true};}if(player.autoSkills.length>=AUTO_SKILL_LIMIT)return {ok:false,reason:'最多激活6个主动技能'};player.autoSkills.push({name,enabled:true});return {ok:true};
}
export function toggleAutoSkill(player,name){const entry=player.autoSkills?.find(e=>e.name===name);if(!entry)return false;entry.enabled=!entry.enabled;return true;}
export function removeAutoSkill(player,name){const before=player.autoSkills?.length||0;player.autoSkills=(player.autoSkills||[]).filter(e=>e.name!==name);return before!==player.autoSkills.length;}
