import fs from 'node:fs/promises';
const file='src/render.js';let s=await fs.readFile(file,'utf8');
s=s.replace('float lighting=.38+.62*max(dot(worldNormal,normalize(vec3(-.4,.9,.3))),0.);',`vec3 tn=tex(baseNormal,baseTiling)*2.-1.;tn=mix(tn,tex(coverNormal,coverTiling)*2.-1.,smoothstep(.35,.65,variation)*${.55});tn=mix(tn,tex(pathNormal,pathTiling)*2.-1.,masks.r);tn=mix(tn,tex(clearingNormal,clearingTiling)*2.-1.,masks.g);tn=mix(tn,tex(roughNormal,roughTiling)*2.-1.,masks.b*.65);vec3 surfaceNormal=normalize(worldNormal+vec3(-tn.x,0.,tn.y));float lighting=.34+.66*max(dot(surfaceNormal,normalize(vec3(-.4,.9,.3))),0.);`);
s=s.replaceAll("material.userData.source?.floats._Tiling||1.6","1/(material.userData.source?.floats._Tiling||1.6)");
s=s.replace('sourceNormal=normalize(mat3(modelMatrix)*objectNormal);','vec3 sourceN=objectNormal;\\n#ifdef USE_INSTANCING\\nsourceN=mat3(instanceMatrix)*sourceN;\\n#endif\\nsourceNormal=normalize(mat3(modelMatrix)*sourceN);');
s=s.replace('constructor(assets,shared){this.assets=assets;this.shared=shared;this.root=new T.Group();}','constructor(assets,shared){this.assets=assets;this.shared=shared;this.root=new T.Group();this.propMaterials=new Map();this.buckets=[];}');
s=s.replace('const liquid=liquidMaterial(a,a.ref(s.LiquidMaterial),this.shared);','const liquid=this.liquid=liquidMaterial(a,a.ref(s.LiquidMaterial),this.shared);');
s=s.replace('if(Math.hypot(p.x,p.z)>24)continue;','');
s=s.replace('materials=await Promise.all(d.Materials.map(id=>a.material(a.ref(id))));materials.forEach(m=>clipMaterial(m,this.shared,s));',`materials=await Promise.all(d.Materials.map(async id=>{const key=a.ref(id);if(!this.propMaterials.has(key)){const original=await a.material(key),mat=original.clone();mat.userData={source:original.userData.source};clipMaterial(mat,this.shared,s);this.propMaterials.set(key,mat);}return this.propMaterials.get(key);}));`);
s=s.replace('inst.castShadow=inst.receiveShadow=true;this.root.add(inst);','inst.castShadow=inst.receiveShadow=true;inst.frustumCulled=false;this.buckets.push({inst,placements});this.root.add(inst);');
s=s.replace('  return this;\n }\n dispose(){',`  this.update(new T.Vector3());return this;
 }
 update(center){if(this.lastCenter&&this.lastCenter.distanceToSquared(center)<.2)return;this.lastCenter=center.clone();const matrix=new T.Matrix4(),q=new T.Quaternion(),v=new T.Vector3(),range=this.shared.radius.value+7;
  for(const {inst,placements}of this.buckets){let count=0;for(const p of placements){if(Math.abs(p.x-center.x)>range||Math.abs(p.z-center.z)>range)continue;matrix.compose(new T.Vector3(p.x,0,p.z),q.setFromAxisAngle(new T.Vector3(0,1,0),p.yaw*Math.PI/180),v.setScalar(p.scale));inst.setMatrixAt(count++,matrix);}inst.count=count;inst.instanceMatrix.needsUpdate=true;}
 }
 dispose(){`);
s=s.replace('this.material?.dispose();}','this.material?.dispose();this.liquid?.dispose();for(const m of this.propMaterials.values())m.dispose();this.root.traverse(o=>{if(o.isInstancedMesh)o.dispose();});}');
await fs.writeFile(file,s);
