import fs from 'node:fs/promises';import assert from 'node:assert/strict';
import {MAP_GROUPS,mapSpriteExtents,visibleMapCells} from '../src/map-visibility.js';
import {WORLD_VIEW,worldView} from '../src/world-view.js';
const read=async file=>JSON.parse(await fs.readFile('public/assets/'+file,'utf8')),packs=new Map(await Promise.all(['FloorBig','FloorSmall',...Object.values(MAP_GROUPS)].map(async name=>['Map/Res/'+name,await read('sprites/Map/Res/'+name+'/index.json')])));packs.set('Data4',await read('sprites/Data4/index.json'));
// An 800-pixel roof whose bottom anchor is far below a 300-pixel viewport.
const frame={original:[48,800],crop:[0,30],rect:[0,0,48,770]},fixturePacks=new Map([['Map/Res/Building',{frames:[null,frame]}]]),fixture={width:2,height:40,cells:Array.from({length:80},()=>[0,0,0,0])};fixture.cells[30]=[0,0,4,1];
const extents=mapSpriteExtents(fixture,fixturePacks),tall=visibleMapCells(fixture,fixturePacks,{x:0,y:0,width:100,height:300},extents);assert.ok(tall.some(c=>c.y===30&&c.objectVisible&&!c.floorVisible));assert.equal(extents.top,-738);assert.deepEqual(visibleMapCells(fixture,fixturePacks,{x:0,y:-1100,width:100,height:300},extents),[]);
// A map loaded before its art must acquire the roof once the real map pack
// arrives. Loading an enemy pack cannot substitute its bounds for map art.
const latePacks=new Map(),view={x:0,y:0,width:100,height:300};
assert.equal(mapSpriteExtents(fixture,latePacks).top,0);assert.deepEqual(visibleMapCells(fixture,latePacks,view,mapSpriteExtents(fixture,latePacks)),[]);
latePacks.set('Mon/1',fixturePacks.get('Map/Res/Building'));assert.equal(mapSpriteExtents(fixture,latePacks).top,0);
latePacks.set('Map/Res/Building',fixturePacks.get('Map/Res/Building'));assert.ok(visibleMapCells(fixture,latePacks,view,mapSpriteExtents(fixture,latePacks)).some(c=>c.y===30&&c.objectVisible));
latePacks.set('Map/Res/Building',{frames:[null,{original:[48,50],crop:[0,0],rect:[0,0,48,50]}]});assert.equal(mapSpriteExtents(fixture,latePacks).top,-18);assert.deepEqual(visibleMapCells(fixture,latePacks,view,mapSpriteExtents(fixture,latePacks)),[]);
fixture.cells[30][3]=0;assert.equal(mapSpriteExtents(fixture,latePacks).top,0);fixture.cells[30][3]=1;
const mapList=await read('data/maps.json'),cases=[];let checkedViews=0,offscreenAnchors=0,maximumOverhang=0;
for(const entry of mapList){const map=await read('maps/'+entry.id+'.json'),bounds=mapSpriteExtents(map,packs);maximumOverhang=Math.max(maximumOverhang,-bounds.top);const cameras=[{x:0,y:0},{x:map.width/2+.49,y:map.height/2+.51},{x:map.width-1,y:map.height-1},{x:map.width/2,y:0},{x:0,y:map.height/2},{x:map.width-1,y:map.height/2},...(map.home?[{x:map.home[0]+.03,y:map.home[1]+.01}]:[])];
 for(const camera of cameras){const origin=worldView(camera).origin,z=WORLD_VIEW.scale,view={x:origin.x/z,y:origin.y/z,width:WORLD_VIEW.width,height:WORLD_VIEW.height},actual=visibleMapCells(map,packs,view,bounds),keys=new Map(actual.map(c=>[c.x+','+c.y,c])),expected=[];
  // Exhaustive whole-map oracle is independent of the bounded search range.
  for(let x=0;x<map.width;x++)for(let y=0;y<map.height;y++){const cell=map.cells[x*map.height+y],[floor,,type,index]=cell,floorFrame=floor&&packs.get('Map/Res/'+(floor<0?'FloorBig':'FloorSmall')).frames[Math.abs(floor)],objectFrames=index>0?(type===8?[55,56,57,58,59].map(i=>({f:packs.get('Data4').frames[i],top:-52})):MAP_GROUPS[type]?Array.from({length:type===5?5:1},(_,i)=>packs.get('Map/Res/'+MAP_GROUPS[type]).frames[index+i]).filter(Boolean).map(f=>({f,top:32-f.original[1]})):[]):[],intersects=({f,top})=>{if(!f||f.rect[2]<=0||f.rect[3]<=0)return false;const left=view.x+x*48+f.crop[0],yTop=view.y+y*32+f.crop[1]+top;return left+f.rect[2]>-1&&yTop+f.rect[3]>-1&&left<view.width+1&&yTop<view.height+1;},hits=[intersects({f:floorFrame,top:0}),objectFrames.some(intersects)];if(hits.some(Boolean)){const key=x+','+y,c=keys.get(key);expected.push(key);assert.ok(c,entry.id+'/'+key);assert.equal(c.floorVisible,hits[0]);assert.equal(c.objectVisible,hits[1]);if(hits[1]&&view.y+y*32>view.height)offscreenAnchors++;}}
  assert.equal(keys.size,expected.length);checkedViews++;
  // Preload one full cell ahead, including diagonal camera movement.
  const preload=new Map(visibleMapCells(map,packs,view,bounds,{padding:49}).map(c=>[c.x+','+c.y,c]));for(const [dx,dy]of [[48,0],[-48,0],[0,32],[0,-32],[48,32],[-48,-32]])for(const c of visibleMapCells(map,packs,{...view,x:view.x+dx,y:view.y+dy},bounds)){const ahead=preload.get(c.x+','+c.y);assert.ok(ahead,entry.id+' prefetch gap');if(c.floorVisible)assert.ok(ahead.floorVisible);if(c.objectVisible)assert.ok(ahead.objectVisible);}
 }
 cases.push({map:entry.id,extents:bounds,views:cameras.length});
}
assert.ok(offscreenAnchors>0);const result={passed:true,maps:mapList.length,checkedViews,offscreenAnchors,maximumOverhang,tallOffscreenRoofIncluded:true,lateMapArtAndReplacementCovered:true,oneCellAheadPreloadCovered:true,cases};await fs.writeFile('reports/map-visibility-tests.json',JSON.stringify(result,null,2));console.log({passed:true,maps:mapList.length,checkedViews,offscreenAnchors,maximumOverhang});
