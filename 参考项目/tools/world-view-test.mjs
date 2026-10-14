import assert from 'node:assert/strict';import fs from 'node:fs/promises';import {WORLD_VIEW,worldView} from '../src/world-view.js';
const z=WORLD_VIEW.scale,p=WORLD_VIEW.padding,checks=[];
for(const camera of [{x:86,y:52},{x:86.0001,y:52.0001},{x:86.01,y:52.01},{x:85.99,y:51.99},{x:0,y:0}]){
 const v=worldView(camera),[u,top,du,dv]=v.uv;
 assert.ok(u>0&&u+du<1);assert.ok(top<1&&top+dv>0);
 for(const point of [{x:86,y:52},{x:87,y:53},{x:85,y:51}]){
  const sx=v.origin.x+point.x*48*z-u*WORLD_VIEW.width*z,sy=v.origin.y+point.y*32*z-(1-top)*WORLD_VIEW.height*z;
  assert.ok(Math.abs(sx-(375+(point.x-camera.x)*48*z))<1e-9);assert.ok(Math.abs(sy-(555+(point.y-camera.y)*32*z))<1e-9);
 }
 checks.push({camera,padding:p,uvWithinOverscan:true});
}
const r={passed:true,checks};await fs.writeFile('reports/world-view-tests.json',JSON.stringify(r,null,2));console.log(JSON.stringify({passed:true,cases:checks.length}));
