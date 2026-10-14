using UnityEngine;
namespace Scellecs.Morpeh {
 public interface IComponent{}
 public struct Entity {public bool IsNullOrDisposed()=>false;}
 public class World {public static World Default=new World();public Stash<T> GetStash<T>()where T:new()=>new Stash<T>();}
 public class Stash<T>where T:new(){static T value=new T();public bool Has(Entity e)=>false;public ref T Get(Entity e)=>ref value;}
}
public struct GameObjectComponent {public GameObject GameObject;}
public struct CrowdActorComponent {public CombatSkillCast Mark;}
public sealed class CombatSkillCast {public int Id;public Scellecs.Morpeh.Entity Source;public CombatSkillDefinition Skill;}
public sealed class CombatSkillTimeline {public double Time;public int Generation;public static bool Alive(Scellecs.Morpeh.World w,CombatSkillCast c)=>true;}
public static class PackEncounterService {public static bool Alive(Scellecs.Morpeh.World w,Scellecs.Morpeh.Entity e)=>true;}
public static class CombatSkillGeometry {public static bool Occluded(Vector3 a,Vector3 b,out float distance){distance=0;return false;}}
