using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

public static class ProceduralHazardVisuals
{
	public const int ChunkSize = 8;

	private const int GroundSubdivisions = 10;

	private const int LiquidSubdivisions = 4;

	public const int SearchRadius = 3;

	public static List<ProceduralHazardChunk> Build(ProceduralTileMap map, ProceduralZoneSettings settings, RectInt? region = null)
	{
		if (map == null)
		{
			throw new ArgumentNullException("map");
		}
		if (settings == null)
		{
			throw new ArgumentNullException("settings");
		}
		List<ProceduralHazardChunk> list = new List<ProceduralHazardChunk>();
		int num = (map.Size + 8 - 1) / 8;
		List<Vector2Int> list2 = new List<Vector2Int>();
		for (int i = 0; i < num; i++)
		{
			for (int j = 0; j < num; j++)
			{
				RectInt cells = new RectInt(j * 8, i * 8, Mathf.Min(8, map.Size - j * 8), Mathf.Min(8, map.Size - i * 8));
				if (region.HasValue && !cells.Overlaps(region.Value))
				{
					continue;
				}
				list2.Clear();
				bool flag = false;
				for (int k = cells.yMin; k < cells.yMax; k++)
				{
					for (int l = cells.xMin; l < cells.xMax; l++)
					{
						ProceduralTileKind proceduralTileKind = map.SunkenAt(l, k);
						if (proceduralTileKind != ProceduralTileKind.Void)
						{
							list2.Add(new Vector2Int(l, k));
							flag = flag || proceduralTileKind == ProceduralTileKind.Liquid;
						}
					}
				}
				if (list2.Count != 0)
				{
					list.Add(new ProceduralHazardChunk
					{
						Cells = cells,
						Ground = BuildGround(map, settings, list2),
						Liquid = (flag ? BuildLiquid(map, settings, list2) : null)
					});
				}
			}
		}
		return list;
	}

	private static Mesh BuildGround(ProceduralTileMap map, ProceduralZoneSettings settings, List<Vector2Int> cells)
	{
		List<Vector3> list = new List<Vector3>(cells.Count * 11 * 11);
		List<Vector3> list2 = new List<Vector3>(list.Capacity);
		List<Vector4> list3 = new List<Vector4>(list.Capacity);
		List<int> list4 = new List<int>(cells.Count * 10 * 10 * 6);
		Vector3 vector = map.WorldPosition(0, 0);
		float tileSize = map.TileSize;
		foreach (Vector2Int cell in cells)
		{
			ProceduralTileKind proceduralTileKind = map.SunkenAt(cell.x, cell.y);
			float num = ((proceduralTileKind == ProceduralTileKind.Chasm) ? 1f : 0f);
			float num2 = ((num > 0f) ? settings.ChasmDepth : settings.LiquidBedDepth);
			int count = list.Count;
			for (int i = 0; i <= 10; i++)
			{
				for (int j = 0; j <= 10; j++)
				{
					Vector2 vector2 = new Vector2((float)cell.x - 0.5f + (float)j / 10f, (float)cell.y - 0.5f + (float)i / 10f);
					float num3 = Height(map, settings, proceduralTileKind, vector2);
					float num4 = Height(map, settings, proceduralTileKind, vector2 + new Vector2(0.02f, 0f)) - Height(map, settings, proceduralTileKind, vector2 - new Vector2(0.02f, 0f));
					float num5 = Height(map, settings, proceduralTileKind, vector2 + new Vector2(0f, 0.02f)) - Height(map, settings, proceduralTileKind, vector2 - new Vector2(0f, 0.02f));
					float num6 = 0.04f * tileSize;
					list.Add(vector + new Vector3(vector2.x * tileSize, num3, vector2.y * tileSize));
					list2.Add(new Vector3((0f - num4) / num6, 1f, (0f - num5) / num6).normalized);
					list3.Add(new Vector4(num, 1f, Mathf.Clamp01((0f - num3) / num2), (num > 0f) ? 99f : (num3 + settings.LiquidLevel)));
				}
			}
			for (int k = 0; k < 10; k++)
			{
				for (int l = 0; l < 10; l++)
				{
					int num7 = count + k * 11 + l;
					int item = num7 + 1;
					int num8 = num7 + 10 + 1;
					int item2 = num8 + 1;
					list4.Add(num7);
					list4.Add(num8);
					list4.Add(item2);
					list4.Add(num7);
					list4.Add(item2);
					list4.Add(item);
				}
			}
		}
		Mesh mesh = new Mesh
		{
			name = "Procedural sunken ground"
		};
		if (list.Count > 65000)
		{
			mesh.indexFormat = IndexFormat.UInt32;
		}
		mesh.SetVertices(list);
		mesh.SetNormals(list2);
		mesh.SetUVs(0, list3);
		mesh.SetTriangles(list4, 0);
		mesh.RecalculateBounds();
		mesh.UploadMeshData(markNoLongerReadable: true);
		return mesh;
	}

	private static Mesh BuildLiquid(ProceduralTileMap map, ProceduralZoneSettings settings, List<Vector2Int> cells)
	{
		List<Vector3> list = new List<Vector3>();
		List<Vector4> list2 = new List<Vector4>();
		List<int> list3 = new List<int>();
		Vector3 vector = map.WorldPosition(0, 0);
		float tileSize = map.TileSize;
		foreach (Vector2Int cell in cells)
		{
			if (map.SunkenAt(cell.x, cell.y) != ProceduralTileKind.Liquid)
			{
				continue;
			}
			int count = list.Count;
			for (int i = 0; i <= 4; i++)
			{
				for (int j = 0; j <= 4; j++)
				{
					Vector2 p = new Vector2((float)cell.x - 0.5f + (float)j / 4f, (float)cell.y - 0.5f + (float)i / 4f);
					float num = Height(map, settings, ProceduralTileKind.Liquid, p);
					list.Add(vector + new Vector3(p.x * tileSize, 0f - settings.LiquidLevel, p.y * tileSize));
					list2.Add(new Vector4(0f - num - settings.LiquidLevel, 0f, 0f, 0f));
				}
			}
			for (int k = 0; k < 4; k++)
			{
				for (int l = 0; l < 4; l++)
				{
					int num2 = count + k * 5 + l;
					int item = num2 + 1;
					int num3 = num2 + 4 + 1;
					int item2 = num3 + 1;
					list3.Add(num2);
					list3.Add(num3);
					list3.Add(item2);
					list3.Add(num2);
					list3.Add(item2);
					list3.Add(item);
				}
			}
		}
		Vector3[] array = new Vector3[list.Count];
		for (int m = 0; m < array.Length; m++)
		{
			array[m] = Vector3.up;
		}
		Mesh mesh = new Mesh();
		mesh.name = "Procedural liquid surface";
		mesh.SetVertices(list);
		mesh.SetNormals(array);
		mesh.SetUVs(0, list2);
		mesh.SetTriangles(list3, 0);
		mesh.RecalculateBounds();
		mesh.UploadMeshData(markNoLongerReadable: true);
		return mesh;
	}

	private static float Height(ProceduralTileMap map, ProceduralZoneSettings settings, ProceduralTileKind kind, Vector2 p)
	{
		float num = SolidDistance(map, p);
		float num2 = (Mathf.PerlinNoise(p.x * 1.3f + 17.1f, p.y * 1.3f + 3.7f) * 0.65f + Mathf.PerlinNoise(p.x * 3.7f + 5.3f, p.y * 3.7f + 11.9f) * 0.35f) * 0.35f;
		if (kind == ProceduralTileKind.Chasm)
		{
			float num3 = Smooth((num - num2) / settings.ChasmBankWidth);
			float num4 = Mathf.Clamp01((num - num2 - settings.ChasmBankWidth) / 1.2f);
			return (0f - settings.ChasmDepth) * (num3 * 0.82f + num4 * 0.18f);
		}
		return (0f - settings.LiquidBedDepth) * Smooth((num - num2) / settings.LiquidBankWidth);
	}

	private static float SolidDistance(ProceduralTileMap map, Vector2 p)
	{
		int num = Mathf.RoundToInt(p.x);
		int num2 = Mathf.RoundToInt(p.y);
		float num3 = Mathf.Exp(-15.909091f);
		for (int i = -3; i <= 3; i++)
		{
			for (int j = -3; j <= 3; j++)
			{
				int num4 = num + j;
				int num5 = num2 + i;
				if (map.SunkenAt(num4, num5) == ProceduralTileKind.Void)
				{
					float num6 = Mathf.Max(Mathf.Abs(p.x - (float)num4) - 0.5f, 0f);
					float num7 = Mathf.Max(Mathf.Abs(p.y - (float)num5) - 0.5f, 0f);
					num3 += Mathf.Exp((0f - Mathf.Sqrt(num6 * num6 + num7 * num7)) / 0.22f);
				}
			}
		}
		return Mathf.Max(0f, -0.22f * Mathf.Log(num3));
	}

	private static float Smooth(float t)
	{
		t = Mathf.Clamp01(t);
		return t * t * (3f - 2f * t);
	}
}
