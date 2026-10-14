// Pool 5c5b00 (1024 entries), Data1 frame31 at 599aa8, update 5c6c10.
// Native status particles: 0 ice, 1 burn, 2 poison. Restorations 3/8
// lose twenty alpha units per tick; dark-aura type4 loses five.
export function emitNativeParticle(c,type,point,options={}){
 const particles=c.particles||=[],rnd=c.visualRandom||Math.random;if(particles.length>=1024)return null;
 let dx=0,dy=0,vx=0,vy=-.6,color='#000000',alpha=200,fade=5,frame=31,rgb,stage,angle,spin=0,pack='Data1',size=1;
 if(type===0){frame=rnd()<.5?33:32;dy=-rnd()*40;vy=-rnd()-.5;const sign=rnd()<.5?-1:1;vx=sign*rnd()/2;dx=16+sign*rnd()*15;color='#ffffff';alpha=220;}
 else if(type===1){vy=-rnd()-.5;dy=-rnd()*50;dx=(rnd()<.5?1:-1)*rnd()*15;rgb=[255,255,0];color='#ffff00';stage=1;frame=25;}
 else if(type===2||type===4){dy=-rnd()*50;dx=(rnd()<.5?1:-1)*rnd()*15;if(type===2)color='#00ff00';}
 else if(type===3||type===8){dx=rnd()*100-10;dy=10-rnd()*80;const angle=Math.atan2(-dy,48-dx);vx=Math.cos(angle)*1.8;vy=Math.sin(angle)*1.8;color=type===3?'#ff0000':'#0000ff';alpha=255;fade=20;}
 else if(type===5||type===21){dy=-rnd()*12;const sign=rnd()<.5?1:-1;dx=sign*rnd()*(type===5?15:18);vy=type===5?-.8:-1.8;frame=34;color=options.color||'#ffffff';alpha=type===5?240:200;fade=type===5?5:4;angle=0;spin=sign*(type===5?.05:.06);}
 else if(type===6||type===7){dx=type===6?7:-25;dy=type===6?-35:-75;vy=type===6?-.6:-.7;frame=type===6?35:36;color='#ffffff';alpha=type===6?210:255;}
 else if(type===9||type===20){vy=0;pack='Data8';frame=type===9?7:8;color='#ffffff';alpha=0;stage=1;size=1.5;if(type===20&&c.particleView){const x=(point.x-c.particleView.x)*48,y=(point.y-c.particleView.y)*32;if(x< -250||x>1000||y< -250||y>600){stage=2;size=3;alpha=255;}}}
 else if(type===22){vy=0;angle=rnd()*360;dy=-rnd()*30;const sign=rnd()<.5?1:-1;dx=sign*rnd()*20;pack='Data8';frame=11;color='#ffffff';alpha=255;fade=10;}
 else return null;
 const p={type,x:point.x,y:point.y,dx,dy,vx,vy,color,alpha,fade,frame,pack,size,age:0,...(rgb?{rgb,stage}:{}),...(angle!==undefined?{angle,spin}:{}),...([9,20].includes(type)?{stage}: {})};particles.push(p);return p;
}
export function updateNativeParticles(c){
 // Compact the native bounded pool in place; no new array every 20 ms.
 const particles=c.particles||=[];let count=0;
 for(const p of particles){p.dx+=p.vx;p.dy+=p.vy;p.age=(p.age||0)+1;if(p.angle!==undefined)p.angle+=p.spin||0;if(p.type===1){if(p.stage===1){p.rgb[1]=Math.max(0,p.rgb[1]-20);if(!p.rgb[1])p.stage=2;}else if(p.stage===2){p.rgb[0]=Math.max(0,p.rgb[0]-20);if(!p.rgb[0])p.stage=3;}else p.alpha-=10;p.color='#'+p.rgb.map(n=>n.toString(16).padStart(2,'0')).join('');}else if(p.type===9||p.type===20){if(p.stage===1){p.alpha+=p.type===9?10:1;p.size+=p.type===9?.02:.01;if(p.alpha>=255){p.alpha=255;p.stage=2;}}else if(p.stage===2){p.age++;p.size+=.01;if(p.age>(p.type===9?20:30))p.stage=3;}else{p.alpha--;p.size+=.01;}}else p.alpha-=p.fade;if(p.alpha>0||p.stage===1)particles[count++]=p;}particles.length=count;
 if(c.player.hp>0&&c.ruleFrame%2===0){if(c.player.healingPool>0)emitNativeParticle(c,3,c.position);if(c.player.mpRecoveryPool>0)emitNativeParticle(c,8,c.position);}
}
export function drawNativeParticles(a){
 for(const p of a.combat.particles||[]){const pack=a.packs.get(p.pack||'Data1');if(!pack)continue;const cloud=p.type===9||p.type===20;if(Math.abs(p.x-a.camera.x)>(cloud?40:17)||Math.abs(p.y-a.camera.y)>(cloud?50:26))continue;const q=a.mapPoint(p.x,p.y),z=a.worldScale,size=p.size||1;let x=q.x+p.dx*z,y=q.y+p.dy*z;if(cloud){x-=(p.type===9?60:120)*size*z;y-=(p.type===9?40:120)*size*z;}if(p.angle!==undefined)a.batch.rotatedFrame(pack,p.frame,x,y,z*size,z*size,p.angle,p.alpha/255,p.color,p.type===22?null:[0,0]);else a.batch.frame(pack,p.frame||31,x,y,z*size,p.color,false,p.alpha/255);}
}
