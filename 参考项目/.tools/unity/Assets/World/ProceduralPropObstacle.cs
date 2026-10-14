using System;
using UnityEngine;

[Serializable]
public struct ProceduralPropObstacle
{
	[Tooltip("Box centre in metres, prop-local X/Z relative to the footprint centre, before rotation and scale.")]
	public Vector2 Center;

	[Tooltip("Box size in metres along prop-local X/Z.")]
	public Vector2 Size;
}
