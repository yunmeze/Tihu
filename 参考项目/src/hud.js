// Native images keep their provenance; only the portrait base panel is supplementary.
export class Hud {
 constructor(content,batch){this.content=content;this.batch=batch;}
 async init(){this.index=await this.content.json('ui/native/index.json');const keys=['dialog','button','button-active','tasks-0','system-0','insight-0','collection-0','progress-track','experience','target-track','target-hp'];await Promise.all(keys.map(k=>this.content.texture(this.index.assets[k].file)));await this.content.texture('ui/resource-orbs-v1.png');this.skillPack=await this.content.pack('Data5');await Promise.all(this.skillPack.pages.map(p=>this.content.texture(p.file)));}
 centered(text,x,y,w,size=24,color='#e8dcc0'){const b=this.batch,s=Math.min(size,size*w/Math.max(1,b.textWidth(text,size)));b.shadowText(text,x+(w-b.textWidth(text,s))/2,y,s,color,w);}
 bar(kind,x,y,w,h,ratio=0){const target=kind==='hp',track=target?'target-track':'progress-track',fill=target?'target-hp':'experience';this.image(track,x,y,w,h);const value=Math.max(0,Math.min(1,ratio)),a=this.index.assets[fill];if(value)this.image(fill,x+2,y+2,(w-4)*value,h-4,[0,0,a.width*value,a.height]);}
 image(key,x,y,w,h,region=null){const a=this.index.assets[key],t=a&&this.content.textureNow(a.file);if(!t)return;const [sx,sy,sw,sh]=region||[0,0,a.width,a.height];this.batch.quad(x,y,w??sw,h??sh,'#ffffff',t,this.content.uv(a.file,sx,sy,sw,sh,a.width,a.height));}
 nine(key,x,y,w,h,edges=[12,12,12,12],center=true){
  const a=this.index.assets[key],texture=a&&this.content.textureNow(a.file);if(!texture)return;
  // Native source cuts remain fixed when a slot or dialog moves/resizes.
  // Cache only their UVs, preserving each destination edge and painter order.
  if(this.sliceAtlas!==this.content.atlas){this.sliceAtlas=this.content.atlas;this.sliceCache=new WeakMap();}this.sliceCache||=new WeakMap();let slices=this.sliceCache.get(a);if(!slices)this.sliceCache.set(a,slices=new Map());const id=edges.join(',');let uv=slices.get(id);
  const [left,top,right,bottom]=edges;if(!uv){const sx=[0,left,a.width-right,a.width],sy=[0,top,a.height-bottom,a.height];uv=Array.from({length:9},(_,i)=>{const ix=i%3,iy=Math.floor(i/3);return this.content.uv(a.file,sx[ix],sy[iy],sx[ix+1]-sx[ix],sy[iy+1]-sy[iy],a.width,a.height);});slices.set(id,uv);}
  const dx=[x,x+left,x+w-right,x+w],dy=[y,y+top,y+h-bottom,y+h];for(let iy=0;iy<3;iy++)for(let ix=0;ix<3;ix++){if(!center&&ix===1&&iy===1)continue;this.batch.quad(dx[ix],dy[iy],dx[ix+1]-dx[ix],dy[iy+1]-dy[iy],'#ffffff',texture,uv[iy*3+ix]);}
 }
 panel(x,y,w,h){this.image('dialog',x,y,w,h,[80,65,24,24]);this.nine('dialog',x,y,w,h,[18,40,18,6],false);}
 button(x,y,w,h,selected=false){this.batch.quad(x+3,y+3,w-6,h-6,'#211915');this.image('dialog',x+3,y+3,w-6,h-6,[80,65,24,24]);this.nine(selected?'button-active':'button',x,y,w,h,[7,5,7,5],false);}
 base(y=1040,h=584){this.panel(0,y,750,h);}
 status(heroClass){this.image('status',20,101,369,135);this.image('portrait-male',52,139,86,83);this.image('hp',149,145,166,15);this.image('mp',149,169,166,15);this.batch.text(heroClass+' · 英雄',160,106,26,'#dfc078');}
 nav(tab,x,y,w,h,selected){this.button(x,y,w,h,selected);this.batch.text(tab,x+(w-60)/2,y+(h-30)/2,30,selected?'#ffe0a0':'#c7b58c');}
 slot(x,y,w=78,h=78,selected=false){this.image('dialog',x,y,w,h,[80,65,24,24]);this.nine(selected?'button-active':'button',x,y,w,h,[7,5,7,5],false);if(selected){this.batch.quad(x+5,y+5,w-10,2,'#c2984e');this.batch.quad(x+5,y+h-7,w-10,2,'#c2984e');}}
 outlineSlot(x,y,w=78,h=78,selected=false){this.nine(selected?'button-active':'button',x,y,w,h,[7,5,7,5],false);if(selected){this.batch.quad(x+5,y+5,w-10,2,'#c2984e');this.batch.quad(x+5,y+h-7,w-10,2,'#c2984e');}}
 flowFrame(x,y,w,h,time){
  this.nine('button-active',x,y,w,h,[7,5,7,5],false);const perimeter=2*(w+h),head=((time*160)%perimeter+perimeter)%perimeter,slices=22,length=100/slices;
  const point=t=>{t=(t%perimeter+perimeter)%perimeter;return t<w?[x+t,y]:t<w+h?[x+w,y+t-w]:t<2*w+h?[x+2*w+h-t,y+h]:[x,y+perimeter-t];};
  for(let i=slices-1;i>=0;i--){let start=((head-i*length)%perimeter+perimeter)%perimeter,remaining=length,alpha=1-i/slices;while(remaining>1e-6){const edgeEnd=start<w?w:start<w+h?w+h:start<2*w+h?2*w+h:perimeter,take=Math.min(remaining,edgeEnd-start),a=point(start),b=point(start+take),horizontal=Math.abs(a[1]-b[1])<1e-6,draw=(thickness,opacity,color)=>this.batch.quad(Math.min(a[0],b[0])-(horizontal?0:thickness/2),Math.min(a[1],b[1])-(horizontal?thickness/2:0),horizontal?take:thickness,horizontal?thickness:take,color,this.batch.white,[0,0,1,1],opacity);draw(10,.32*alpha,'#e6ba62');draw(3,alpha,'#fff4c9');remaining-=take;start=(start+take)%perimeter;}}const [hx,hy]=point(head);this.batch.quad(hx-2,hy-2,4,4,'#fffbea');
 }
 skill(name,x,y,size=60,learned=true){const index=this.content.skills.records.find(s=>s.name===name)?.nativeIndex;if(index===undefined)return;this.batch.frame(this.skillPack,1+index*3+(learned?0:2),x,y,size/32,'#ffffff',false);}
 orb(kind,x,y,size,ratio){const texture=this.content.textureNow('ui/resource-orbs-v1.png');if(!texture)return;const half=kind==='hp'?0:.5,source=this.index.assets['resource-orbs'],sw=source.width,sh=source.height;this.batch.quad(x,y,size,size,'#423c36',texture,this.content.uv('ui/resource-orbs-v1.png',half*sw,0,sw/2,sh,sw,sh));const fill=Math.max(0,Math.min(1,ratio));if(fill)this.batch.quad(x,y+size*(1-fill),size,size*fill,'#ffffff',texture,this.content.uv('ui/resource-orbs-v1.png',half*sw,sh*(1-fill),sw/2,sh*fill,sw,sh));}
 snapshot(){return {nativeAssets:Object.values(this.index.assets).filter(a=>!a.generated).length,menuSkin:'Data1/Data2 native slices; Data5 and Item1 source icons',orbsGenerated:true,portraitPanelGenerated:false};}
}
