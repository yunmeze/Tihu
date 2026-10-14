using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.AI;
public static class WorldBake {
 [Serializable]public class Jobs {public Zone[] zones;}
 [Serializable]public class Zone {public string id,name,json;public Prop[] props;}
 [Serializable]public class Prop {public string id,json,mesh;public float weight;public string[] materials;}
 [Serializable]public class Placement {public int entry;public float x,z,yaw,scale;}
 [Serializable]public class Chunk {public string file;public int vertices,indices,uvWidth=4;public bool liquid;}
 [Serializable]public class Result {public string id,name;public int size,seed;public float tileSize;public int[] tiles;public byte[] layout;public bool[] walkable;public float[] navigationVertices,obstacles;public int[] navigationIndices;public float[] clearings;public Placement[] props;public Chunk[] chunks;}
 public static void Run(){
  string project=Path.GetFullPath(Path.Combine(Application.dataPath,".."));string root=Path.GetFullPath(Path.Combine(project,"../.."));
  var jobs=JsonUtility.FromJson<Jobs>(File.ReadAllText(Path.Combine(project,"world-jobs.json")));string output=Path.Combine(root,"public/assets/worlds");Directory.CreateDirectory(output);
  foreach(var zone in jobs.zones){
   var s=ScriptableObject.CreateInstance<ProceduralZoneSettings>();JsonUtility.FromJsonOverwrite(zone.json,s);
   s.Props=zone.props.Select(p=>{var d=ScriptableObject.CreateInstance<ProceduralPropDefinition>();JsonUtility.FromJsonOverwrite(p.json,d);d.Mesh=new Mesh();d.Materials=new Material[1];return new ProceduralPropEntry{Definition=d,Weight=p.weight};}).ToArray();
   var map=ProceduralTileMap.Generate(s,s.BaseSeed);var props=ProceduralPropLayout.Generate(map,s);var chunks=new List<Chunk>();
   var r=new Result{id=zone.id,name=zone.name,size=map.Size,seed=map.Seed,tileSize=map.TileSize,tiles=new int[map.Size*map.Size],clearings=map.Clearings.SelectMany(p=>new[]{-map.WorldPosition(p.x,p.y).x,map.WorldPosition(p.x,p.y).z}).ToArray(),props=props.Instances.Select(p=>new Placement{entry=p.Entry,x=-p.Center.x,z=p.Center.y,yaw=-p.Yaw,scale=p.Scale}).ToArray()};
   r.layout=new byte[map.Size*map.Size*4];for(int z=0;z<map.Size;z++)for(int x=0;x<map.Size;x++){int j=z*map.Size+x;var kind=map.KindAt(x,z);r.tiles[j]=(int)kind;r.layout[j*4]=(byte)(kind==ProceduralTileKind.Path?255:0);r.layout[j*4+1]=(byte)(kind==ProceduralTileKind.Clearing?255:0);r.layout[j*4+2]=(byte)(kind==ProceduralTileKind.Void||kind==ProceduralTileKind.Boundary?255:kind==ProceduralTileKind.Liquid||kind==ProceduralTileKind.Chasm?170:kind==ProceduralTileKind.Grass&&map.VariationAt(x,z,911)<s.RoughPatchChance?150:0);}
   foreach(var instance in props.Instances){byte contact=(byte)Mathf.RoundToInt(props.Definition(instance.Entry).GroundContact*255);for(int z=instance.Cells.yMin;z<instance.Cells.yMax;z++)for(int x=instance.Cells.xMin;x<instance.Cells.xMax;x++)r.layout[(z*map.Size+x)*4+3]=Math.Max(contact,r.layout[(z*map.Size+x)*4+3]);}
   var nv=new List<Vector3>();var ni=new List<int>();r.walkable=new bool[map.Size*map.Size];float half=map.TileSize*.5f;for(int z=0;z<map.Size;z++)for(int x=0;x<map.Size;x++){r.walkable[z*map.Size+x]=map.IsWalkable(x,z);if(!map.IsWalkable(x,z))continue;var v=map.WorldPosition(x,z);int j=nv.Count;nv.Add(v+new Vector3(-half,0,-half));nv.Add(v+new Vector3(-half,0,half));nv.Add(v+new Vector3(half,0,half));nv.Add(v+new Vector3(half,0,-half));ni.AddRange(new[]{j,j+1,j+2,j,j+2,j+3});}
   var navMesh=new Mesh{indexFormat=UnityEngine.Rendering.IndexFormat.UInt32};navMesh.SetVertices(nv);navMesh.SetTriangles(ni,0);navMesh.RecalculateBounds();var sources=new List<NavMeshBuildSource>{new NavMeshBuildSource{shape=NavMeshBuildSourceShape.Mesh,sourceObject=navMesh,transform=Matrix4x4.identity,area=0}};var obstacles=new List<float>();foreach(var instance in props.Instances){var def=props.Definition(instance.Entry);if(!def.Blocks)continue;foreach(var obstacle in def.Obstacles){ProceduralPropLayout.ObstacleBox(instance,obstacle,out var center,out var size);obstacles.AddRange(new[]{-center.x,center.y,size.x,size.y});sources.Add(new NavMeshBuildSource{shape=NavMeshBuildSourceShape.Box,area=1,size=new Vector3(size.x,2,size.y),transform=Matrix4x4.Translate(new Vector3(center.x,.8f,center.y))});}}
   var nav=NavMeshBuilder.BuildNavMeshData(NavMesh.GetSettingsByIndex(0),sources,new Bounds(Vector3.zero,new Vector3(map.Size*map.TileSize+4,10,map.Size*map.TileSize+4)),Vector3.zero,Quaternion.identity);var navInstance=NavMesh.AddNavMeshData(nav);var tri=NavMesh.CalculateTriangulation();r.navigationVertices=tri.vertices.SelectMany(v=>new[]{-v.x,v.y,v.z}).ToArray();r.navigationIndices=tri.indices;r.obstacles=obstacles.ToArray();navInstance.Remove();UnityEngine.Object.DestroyImmediate(navMesh);UnityEngine.Object.DestroyImmediate(nav);
   int i=0;foreach(var chunk in ProceduralHazardVisuals.Build(map,s)){foreach(var m in new[]{chunk.Ground,chunk.Liquid}){if(m==null)continue;string file=zone.id.Replace(':','_')+"_"+(i++)+".bin";var v=m.vertices;var n=m.normals;var uv=new List<Vector4>();m.GetUVs(0,uv);var indices=m.triangles;
    using(var stream=File.Create(Path.Combine(output,file)))using(var w=new BinaryWriter(stream)){for(int j=0;j<v.Length;j++){w.Write(-v[j].x);w.Write(v[j].y);w.Write(v[j].z);}for(int j=0;j<n.Length;j++){w.Write(-n[j].x);w.Write(n[j].y);w.Write(n[j].z);}for(int j=0;j<v.Length;j++){w.Write(uv.Count>j?uv[j].x:0);w.Write(uv.Count>j?uv[j].y:0);w.Write(uv.Count>j?uv[j].z:0);w.Write(uv.Count>j?uv[j].w:0);}for(int j=0;j<indices.Length;j+=3){w.Write(indices[j+2]);w.Write(indices[j+1]);w.Write(indices[j]);}}
    chunks.Add(new Chunk{file="worlds/"+file,vertices=v.Length,indices=indices.Length,liquid=m==chunk.Liquid});}}
   r.chunks=chunks.ToArray();File.WriteAllText(Path.Combine(output,zone.id.Replace(':','_')+".json"),JsonUtility.ToJson(r));Debug.Log("WORLD "+zone.name+" props="+r.props.Length+" chunks="+chunks.Count);
  }
  var sample=new AnimationClip();AssetDatabase.CreateAsset(sample,"Assets/Sample.anim");AssetDatabase.SaveAssets();string sampleDir=Path.Combine(root,".tools/sample");Directory.CreateDirectory(sampleDir);BuildPipeline.BuildAssetBundles(sampleDir,new[]{new AssetBundleBuild{assetBundleName="sample.bundle",assetNames=new[]{"Assets/Sample.anim"}}},BuildAssetBundleOptions.ChunkBasedCompression,BuildTarget.StandaloneWindows64);
 }
}
