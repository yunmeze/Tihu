using System;
using UnityEngine;

[CreateAssetMenu(menuName = "Desktop Hellfarmer/Zones/Procedural Boss Arena")]
public sealed class ProceduralBossArenaSettings : ScriptableObject
{
	[Header("Floor")]
	[Tooltip("Arena floor material (Procedural Arena Floor shader).")]
	public Material FloorMaterial;

	[Tooltip("Paved floor radius in metres. Wider than the visible ground around the hero, so the fight happens on the arena rather than at its edge.")]
	[Range(3f, 12f)]
	public float FloorRadius = 10f;

	[Header("Site")]
	[Tooltip("Radius in tiles paved as solid, walkable ground (water, pits and coast are filled) and cleared of ordinary props. Keep it past the floor radius.")]
	[Range(3f, 7f)]
	public float ClearRadius = 6f;

	[Tooltip("Metres from the centre at which the arriving hero wakes the waiting boss; a hit wakes it too.")]
	[Min(1f)]
	public float WakeRadius = 3.5f;

	[Tooltip("Share of the way the camera focus moves from the hero toward the arena centre while the hero fights on the floor. The small visible cut then shows the colossus and monuments around the fight.")]
	[Range(0f, 0.9f)]
	public float FramingPull = 0.6f;

	[Header("Set pieces")]
	public ProceduralArenaPiece[] Pieces = Array.Empty<ProceduralArenaPiece>();

	public bool IsValid => FloorMaterial != null;

	private void OnValidate()
	{
		FloorRadius = Mathf.Clamp(FloorRadius, 3f, 12f);
		ClearRadius = Mathf.Clamp(ClearRadius, 3f, 7f);
		WakeRadius = Mathf.Max(1f, WakeRadius);
		FramingPull = Mathf.Clamp(FramingPull, 0f, 0.9f);
		if (Pieces == null)
		{
			Pieces = Array.Empty<ProceduralArenaPiece>();
		}
		for (int i = 0; i < Pieces.Length; i++)
		{
			if (Pieces[i].Angles == null)
			{
				Pieces[i].Angles = Array.Empty<float>();
			}
			if (Pieces[i].Scale < 0.25f)
			{
				Pieces[i].Scale = 1f;
			}
		}
	}
}
