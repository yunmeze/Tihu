using System.Collections.Generic;
using Scellecs.Morpeh;
using UnityEngine;

public struct CombatSkillPulse : IComponent
{
	public CombatSkillCast Cast;

	public Vector3 Origin;

	public Vector3 Direction;

	public float Radius;

	public float Angle;

	public float InnerRadius;

	public float Multiplier;

	public bool Secondary;

	public bool Opposite;

	public bool Initial;

	public bool LegendarySecondary;

	public bool LegendaryProcessed;

	public float WaveLength;

	public float WaveWidth;

	public HashSet<Entity> WaveHits;

	public bool ActionGeometry;

	public Vector3 OcclusionOrigin;

	public bool PresentationOnly;
}
