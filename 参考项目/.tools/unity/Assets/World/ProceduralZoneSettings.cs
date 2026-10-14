using System;
using UnityEngine;
using UnityEngine.Serialization;

[CreateAssetMenu(menuName = "Desktop Hellfarmer/Zones/Procedural Zone Settings")]
public sealed class ProceduralZoneSettings : ScriptableObject
{
	[Header("Deterministic layout")]
	[Range(25f, 129f)]
	public int MapSize = 49;

	[Min(0.5f)]
	public float TileSize = 2f;

	[Range(3f, 9f)]
	public int ClearingGridSize = 5;

	[Tooltip("Tile spacing between encounters. ClearingSpacing * TileSize and the outer clearing extent must leave hidden anchors beyond the largest supported camera viewport.")]
	[Min(5f)]
	public int ClearingSpacing = 8;

	[Range(1f, 4f)]
	public int ClearingRadius = 2;

	public int BaseSeed = 73451;

	[Header("Tile geometry")]
	[Min(0.1f)]
	public float TileDepth = 0.6f;

	[Header("Ground")]
	[Tooltip("Layered terrain material (Procedural Terrain shader): soil, cover, path, clearing and rough layers blend from the generated tile layout.")]
	public Material TerrainMaterial;

	[Tooltip("Share of ordinary field tiles that read as rocky rough ground in the layout.")]
	[Range(0f, 0.5f)]
	public float RoughPatchChance = 0.08f;

	[Header("Environment props")]
	public ProceduralPropEntry[] Props = Array.Empty<ProceduralPropEntry>();

	[Tooltip("Chance per field tile to attempt a Field prop.")]
	[FormerlySerializedAs("DecorationChance")]
	[Range(0f, 0.6f)]
	public float FieldPropDensity = 0.1f;

	[Tooltip("Chance per tile beside a path to attempt a Roadside prop.")]
	[Range(0f, 1f)]
	public float RoadsidePropDensity = 0.2f;

	[Tooltip("Chance per non-walkable coast tile to attempt a Boundary set piece.")]
	[Range(0f, 1f)]
	public float BoundaryPropDensity = 0.35f;

	[Tooltip("Chance per field tile beside sunken ground to place a non-blocking Shore prop.")]
	[Range(0f, 1f)]
	public float ShorePropDensity = 0.35f;

	[Tooltip("Chance per remaining field/coast tile to place non-blocking Scatter debris.")]
	[Range(0f, 1f)]
	public float ScatterDensity = 0.2f;

	[Header("Impassable hazards")]
	[Tooltip("Rivers cross the island edge to edge; path tiles on a river become bridges (Bridge props).")]
	public ProceduralHazardKind RiverKind;

	[Range(0f, 3f)]
	public int RiverCount = 1;

	[Range(1f, 3f)]
	public int RiverWidth = 1;

	[Tooltip("Pools or pits in open field, always a tile away from paths and clearings.")]
	public ProceduralHazardKind PoolKind;

	[Range(0f, 16f)]
	public int PoolCount = 4;

	[Tooltip("Pool radius in tiles.")]
	[Range(1f, 3.5f)]
	public float PoolRadius = 1.6f;

	[Tooltip("Liquid surface material (Procedural Liquid shader).")]
	public Material LiquidMaterial;

	[Tooltip("Metres from the ground plane down to the liquid surface.")]
	[Range(0.05f, 1.5f)]
	public float LiquidLevel = 0.35f;

	[Tooltip("Metres from the ground plane down to the liquid bed.")]
	[Range(0.2f, 4f)]
	public float LiquidBedDepth = 1.2f;

	[Tooltip("Tiles over which a liquid bank descends to its bed.")]
	[Range(0.1f, 1f)]
	public float LiquidBankWidth = 0.55f;

	[Tooltip("Metres from the ground plane down to a chasm floor.")]
	[Range(1f, 20f)]
	public float ChasmDepth = 7f;

	[Tooltip("Tiles over which a chasm wall drops; small values give cliffs.")]
	[Range(0.05f, 1f)]
	public float ChasmBankWidth = 0.22f;

	[Header("Boss arena")]
	[Tooltip("Arena stamped on hidden ground when the zone boss is due. Empty keeps the classic boss entry transition.")]
	public ProceduralBossArenaSettings BossArena;

	[Header("Prop look")]
	[Tooltip("Multiplies every prop material's albedo in this zone.")]
	public Color PropTint = Color.white;

	[Tooltip("Tileable albedo (height in alpha) settling on upward-facing prop surfaces: moss, ash, grime.")]
	public Texture2D PropCoverMap;

	public Color PropCoverTint = Color.white;

	[Range(0f, 1f)]
	public float PropCoverAmount = 0.35f;

	[Tooltip("World metres per repeat of the prop cover texture.")]
	[Min(0.1f)]
	public float PropCoverTiling = 2f;

	public void Validate()
	{
		MapSize = Mathf.Clamp(MapSize, 25, 129) | 1;
		TileSize = ClampFinite(TileSize, 0.5f, 8f, 2f);
		ClearingRadius = Mathf.Clamp(ClearingRadius, 1, 4);
		ClearingSpacing = Mathf.Clamp(ClearingSpacing, ClearingRadius * 2 + 3, 24);
		ClearingGridSize = Mathf.Clamp(ClearingGridSize, 3, 9);
		if ((ClearingGridSize & 1) == 0)
		{
			ClearingGridSize--;
		}
		int b = (ClearingGridSize - 1) * ClearingSpacing + 2 * (ClearingRadius + 4) + 1;
		MapSize = Mathf.Clamp(Mathf.Max(MapSize, b), 25, 129) | 1;
		int b2 = (MapSize / 2 - ClearingRadius - 4) / ClearingSpacing * 2 + 1;
		ClearingGridSize = Mathf.Clamp(ClearingGridSize, 3, Mathf.Min(9, b2));
		TileDepth = ClampFinite(TileDepth, 0.1f, 3f, 0.6f);
		RoughPatchChance = ClampFinite(RoughPatchChance, 0f, 0.5f, 0.08f);
		FieldPropDensity = ClampFinite(FieldPropDensity, 0f, 0.6f, 0.1f);
		RoadsidePropDensity = ClampFinite(RoadsidePropDensity, 0f, 1f, 0.2f);
		BoundaryPropDensity = ClampFinite(BoundaryPropDensity, 0f, 1f, 0.35f);
		ScatterDensity = ClampFinite(ScatterDensity, 0f, 1f, 0.2f);
		ShorePropDensity = ClampFinite(ShorePropDensity, 0f, 1f, 0.35f);
		RiverCount = Mathf.Clamp(RiverCount, 0, 3);
		RiverWidth = Mathf.Clamp(RiverWidth, 1, 3);
		PoolCount = Mathf.Clamp(PoolCount, 0, 16);
		PoolRadius = ClampFinite(PoolRadius, 1f, 3.5f, 1.6f);
		LiquidLevel = ClampFinite(LiquidLevel, 0.05f, 1.5f, 0.35f);
		LiquidBedDepth = ClampFinite(LiquidBedDepth, LiquidLevel + 0.1f, 4f, 1.2f);
		LiquidBankWidth = ClampFinite(LiquidBankWidth, 0.1f, 1f, 0.55f);
		ChasmDepth = ClampFinite(ChasmDepth, 1f, 20f, 7f);
		ChasmBankWidth = ClampFinite(ChasmBankWidth, 0.05f, 1f, 0.22f);
		PropCoverTiling = ClampFinite(PropCoverTiling, 0.1f, 50f, 2f);
		if (Props == null)
		{
			Props = Array.Empty<ProceduralPropEntry>();
		}
	}

	private void OnValidate()
	{
		Validate();
	}

	private static float ClampFinite(float value, float minimum, float maximum, float fallback)
	{
		if (!float.IsNaN(value) && !float.IsInfinity(value))
		{
			return Mathf.Clamp(value, minimum, maximum);
		}
		return fallback;
	}
}
