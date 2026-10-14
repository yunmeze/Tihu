import {storyPages} from './ending.js';
export function openingDestination(content){const m=content.story?.opening?.script.match(/^#To\s+(\S+)\s+(\d+)\s+(\d+)\s*$/im);return m?{id:m[1],x:+m[2],y:+m[3]}:null;}
export function restoreOpening(content,s){return s?.version===1&&s.kind==='opening'&&s.phase==='reading'&&Number.isInteger(s.page)&&s.page>=0&&s.page<storyPages(content.story?.opening).length?{version:1,kind:'opening',phase:'reading',page:s.page}:null;}
export async function advanceOpening(a,delta=1){
 const s=a.combat?.story;if(s?.kind!=='opening'||a.storyBusy||a.changing||a.disposed)return false;
 const pages=storyPages(a.content.story.opening);if(delta<0){s.page=Math.max(0,s.page-1);a.save();return true;}if(s.page<pages.length-1){s.page++;a.save();return true;}
 // The source #To was applied when this new character entered the dream.
 // Do not replay the map load script or change ET0 when resuming a story save.
 a.combat.story=null;a.tab='战斗';a.save();return true;
}
