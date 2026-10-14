using System;
using UnityEngine;

[Serializable]
public struct ProceduralArenaPiece
{
	public ProceduralPropDefinition Prop;

	[Tooltip("Metres from the arena centre to the prop's footprint centre.")]
	[Min(0f)]
	public float Radius;

	[Tooltip("Degrees around the centre as seen on screen: 0 = far side (away from the camera), 90 = right, -90 = left, 180 = nearest the camera. One prop per angle.")]
	public float[] Angles;

	[Tooltip("Degrees added to the facing. 0 turns the prop's front (local -Z) toward the arena centre.")]
	public float Yaw;

	[Tooltip("Uniform scale; blocking boxes scale with it.")]
	[Min(0.25f)]
	public float Scale;
}
