// GAMEOVER dispatcher6186fd; native settlement62e418..62e6c9.
export const ENDING_RULES={destination:{id:'A00',x:138,y:12},bossTimers:30,bossTimerValue:-1,bossCycleValue:1,events:30,eventValue:0,direction:4,maxClearCount:32767,modeUnlockMax:3,firstClearNotice:1};
export const STORY_COLORS={红:'#ff0000',橙:'#ff9b00',黄:'#ffff00',绿:'#00ff00',青:'#00ffff',蓝:'#0000ff',紫:'#ff00ff',白:'#ffffff',黑:'#000000'};
export function storyPages(data,count){
 const pages=[];let page;for(const line of (data?.script||'').split(/\r?\n/)){
  const p=line.match(/^#P\s+(\S+)(?:\s+(\S+))?(?:\s+(\d+))?\s*$/i);
  if(p){page={color:p[1],secondary:p[2]||'黑',onlyClear:p[3]?Number(p[3]):null,lines:[]};pages.push(page);}
  else if(page&&!line.startsWith('#'))page.lines.push(line);
 }
 return pages.filter(p=>p.onlyClear===null||p.onlyClear===count).map(p=>({...p,text:reflow(p.lines)}));
}
function reflow(lines){
 const out=[];for(const line of lines){if(!line.trim()){if(out.length&&out.at(-1)!=='\n')out.push('\n');continue;}if(out.length&&out.at(-1)!=='\n'&&/^　/.test(line))out.push('\n');out.push(line.trimEnd());}
 return out.join('').replace(/^\n+|\n+$/g,'');
}
export function normalizeEndingPlayer(p){p.clearCount=Number.isSafeInteger(p.clearCount)&&p.clearCount>=0&&p.clearCount<=32767?p.clearCount:0;p.modeUnlock=Number.isSafeInteger(p.modeUnlock)&&p.modeUnlock>=0&&p.modeUnlock<=3?p.modeUnlock:0;return p;}
export function planEnding(c,e){
 const p=c.player,mode=p.gameMode||0;
 if(c.story||p.hp<=0||p.events?.[0]!==28||c.map.id!=='A13'||!Number.isSafeInteger(p.clearCount||0)||(p.clearCount||0)>=32767||![0,1,2].includes(mode)||!storyPages(c.content.story?.ending,(p.clearCount||0)+1).length)return null;
 return {...e};
}
export function beginEnding(c){
 const p=normalizeEndingPlayer(c.player);p.clearCount++;p.modeUnlock=Math.max(p.modeUnlock,(p.gameMode||0)+1);p.questLog='';p.questFlags=Array(30).fill(0);p.events=Array(30).fill(0);p.bossTimers=Array(30).fill(-1);p.bossCycles=Array(30).fill(1);
 c.stopFarming();c.position.direction=4;c.story={version:1,kind:'ending',phase:'reading',page:0,clears:p.clearCount};
 for(const state of [c.scriptState,c.mapFlagsByMap])if(state)for(const key of Object.keys(state))delete state[key];
}
export function restoreEnding(p,content,s){
 if(!s||s.version!==1||s.kind!=='ending'||!['reading','return'].includes(s.phase)||s.clears!==p.clearCount||!Number.isSafeInteger(s.page)||s.page<0)return null;
 const pages=storyPages(content.story?.ending,p.clearCount);return s.page<pages.length?{version:1,kind:'ending',phase:s.phase,page:s.page,clears:s.clears}:null;
}
export async function advanceEnding(a,delta=1){
 const c=a.combat,s=c?.story;if(!s||a.storyBusy||a.changing||a.entering||a.disposed)return false;const pages=storyPages(a.content.story.ending,s.clears);
 if(delta<0){s.page=Math.max(0,s.page-1);s.phase='reading';a.save();return true;}
 if(s.phase==='reading'&&s.page<pages.length-1){s.page++;a.save();return true;}
 s.phase='return';a.save();a.storyBusy=true;
 try{const d=ENDING_RULES.destination;if(!await a.changeMap(d.id,{x:d.x,y:d.y},{unlock:true}))return false;c.story=null;a.tab='战斗';a.save();return true;}
 catch(e){s.phase='reading';a.save();a.notify('回村未完成，请重试');return false;}
 finally{a.storyBusy=false;}
}
