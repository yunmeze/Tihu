using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditorInternal;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;
public static class Bake {
 public static void AvatarTemplate(){var root=new GameObject("root");var avatar=AvatarBuilder.BuildGenericAvatar(root,"");AssetDatabase.CreateAsset(avatar,"Assets/SampleAvatar.asset");AssetDatabase.SaveAssets();string output=Path.Combine(Root,".tools/sample-avatar");Directory.CreateDirectory(output);BuildPipeline.BuildAssetBundles(output,new[]{new AssetBundleBuild{assetBundleName="sample-avatar.bundle",assetNames=new[]{"Assets/SampleAvatar.asset"}}},BuildAssetBundleOptions.ChunkBasedCompression,BuildTarget.StandaloneWindows64);}
 public static void Test(){foreach(var file in new[]{"sample/sample.bundle","repacked-sample.bundle","original-motion.bundle"}){var b=AssetBundle.LoadFromFile(Path.Combine(Root,".tools/"+file));Debug.Log("TEST "+file+" "+(b!=null));if(b!=null)b.Unload(true);}var objects=InternalEditorUtility.LoadSerializedFileAndForget(Path.Combine(Root,".tools/motion.assets"));Debug.Log("LOOSE "+objects.Length+" "+string.Join(",",objects.Select(o=>o.GetType().Name+":"+o.name)));}
 public static void All(){WorldBake.Run();Run();}
 [Serializable] public class Catalog { public Actor[] actors; }
 [Serializable] public class Actor { public string name,id,avatar; public Node[] nodes; }
 [Serializable] public class Node { public string id,name,path; public int parent; public float[] position,rotation,scale; }
 [Serializable] public class Motion { public string name,file,source;public float duration;public int frames,bones; }
 [Serializable] public class ActorMotions { public string id;public Motion[] clips; }
 [Serializable] public class Index { public ActorMotions[] actors; }
 static string Root => Path.GetFullPath(Path.Combine(Application.dataPath,"../../.."));
 public static void Inspect() {
  string data=Path.Combine(Root,"reference/Desktop Hellfarmer/Desktop Hellfarmer_Data");
  var objects=InternalEditorUtility.LoadSerializedFileAndForget(Path.Combine(data,"resources.assets"));
  Debug.Log("LOADED "+objects.Length+" objects "+string.Join(",",objects.GroupBy(o=>o.GetType().Name).Select(g=>g.Key+":"+g.Count())));
  foreach(var a in objects.OfType<AnimationClip>())Debug.Log("CLIP "+a.name+" "+a.length);
 }
 public static void Run() {
  string data=Path.Combine(Root,"reference/Desktop Hellfarmer/Desktop Hellfarmer_Data");
  var bundle=AssetBundle.LoadFromFile(Path.Combine(Root,".tools/original-motion.bundle"));
  if(bundle==null)throw new Exception("Cannot load original motion bundle");
  var clips=bundle.LoadAllAssets<AnimationClip>();var avatars=bundle.LoadAllAssets<Avatar>();
  if(clips.Length!=40)throw new Exception("Expected 40 original clips, imported "+clips.Length);
  var catalog=JsonUtility.FromJson<Catalog>(File.ReadAllText(Path.Combine(Root,"public/assets/catalog.json")));
  var results=new List<ActorMotions>();string output=Path.Combine(Root,"public/assets/motions");Directory.CreateDirectory(output);
  foreach(var actor in catalog.actors) {
   var transforms=new Transform[actor.nodes.Length];
   for(int i=0;i<transforms.Length;i++){
    var n=actor.nodes[i];var t=new GameObject(n.name).transform;transforms[i]=t;if(n.parent>=0)t.SetParent(transforms[n.parent],false);
    t.localPosition=new Vector3(-n.position[0],n.position[1],n.position[2]);t.localRotation=new Quaternion(n.rotation[0],-n.rotation[1],-n.rotation[2],n.rotation[3]);t.localScale=new Vector3(n.scale[0],n.scale[1],n.scale[2]);
   }
   var root=transforms[0].gameObject; var animator=root.AddComponent<Animator>();
   // Avatar uses original hierarchy path names. Rebuild a humanoid avatar if
   // native serialized loader does not expose the original standalone Avatar.
   string avatarPath="avatar/"+actor.avatar.Split(':').Last();animator.avatar=bundle.LoadAsset<Avatar>(avatarPath);
   if(animator.avatar==null){
    var human=new List<HumanBone>();string[] names={"Hips","Spine","Chest","UpperChest","Neck","Head","LeftShoulder","LeftUpperArm","LeftLowerArm","LeftHand","RightShoulder","RightUpperArm","RightLowerArm","RightHand","LeftUpperLeg","LeftLowerLeg","LeftFoot","LeftToes","RightUpperLeg","RightLowerLeg","RightFoot","RightToes"};
    string[] source={"Hips","Spine","Spine1","Spine2","Neck","Head","LeftShoulder","LeftArm","LeftForeArm","LeftHand","RightShoulder","RightArm","RightForeArm","RightHand","LeftUpLeg","LeftLeg","LeftFoot","LeftToeBase","RightUpLeg","RightLeg","RightFoot","RightToeBase"};
    for(int i=0;i<names.Length;i++){var t=transforms.FirstOrDefault(t=>t.name.EndsWith(":"+source[i])||t.name==source[i]);if(t!=null)human.Add(new HumanBone{humanName=names[i],boneName=t.name,limit=new HumanLimit{useDefaultValues=true}});}
    animator.avatar=AvatarBuilder.BuildHumanAvatar(root,new HumanDescription{human=human.ToArray(),skeleton=transforms.Select(t=>new SkeletonBone{name=t.name,position=t.localPosition,rotation=t.localRotation,scale=t.localScale}).ToArray(),upperArmTwist=.5f,lowerArmTwist=.5f,upperLegTwist=.5f,lowerLegTwist=.5f,armStretch=.05f,legStretch=.05f,feetSpacing=0});
   }
   animator.applyRootMotion=false; animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;
   if(animator.avatar==null||!animator.avatar.isValid)throw new Exception("Invalid avatar "+actor.name);
   var restP=transforms.Select(t=>t.localPosition).ToArray();var restQ=transforms.Select(t=>t.localRotation).ToArray();var restS=transforms.Select(t=>t.localScale).ToArray();var motions=new List<Motion>();
   for(int c=0;c<clips.Length;c++){
    var clip=clips[c];for(int n=0;n<transforms.Length;n++){transforms[n].localPosition=restP[n];transforms[n].localRotation=restQ[n];transforms[n].localScale=restS[n];}animator.Rebind();
    var graph=PlayableGraph.Create("OriginalClipBake");graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);
    try{
     var playable=AnimationClipPlayable.Create(graph,clip);playable.SetApplyFootIK(false);var outp=AnimationPlayableOutput.Create(graph,"Motion",animator);outp.SetSourcePlayable(playable);graph.Play();
     int frames=Math.Max(2,Mathf.CeilToInt(clip.length*30)+1);string file=actor.id.Replace(':','_')+"_"+c+".bin";
     using(var stream=File.Create(Path.Combine(output,file)))using(var writer=new BinaryWriter(stream)){
      for(int f=0;f<frames;f++){playable.SetTime(Math.Min(f/30f,clip.length));graph.Evaluate(0);transforms[0].localPosition=Vector3.zero;transforms[0].localRotation=Quaternion.identity;
       for(int n=0;n<transforms.Length;n++){var p=transforms[n].localPosition;var q=transforms[n].localRotation;writer.Write(-p.x);writer.Write(p.y);writer.Write(p.z);writer.Write(q.x);writer.Write(-q.y);writer.Write(-q.z);writer.Write(q.w);}
      }
     }
     long local=Enumerable.Range(426,40).First(id=>bundle.LoadAsset<AnimationClip>("animationclip/"+id)==clip);
     motions.Add(new Motion{name=clip.name,file="motions/"+file,source=local.ToString(),duration=clip.length,frames=frames,bones=transforms.Length});
    }finally{graph.Destroy();}
   }
   results.Add(new ActorMotions{id=actor.id,clips=motions.ToArray()});UnityEngine.Object.DestroyImmediate(root);Debug.Log("BAKED "+actor.name+" "+motions.Count);
  }
  File.WriteAllText(Path.Combine(output,"index.json"),JsonUtility.ToJson(new Index{actors=results.ToArray()}));
 }
}
