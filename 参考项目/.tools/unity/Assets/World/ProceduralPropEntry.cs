using System;
using UnityEngine;

[Serializable]
public struct ProceduralPropEntry
{
	public ProceduralPropDefinition Definition;

	[Tooltip("Relative chance among props of the same placement class in this zone.")]
	[Min(0f)]
	public float Weight;
}
