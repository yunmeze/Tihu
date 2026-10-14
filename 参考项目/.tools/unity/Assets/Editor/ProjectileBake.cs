using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
public static class ProjectileBake {
 [Serializable]public class Frame {public int offset,count;}
 [Serializable]public class Clip {public string name,file;public float fps=30;public Frame[] frames;}
 [Serializable]public class Index {public int stride=22;public Clip[] clips;}
 static void Call(object o,string method,float dt)=>o.GetType().GetMethod(method,BindingFlags.Instance|BindingFlags.NonPublic).Invoke(o,new object[]{dt});
 public static void Run(){string root=Path.GetFullPath(Path.Combine(Application.dataPath,"../../..")),folder=Path.Combine(root,"public/assets/projectiles");Directory.CreateDirectory(folder);var outputs=new List<Clip>();
  foreach(string phase in new[]{"charge","flight","impact"}){var go=new GameObject(phase,typeof(MeshFilter),typeof(MeshRenderer));var effect=go.AddComponent<FireballProjectileVisual>();typeof(FireballProjectileVisual).GetField("_random",BindingFlags.Instance|BindingFlags.NonPublic).SetValue(effect,2654435769u);var frames=new List<Frame>();var build=typeof(FireballProjectileVisual).GetMethod("Build",BindingFlags.Instance|BindingFlags.NonPublic);
   if(phase!="charge"){effect.Launch(Vector3.zero,1);effect.Move(Vector3.zero,Vector3.forward);if(phase=="impact")effect.Impact();}
   using(var stream=File.Create(Path.Combine(folder,phase+".bin")))using(var writer=new BinaryWriter(stream))for(int f=0;f<=60;f++){float dt=1f/30,time=f/30f;Vector3 center=Vector3.zero;if(phase=="charge"){effect.Charge(Vector3.zero,1,Mathf.Clamp01(time));Call(effect,"EmitCharge",dt);}else if(phase=="flight"){center=Vector3.forward*time*10;effect.Move(center,Vector3.forward);Call(effect,"EmitFlight",dt);}Call(effect,"Simulate",dt);build.Invoke(effect,null);var mesh=go.GetComponent<MeshFilter>().sharedMesh;var pos=mesh.vertices;var normal=mesh.normals;var tangent=mesh.tangents;var color=mesh.colors;var uv=new List<Vector4>();var uv1=new List<Vector4>();mesh.GetUVs(0,uv);mesh.GetUVs(1,uv1);var frame=new Frame{offset=(int)stream.Position,count=mesh.triangles.Length};foreach(int i in mesh.triangles){var p=pos[i]-center;writer.Write(-p.x);writer.Write(p.y);writer.Write(p.z);writer.Write(-normal[i].x);writer.Write(normal[i].y);writer.Write(normal[i].z);writer.Write(-tangent[i].x);writer.Write(tangent[i].y);writer.Write(tangent[i].z);writer.Write(tangent[i].w);writer.Write(color[i].r);writer.Write(color[i].g);writer.Write(color[i].b);writer.Write(color[i].a);foreach(var t in new[]{uv[i],uv1[i]}){writer.Write(t.x);writer.Write(t.y);writer.Write(t.z);writer.Write(t.w);}}frames.Add(frame);}
   outputs.Add(new Clip{name=phase,file="projectiles/"+phase+".bin",frames=frames.ToArray()});UnityEngine.Object.DestroyImmediate(go);Debug.Log("PROJECTILE "+phase);}
  File.WriteAllText(Path.Combine(folder,"index.json"),JsonUtility.ToJson(new Index{clips=outputs.ToArray()}));EditorApplication.Exit(0);
 }
}
