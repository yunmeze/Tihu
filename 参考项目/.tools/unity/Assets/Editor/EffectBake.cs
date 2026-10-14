using System;
using System.IO;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
public static class EffectBake {
 [Serializable]public class Curve {public int mode;public float min,max;public Key[] keys;}
 [Serializable]public class Key {public float time,value,inSlope,outSlope;}
 [Serializable]public class ColorKey {public float time;public Color color;}
 [Serializable]public class AlphaKey {public float time,alpha;}
 [Serializable]public class ParticleInput {public Curve lifetime,gravity,size,rotation,sizeLife;public ColorKey[] colorKeys;public AlphaKey[] alphaKeys;public bool colorEnabled,sizeEnabled;public int tilesX,tilesY,material,mesh,positionOffset,positionCount,normalOffset,indexOffset,indexCount,indexBytes;public string meshFile;}
 [Serializable]public class Job {public string name,profile,definition;public int skill,segments;public float waveWidth;public ParticleInput[] particles;}
 [Serializable]public class Jobs {public Job[] jobs;}
 [Serializable]public class Frame {public int offset,count,shockOffset,shockCount;public int[] particleOffsets,particleCounts;public Vector4 shape,clock,style,impact;public float[] limits;}
 [Serializable]public class Effect {public string name,file;public int skill;public float duration,fps,eventDuration,startRadius,endRadius,speed;public int[] particleMaterials;public bool[] particleBillboards;public Frame[] frames;}
 [Serializable]public class Index {public int stride=14;public Effect[] effects;}
 static string Root=>Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 public static void All(){Run();UIBake.Run();}
 static ParticleSystem.MinMaxCurve ConvertCurve(Curve c){
  if(c==null)return new ParticleSystem.MinMaxCurve(1);
  if(c.mode==3)return new ParticleSystem.MinMaxCurve(c.min,c.max);
  if(c.mode==1){var keys=new List<Keyframe>();foreach(var k in c.keys)keys.Add(new Keyframe(k.time,k.value,k.inSlope,k.outSlope));return new ParticleSystem.MinMaxCurve(c.max,new AnimationCurve(keys.ToArray()));}
  return new ParticleSystem.MinMaxCurve(c.max);
 }
 static ParticleSystem MakeParticle(GameObject owner,ParticleInput p){
  if(p==null||p.material==0)return null;var go=new GameObject("Source particle "+p.material);go.transform.SetParent(owner.transform,false);var ps=go.AddComponent<ParticleSystem>();ps.Stop(true,ParticleSystemStopBehavior.StopEmittingAndClear);ps.useAutoRandomSeed=false;ps.randomSeed=173;
  var main=ps.main;main.playOnAwake=false;main.loop=false;main.simulationSpace=ParticleSystemSimulationSpace.World;main.maxParticles=160;main.startSpeed=0;main.startLifetime=ConvertCurve(p.lifetime);main.startSize=ConvertCurve(p.size);main.startRotation=ConvertCurve(p.rotation);main.gravityModifier=ConvertCurve(p.gravity);
  var emission=ps.emission;emission.enabled=false;var shape=ps.shape;shape.enabled=false;var size=ps.sizeOverLifetime;size.enabled=p.sizeEnabled;if(p.sizeEnabled)size.size=ConvertCurve(p.sizeLife);
  var color=ps.colorOverLifetime;color.enabled=p.colorEnabled;if(p.colorEnabled){var g=new Gradient();var ck=new List<GradientColorKey>();foreach(var k in p.colorKeys)ck.Add(new GradientColorKey(k.color,k.time));var ak=new List<GradientAlphaKey>();foreach(var k in p.alphaKeys)ak.Add(new GradientAlphaKey(k.alpha,k.time));g.SetKeys(ck.ToArray(),ak.ToArray());color.color=g;}
  var uv=ps.textureSheetAnimation;uv.enabled=p.tilesX>1;if(uv.enabled){uv.numTilesX=p.tilesX;uv.numTilesY=p.tilesY;uv.frameOverTime=0;uv.startFrame=new ParticleSystem.MinMaxCurve(0,.9999f);}
  var renderer=go.GetComponent<ParticleSystemRenderer>();renderer.sharedMaterial=new Material(Shader.Find("Hidden/Internal-Colored"));renderer.renderMode=ParticleSystemRenderMode.Billboard;if(p.mesh>0){renderer.renderMode=ParticleSystemRenderMode.Mesh;var vertices=new Vector3[p.positionCount];var normals=new Vector3[p.positionCount];var indices=new int[p.indexCount];using(var r=new BinaryReader(File.OpenRead(Path.Combine(Root,"public/assets",p.meshFile)))){r.BaseStream.Position=p.positionOffset;for(int i=0;i<vertices.Length;i++)vertices[i]=new Vector3(-r.ReadSingle(),r.ReadSingle(),r.ReadSingle());r.BaseStream.Position=p.normalOffset;for(int i=0;i<normals.Length;i++)normals[i]=new Vector3(-r.ReadSingle(),r.ReadSingle(),r.ReadSingle());r.BaseStream.Position=p.indexOffset;for(int i=0;i<indices.Length;i++)indices[i]=p.indexBytes==2?r.ReadUInt16():(int)r.ReadUInt32();}for(int i=0;i<indices.Length;i+=3){int a=indices[i];indices[i]=indices[i+2];indices[i+2]=a;}var mesh=new Mesh();mesh.vertices=vertices;mesh.normals=normals;mesh.uv=new Vector2[vertices.Length];mesh.triangles=indices;renderer.mesh=mesh;}
  return ps;
 }
 public static void Run(){
  var jobs=JsonUtility.FromJson<Jobs>(File.ReadAllText(Path.Combine(Root,".tools/effect-jobs.json")));var outputs=new List<Effect>();var folder=Path.Combine(Root,"public/assets/effects");Directory.CreateDirectory(folder);
  var cameraObject=new GameObject("Bake camera");var camera=cameraObject.AddComponent<Camera>();camera.orthographic=true;cameraObject.transform.position=new Vector3(-6,5,-6);cameraObject.transform.LookAt(Vector3.zero);
  foreach(var job in jobs.jobs){
   var p=ScriptableObject.CreateInstance<CombatSkillPresentationProfile>();JsonUtility.FromJsonOverwrite(job.profile,p);
   var go=new GameObject(job.name,typeof(MeshFilter),typeof(MeshRenderer));var effect=go.AddComponent<ElementalSkillEffect>();effect.FireFlames=job.skill==0;effect.EarthCrests=job.skill==2;effect.Segments=job.segments;
   var particles=new ParticleSystem[3];var materialIds=new int[3];for(int i=0;i<3;i++){particles[i]=MakeParticle(go,job.particles[i]);materialIds[i]=job.particles[i]?.material??0;}
   effect.Sparks=particles[0];effect.Rubble=particles[1];effect.Smoke=particles[2];var shock=new Material(Shader.Find("Hidden/Internal-Colored"));effect.Warm(true,shock);
   var timeline=new CombatSkillTimeline();var skill=JsonUtility.FromJson<CombatSkillDefinition>(job.definition);skill.Presentation=p;
   bool secondary=job.name.Contains("aftershock");var pulse=new CombatSkillPulse{Cast=new CombatSkillCast{Id=173,Skill=skill},Origin=Vector3.zero,Direction=Vector3.forward,Radius=skill.Radius,Angle=skill.Angle,Secondary=secondary,WaveWidth=job.waveWidth};
   string kn=job.name.Split('_')[1];var kind=kn=="contact"?CombatSkillVisualKind.Contact:kn=="ground"?(job.skill==0?CombatSkillVisualKind.Scorch:CombatSkillVisualKind.BrokenGround):kn=="crater"?CombatSkillVisualKind.Uplift:kn=="takeoff"?CombatSkillVisualKind.Takeoff:kn=="shadow"?CombatSkillVisualKind.Shadow:CombatSkillVisualKind.Front;
   float start=kind==CombatSkillVisualKind.Front?(secondary?0:skill.Action.ContactRadius):kind==CombatSkillVisualKind.Uplift||kind==CombatSkillVisualKind.BrokenGround||kind==CombatSkillVisualKind.Scorch?skill.Action.ContactRadius:0;
   float end=kind==CombatSkillVisualKind.Contact?skill.Action.ContactRadius:kind==CombatSkillVisualKind.Takeoff?.6f:kind==CombatSkillVisualKind.Shadow?.45f:skill.Radius;
   float speed=job.skill==0?skill.Action.WaveSpeed:(end-start)/(secondary?skill.Action.AftershockTravelTime:skill.Action.PrimaryTravelTime);
   float duration=kind==CombatSkillVisualKind.Front?(end-start)/speed:kind==CombatSkillVisualKind.Contact?(job.skill==0?.25f:.45f):kind==CombatSkillVisualKind.Scorch?skill.Action.ScorchInterval*skill.Action.ScorchTicks:kind==CombatSkillVisualKind.Uplift?p.FractureLifetime:kind==CombatSkillVisualKind.Takeoff?.25f:kind==CombatSkillVisualKind.Shadow?skill.Action.LandingTime-skill.Action.TakeoffTime:2f;
   if(kind!=CombatSkillVisualKind.Front&&kind!=CombatSkillVisualKind.Uplift&&kind!=CombatSkillVisualKind.BrokenGround)speed=0;
   var visual=new CombatSkillVisualEvent{Pulse=pulse,Timeline=timeline,Kind=kind,Duration=duration,StartRadius=start,EndRadius=end,Speed=speed};
   bool invisible=kind==CombatSkillVisualKind.Shadow;int sparks=invisible||kind==CombatSkillVisualKind.Uplift||kind==CombatSkillVisualKind.BrokenGround?0:job.skill==0?(kind==CombatSkillVisualKind.Front?p.EmberCount:kind==CombatSkillVisualKind.Contact?26:14):kind==CombatSkillVisualKind.Contact?36:kind==CombatSkillVisualKind.Takeoff?10:p.WaveDustCount;
   int rubble=invisible||kind==CombatSkillVisualKind.Uplift||kind==CombatSkillVisualKind.BrokenGround?0:job.skill==0?(kind==CombatSkillVisualKind.Front?p.SmokeCount:5):kind==CombatSkillVisualKind.Contact?24:kind==CombatSkillVisualKind.Takeoff?4:p.WaveChipCount;
   effect.Begin(visual,sparks,rubble);var frames=new List<Frame>();string file=job.name+".bin";float total=job.skill==0?kind==CombatSkillVisualKind.Front?duration+p.ScorchLinger+1.1f:kind==CombatSkillVisualKind.Scorch?duration+.7f:1.9f:duration+1.3f;
   using(var stream=File.Create(Path.Combine(folder,file)))using(var w=new BinaryWriter(stream)){
    for(int f=0;f<=Mathf.CeilToInt(total*30);f++){timeline.Time=f/30.0;effect.Tick();var frame=new Frame{offset=(int)stream.Position};frame.count=WriteMesh(go.GetComponent<MeshFilter>(),w);
     frame.shockOffset=(int)stream.Position;var sf=go.transform.Find(job.skill==0?"Fire ground layer":"Seismic shock layer")?.GetComponent<MeshFilter>();if(sf!=null){frame.shockCount=WriteMesh(sf,w);var block=new MaterialPropertyBlock();sf.GetComponent<MeshRenderer>().GetPropertyBlock(block);frame.shape=block.GetVector("_Shape");frame.clock=block.GetVector("_Clock");frame.style=block.GetVector("_Style");frame.impact=block.GetVector("_Impact");frame.limits=block.GetFloatArray("_Limits");}
     frame.particleOffsets=new int[3];frame.particleCounts=new int[3];for(int i=0;i<3;i++){frame.particleOffsets[i]=(int)stream.Position;if(particles[i]!=null)frame.particleCounts[i]=WriteParticles(particles[i],camera,w);}frames.Add(frame);
    }
   }
   outputs.Add(new Effect{name=job.name,skill=job.skill,file="effects/"+file,duration=total,fps=30,eventDuration=duration,startRadius=start,endRadius=end,speed=speed,particleMaterials=materialIds,particleBillboards=new[]{true,job.particles[1]?.mesh==0,true},frames=frames.ToArray()});UnityEngine.Object.DestroyImmediate(go);UnityEngine.Object.DestroyImmediate(p);UnityEngine.Object.DestroyImmediate(shock);Debug.Log("EFFECT "+job.name+" baked "+frames.Count);
  }
  UnityEngine.Object.DestroyImmediate(cameraObject);File.WriteAllText(Path.Combine(folder,"index.json"),JsonUtility.ToJson(new Index{effects=outputs.ToArray()}));
 }
 static void Vertex(BinaryWriter w,Vector3 v,Vector3 n,Color c,Vector4 uv){w.Write(-v.x);w.Write(v.y);w.Write(v.z);w.Write(-n.x);w.Write(n.y);w.Write(n.z);w.Write(c.r);w.Write(c.g);w.Write(c.b);w.Write(c.a);w.Write(uv.x);w.Write(uv.y);w.Write(uv.z);w.Write(uv.w);}
 static int WriteMesh(MeshFilter filter,BinaryWriter w){
  var m=filter.sharedMesh;var renderer=filter.GetComponent<MeshRenderer>();if(m==null||!renderer.enabled)return 0;int count=m.GetSubMesh(0).vertexCount;if(count<=0)return 0;
  var v=m.vertices;var n=m.normals;var c=m.colors;var uv=new List<Vector4>();m.GetUVs(0,uv);for(int i=0;i<count;i++)Vertex(w,v[i],n.Length>i?n[i]:Vector3.up,c.Length>i?c[i]:Color.white,uv.Count>i?uv[i]:Vector4.zero);return count;
 }
 static int WriteParticles(ParticleSystem ps,Camera camera,BinaryWriter w){
  if(ps.particleCount==0)return 0;var mesh=new Mesh();ps.GetComponent<ParticleSystemRenderer>().BakeMesh(mesh,camera,false);var v=mesh.vertices;var colors=mesh.colors;var uv=mesh.uv;var triangles=mesh.triangles;var normals=mesh.normals;bool billboard=ps.GetComponent<ParticleSystemRenderer>().renderMode!=ParticleSystemRenderMode.Mesh;
  for(int i=0;i<triangles.Length;i++){int j=triangles[i],b=j/4*4;if(!billboard){Vertex(w,v[j],normals[j],colors.Length>j?colors[j]:Color.white,new Vector4(uv[j].x,uv[j].y,0,0));continue;}Vector3 center=(v[b]+v[b+1]+v[b+2]+v[b+3])*.25f;Vector3 diff=v[j]-center;var extent=new Vector3(Vector3.Dot(diff,camera.transform.right),Vector3.Dot(diff,camera.transform.up),0);Vertex(w,center,extent,colors.Length>j?colors[j]:Color.white,new Vector4(uv[j].x,uv[j].y,0,0));}
  int count=triangles.Length;UnityEngine.Object.DestroyImmediate(mesh);return count;
 }
}
