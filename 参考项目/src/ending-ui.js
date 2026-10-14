import {storyPages,STORY_COLORS,advanceEnding} from './ending.js';
import {advanceOpening} from './opening.js';
export function storyLines(text,font,width,size){const rows=[];let row='',used=0;for(const ch of text){const advance=(font.glyphs[ch]?.advance||32)*size/32;if(ch==='\n'||used+advance>width){rows.push(row);row='';used=0;if(ch==='\n')continue;}row+=ch;used+=advance;}if(row)rows.push(row);return rows;}
export function drawEnding(a){
 const s=a.combat.story,opening=s.kind==='opening',advance=opening?advanceOpening:advanceEnding,pages=storyPages(opening?a.content.story.opening:a.content.story.ending,s.clears),page=pages[s.page],h=a.hud,b=a.batch;
 a.entry.background();b.quad(38,160,674,1340,'#2b211d');h.panel(38,160,674,1340);h.centered(opening?'前世今生':'封印魔界',68,215,614,39,'#e6c78d');
 // Reflow the source paragraphs; preserve dialogue and notice line breaks.
 const size=page.onlyClear===1?28:32,lines=storyLines(page.text,a.content.font,570,size);a.endingLayout={lines:lines.length,capacity:20,page:s.page,pages:pages.length};
 lines.slice(0,20).forEach((text,i)=>b.text(text,90,365+i*47,size,STORY_COLORS[page.color]||'#ffff00'));
 if(a.message&&a.elapsed<a.messageUntil)h.centered(a.message,68,1320,614,26,'#e6c78d');
 if(!opening)h.centered('通关 '+s.clears+' 次',68,1270,614,27,'#d5bd8c');h.centered((s.page+1)+' / '+pages.length,267,1374,216,26);
 if(s.page)a.button('上一页',68,1410,250,62,()=>advance(a,-1),false,28);
 a.button(s.page<pages.length-1?'下一页':opening?'进入梦境':'返回海曦村',382,1410,300,62,()=>advance(a),false,28);
}
