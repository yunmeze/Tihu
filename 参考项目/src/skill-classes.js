// The native learning handlers explicitly reject other jobs for 19 skills.
// The remaining seven are shared, including the two NPC-acquired skills.
export const classAllowsSkill=(record,job)=>!!record&&(!record.classes||record.classes.includes(job));
export const classSkillRecords=(content,job)=>content.skills.records.filter(r=>classAllowsSkill(r,job));
// NPC/quest skills are discovered by learning them, not through the point panel.
export const hiddenUntilLearned=record=>!!record.acquisition||record.hiddenUntilLearned===true||record.pointCosts?.length===0;
export function visibleSkillRecords(player,content){const learned=new Set(player.skills.filter(s=>s.level>0).map(s=>s.name));return classSkillRecords(content,player.class).filter(r=>!hiddenUntilLearned(r)||learned.has(r.name));}
export function learnedClassSkills(player,content){const names=new Set(classSkillRecords(content,player.class).map(r=>r.name));return player.skills.filter(s=>names.has(s.name));}
export function normalizeActiveClassSkill(player,content){const skills=learnedClassSkills(player,content);if(!skills.some(s=>s.name===player.activeSkill))player.activeSkill=skills[0]?.name||null;return player;}
