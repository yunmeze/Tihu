using System;
using UnityEngine;

[CreateAssetMenu(menuName = "Desktop Hellfarmer/Zones/Procedural Prop")]
public sealed class ProceduralPropDefinition : ScriptableObject
{
	[Header("Presentation")]
	public Mesh Mesh;

	[Tooltip("One material per mesh submesh, in submesh order.")]
	public Material[] Materials;

	[Tooltip("Uniform random scale range. Blocking boxes scale with the visual.")]
	public Vector2 ScaleRange = new Vector2(0.9f, 1.1f);

	[Tooltip("Single-tile props may turn to any yaw; others turn in 90-degree steps so the footprint stays on the grid.")]
	public bool FreeRotation;

	[Header("Placement")]
	public ProceduralPropPlacement Placement;

	[Tooltip("Occupied tiles along prop-local X (width) and Z (depth) before rotation.")]
	public Vector2Int Footprint = Vector2Int.one;

	[Tooltip("Field and roadside props with this flag carve navigation and block combat lines with their boxes. Boundary and scatter props never block: boundary tiles are already non-walkable.")]
	public bool BlocksMovement = true;

	public ProceduralPropObstacle[] Obstacles = Array.Empty<ProceduralPropObstacle>();

	[Tooltip("Strength of bare, darker ground under the footprint in the terrain layout.")]
	[Range(0f, 1f)]
	public float GroundContact = 0.6f;

	[Header("Light")]
	[Tooltip("Flickering point light cast on nearby ground and props (black = none).")]
	[ColorUsage(false, true)]
	public Color LightColor = Color.black;

	[Tooltip("Light reach in metres before prop scale.")]
	[Min(0f)]
	public float LightRadius = 5f;

	[Tooltip("Light source in metres, prop-local X/Y/Z from the footprint centre on the ground.")]
	public Vector3 LightOffset = new Vector3(0f, 1.2f, 0f);

	public bool HasLight
	{
		get
		{
			if (LightRadius > 0f)
			{
				return LightColor.maxColorComponent > 0.001f;
			}
			return false;
		}
	}

	public bool IsValid
	{
		get
		{
			if (Mesh != null && Materials != null && Materials.Length != 0 && Footprint.x >= 1)
			{
				return Footprint.y >= 1;
			}
			return false;
		}
	}

	public bool Blocks
	{
		get
		{
			if (BlocksMovement)
			{
				if (Placement != ProceduralPropPlacement.Field)
				{
					return Placement == ProceduralPropPlacement.Roadside;
				}
				return true;
			}
			return false;
		}
	}

	private void OnValidate()
	{
		Footprint = new Vector2Int(Mathf.Clamp(Footprint.x, 1, 6), Mathf.Clamp(Footprint.y, 1, 6));
		if (Footprint != Vector2Int.one)
		{
			FreeRotation = false;
		}
		ScaleRange = new Vector2(Mathf.Clamp(ScaleRange.x, 0.25f, 4f), Mathf.Clamp(ScaleRange.y, 0.25f, 4f));
		if (ScaleRange.y < ScaleRange.x)
		{
			ScaleRange.y = ScaleRange.x;
		}
		if (Obstacles == null)
		{
			Obstacles = Array.Empty<ProceduralPropObstacle>();
		}
		LightRadius = Mathf.Max(0f, LightRadius);
	}
}
