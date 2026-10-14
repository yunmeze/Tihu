import {CHALLENGE_RULES,challengeTime,challengeRemaining,endChallenge} from './challenges.js';

export function drawChallengeHud(a){
 const s=a.combat.challenge;if(!s)return;
 a.button('挑战',404,20,126,80,()=>a.openFeature('challenge'),false,27);
 const remaining=challengeRemaining(a.combat),label=challengeTime(s.frames)+(s.kind==='time'?'  剩余敌人：'+remaining:'  生存挑战');
 a.hud.button(18,200,510,50);a.hud.centered(label,28,213,490,25,'#f6e4b6');
 if(s.kind==='time')a.hud.bar('xp',18,252,510,12,(57-remaining)/57);
}
export function drawChallengeDialog(a){
 const c=a.combat,s=c.challenge;if(!s)return;const h=a.hud,b=a.batch,records=a.player.challengeRecords;
 const status=s.status==='active'?'进行中':s.status==='complete'?'成功！':s.status==='failed'?(s.kind==='time'?'失败':'结束'):'已退出';
 h.centered(CHALLENGE_RULES[s.kind].name+' - '+status,68,375,614,34,'#e6c78d');
 const duration=s.kind==='survival'?(s.status==='active'?'你已经存活了':'这次，你存活了'):(s.status==='active'?'你已经用了':'你共用了');
 h.centered(duration+' '+challengeTime(s.frames),68,471,614,31);
 if(s.kind==='time'){
  const remaining=challengeRemaining(c);h.centered('剩余敌人：'+remaining+' / 57',68,552,614,29);h.bar('xp',96,612,558,28,(57-remaining)/57);
  b.paragraph('最短用时：'+(records.timeFrames?challengeTime(records.timeFrames):'还未完成过该挑战'),96,712,558,29,43,3);
 }else h.centered('最长存活：'+challengeTime(records.survivalFrames),68,595,614,29);
 if(s.status==='failed')b.paragraph('胜败乃兵家常事，回头又是一条好汉',96,892,558,29,43,3);
 if(s.status==='active')a.button('继续挑战',182,1140,386,64,()=>a.closeFeature(),false,29);
 if(s.status==='complete')a.button('继续拾取',182,1140,386,64,()=>a.closeFeature(),false,29);
 if(a.player.hp<=0)a.button('回城复活',182,1240,386,64,()=>a.reviveAtTown(),false,29);
 else a.button(s.status==='active'?'退出挑战':'返回入口地图',182,1240,386,64,async()=>{
  const origin={...s.origin};if(s.status==='active')endChallenge(c,'abandoned');a.save();
  await a.changeMap(origin.map,{x:origin.x,y:origin.y},{unlock:true});a.save();
 },false,29);
}
