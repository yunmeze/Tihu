using System;
using System.Collections.Generic;
using UnityEngine;

public sealed class ProceduralPropLayout
{
	private const int ChunkSize = 8;

	public const int VisualMargin = 2;

	private readonly ProceduralTileMap _map;

	private readonly int[] _owner;

	private readonly List<ProceduralPropInstance> _instances = new List<ProceduralPropInstance>();

	private readonly List<ProceduralPropDefinition> _definitions = new List<ProceduralPropDefinition>();

	private readonly List<bool> _suppressed = new List<bool>();

	private readonly List<int>[] _chunks;

	private readonly int _chunkCount;

	private int[] _queryStamp = Array.Empty<int>();

	private int _queryId;

	public IReadOnlyList<ProceduralPropInstance> Instances => _instances;

	public ProceduralPropDefinition Definition(int entry)
	{
		return _definitions[entry];
	}

	public bool IsSuppressed(int index)
	{
		return _suppressed[index];
	}

	private ProceduralPropLayout(ProceduralTileMap map, ProceduralPropEntry[] entries)
	{
		_map = map;
		if (entries != null)
		{
			for (int i = 0; i < entries.Length; i++)
			{
				ProceduralPropEntry proceduralPropEntry = entries[i];
				_definitions.Add(proceduralPropEntry.Definition);
			}
		}
		_owner = new int[map.Size * map.Size];
		for (int j = 0; j < _owner.Length; j++)
		{
			_owner[j] = -1;
		}
		_chunkCount = (map.Size + 8 - 1) / 8;
		_chunks = new List<int>[_chunkCount * _chunkCount];
	}

	public int OwnerAt(int x, int z)
	{
		if (!_map.Contains(x, z))
		{
			return -1;
		}
		return _owner[z * _map.Size + x];
	}

	public static ProceduralPropLayout Generate(ProceduralTileMap map, ProceduralZoneSettings settings)
	{
		if (map == null)
		{
			throw new ArgumentNullException("map");
		}
		if (settings == null)
		{
			throw new ArgumentNullException("settings");
		}
		ProceduralPropLayout proceduralPropLayout = new ProceduralPropLayout(map, settings.Props);
		ProceduralPropEntry[] props = settings.Props;
		if (props == null || props.Length == 0)
		{
			return proceduralPropLayout;
		}
		proceduralPropLayout.PlacePass(props, ProceduralPropPlacement.Boundary, settings.BoundaryPropDensity, null);
		proceduralPropLayout.PlacePass(props, ProceduralPropPlacement.Field, settings.FieldPropDensity, true);
		proceduralPropLayout.PlacePass(props, ProceduralPropPlacement.Field, settings.FieldPropDensity, false);
		proceduralPropLayout.PlacePass(props, ProceduralPropPlacement.Roadside, settings.RoadsidePropDensity, null);
		proceduralPropLayout.PlaceBridges(props);
		proceduralPropLayout.PlacePass(props, ProceduralPropPlacement.Shore, settings.ShorePropDensity, null);
		proceduralPropLayout.PlacePass(props, ProceduralPropPlacement.Scatter, settings.ScatterDensity, null);
		return proceduralPropLayout;
	}

	public void Query(RectInt bounds, List<int> results)
	{
		results.Clear();
		if (_instances.Count == 0)
		{
			return;
		}
		if (_queryStamp.Length != _instances.Count)
		{
			_queryStamp = new int[_instances.Count];
		}
		_queryId++;
		int num = Mathf.Clamp(Mathf.FloorToInt((float)(bounds.xMin - 2) / 8f), 0, _chunkCount - 1);
		int num2 = Mathf.Clamp(Mathf.FloorToInt((float)(bounds.xMax - 1 + 2) / 8f), 0, _chunkCount - 1);
		int num3 = Mathf.Clamp(Mathf.FloorToInt((float)(bounds.yMin - 2) / 8f), 0, _chunkCount - 1);
		int num4 = Mathf.Clamp(Mathf.FloorToInt((float)(bounds.yMax - 1 + 2) / 8f), 0, _chunkCount - 1);
		for (int i = num3; i <= num4; i++)
		{
			for (int j = num; j <= num2; j++)
			{
				List<int> list = _chunks[i * _chunkCount + j];
				if (list == null)
				{
					continue;
				}
				foreach (int item in list)
				{
					if (_queryStamp[item] != _queryId && !_suppressed[item])
					{
						_queryStamp[item] = _queryId;
						RectInt cells = _instances[item].Cells;
						if (cells.xMax + 2 > bounds.xMin && cells.xMin - 2 < bounds.xMax && cells.yMax + 2 > bounds.yMin && cells.yMin - 2 < bounds.yMax)
						{
							results.Add(item);
						}
					}
				}
			}
		}
	}

	public static void ObstacleBox(ProceduralPropInstance instance, ProceduralPropObstacle obstacle, out Vector2 center, out Vector2 size)
	{
		Vector2 vector = obstacle.Center * instance.Scale;
		Vector2 vector2 = obstacle.Size * instance.Scale;
		if (instance.Quarter < 0)
		{
			float f = instance.Yaw * (MathF.PI / 180f);
			float num = Mathf.Cos(f);
			float num2 = Mathf.Sin(f);
			center = instance.Center + new Vector2(vector.x * num + vector.y * num2, (0f - vector.x) * num2 + vector.y * num);
			size = vector2;
			return;
		}
		switch (instance.Quarter & 3)
		{
		case 1:
			vector = new Vector2(vector.y, 0f - vector.x);
			vector2 = new Vector2(vector2.y, vector2.x);
			break;
		case 2:
			vector = -vector;
			break;
		case 3:
			vector = new Vector2(0f - vector.y, vector.x);
			vector2 = new Vector2(vector2.y, vector2.x);
			break;
		}
		center = instance.Center + vector;
		size = vector2;
	}

	private void PlacePass(ProceduralPropEntry[] entries, ProceduralPropPlacement placement, float density, bool? multiTile)
	{
		if (density <= 0f)
		{
			return;
		}
		List<int> list = new List<int>();
		float num = 0f;
		float num2 = 0f;
		for (int i = 0; i < entries.Length; i++)
		{
			ProceduralPropDefinition definition = entries[i].Definition;
			if (!(definition == null) && definition.IsValid && definition.Placement == placement && !(entries[i].Weight <= 0f))
			{
				num2 += entries[i].Weight;
				if (!multiTile.HasValue || definition.Footprint.x * definition.Footprint.y > 1 == multiTile.Value)
				{
					list.Add(i);
					num += entries[i].Weight;
				}
			}
		}
		if (list.Count == 0)
		{
			return;
		}
		density *= num / num2;
		int num3 = 4099 + (int)placement * 131 + ((multiTile == true) ? 37 : 0);
		int[] array = new int[_map.Size * _map.Size];
		uint[] array2 = new uint[array.Length];
		for (int j = 0; j < array.Length; j++)
		{
			array[j] = j;
			array2[j] = _map.CellHash(j % _map.Size, j / _map.Size, num3);
		}
		Array.Sort(array2, array);
		int[] array3 = array;
		foreach (int num4 in array3)
		{
			int x = num4 % _map.Size;
			int z = num4 / _map.Size;
			if (_owner[num4] >= 0 || _map.VariationAt(x, z, num3 + 1) >= density || !CellAllowed(placement, x, z))
			{
				continue;
			}
			float num5 = _map.VariationAt(x, z, num3 + 2) * num;
			int num6 = list[list.Count - 1];
			foreach (int item in list)
			{
				num5 -= entries[item].Weight;
				if (num5 < 0f)
				{
					num6 = item;
					break;
				}
			}
			TryPlace(entries[num6].Definition, num6, x, z, num3);
		}
	}

	private bool TryPlace(ProceduralPropDefinition definition, int entry, int x, int z, int salt)
	{
		uint num = _map.CellHash(x, z, salt + 3);
		Vector2Int footprint = definition.Footprint;
		if (definition.Placement == ProceduralPropPlacement.Roadside)
		{
			int num2 = RoadsideQuarter(x, z);
			if (num2 >= 0)
			{
				return TryRect(definition, entry, x, z, num2, num);
			}
			return false;
		}
		int num3 = (int)(num & 3);
		int num4 = ((footprint.x == footprint.y) ? 1 : 4);
		for (int i = 0; i < num4; i++)
		{
			if (TryRect(definition, entry, x, z, (num3 + i) & 3, num))
			{
				return true;
			}
		}
		return false;
	}

	private bool TryRect(ProceduralPropDefinition definition, int entry, int x, int z, int quarter, uint hash)
	{
		int num = (((quarter & 1) == 0) ? definition.Footprint.x : definition.Footprint.y);
		int num2 = (((quarter & 1) == 0) ? definition.Footprint.y : definition.Footprint.x);
		int num3 = (int)((hash >> 4) % (uint)(num * num2));
		for (int i = 0; i < num * num2; i++)
		{
			int num4 = (num3 + i) % (num * num2);
			RectInt rect = new RectInt(x - num4 % num, z - num4 / num, num, num2);
			if (Fits(definition, rect, quarter))
			{
				Place(definition, entry, rect, quarter, hash);
				return true;
			}
		}
		return false;
	}

	private bool Fits(ProceduralPropDefinition definition, RectInt rect, int quarter)
	{
		if (rect.xMin < 0 || rect.yMin < 0 || rect.xMax > _map.Size || rect.yMax > _map.Size)
		{
			return false;
		}
		bool multiTile = rect.width * rect.height > 1;
		for (int i = rect.yMin; i < rect.yMax; i++)
		{
			for (int j = rect.xMin; j < rect.xMax; j++)
			{
				if (_owner[i * _map.Size + j] >= 0 || !CellAllowed(definition.Placement, j, i))
				{
					return false;
				}
				if (definition.Placement == ProceduralPropPlacement.Roadside && !FacesPath(j, i, quarter))
				{
					return false;
				}
				if (definition.Blocks && ((definition.Placement == ProceduralPropPlacement.Roadside) ? TouchesClearing(j, i) : TouchesEncounterSpace(j, i, multiTile)))
				{
					return false;
				}
			}
		}
		return true;
	}

	private void Place(ProceduralPropDefinition definition, int entry, RectInt rect, int quarter, uint hash)
	{
		int width = rect.width;
		int height = rect.height;
		int count = _instances.Count;
		for (int i = rect.yMin; i < rect.yMax; i++)
		{
			for (int j = rect.xMin; j < rect.xMax; j++)
			{
				_owner[i * _map.Size + j] = count;
			}
		}
		Vector3 vector = _map.WorldPosition(rect.xMin, rect.yMin);
		Vector2 center = new Vector2(vector.x + (float)(width - 1) * 0.5f * _map.TileSize, vector.z + (float)(height - 1) * 0.5f * _map.TileSize);
		float num = (float)((hash >> 8) & 0xFFFF) / 65535f;
		float yaw = (definition.FreeRotation ? (num * 360f) : ((float)quarter * 90f + (num - 0.5f) * ((definition.Placement == ProceduralPropPlacement.Roadside) ? 14f : 6f)));
		float t = (float)((hash >> 20) & 0x3FF) / 1023f;
		float scale = Mathf.Lerp(definition.ScaleRange.x, definition.ScaleRange.y, t);
		_instances.Add(new ProceduralPropInstance(entry, rect, (!definition.FreeRotation) ? quarter : 0, yaw, scale, center));
		_suppressed.Add(item: false);
		Register(count, rect);
	}

	private void PlaceBridges(ProceduralPropEntry[] entries)
	{
		int num = FirstEntry(entries, ProceduralPropPlacement.Bridge);
		int num2 = FirstEntry(entries, ProceduralPropPlacement.BridgeRail);
		if (num < 0 && num2 < 0)
		{
			return;
		}
		for (int i = 0; i < _map.Size; i++)
		{
			for (int j = 0; j < _map.Size; j++)
			{
				if (!_map.IsBridge(j, i))
				{
					continue;
				}
				int num3 = BridgeQuarter(j, i);
				RectInt rect = new RectInt(j, i, 1, 1);
				if (num >= 0)
				{
					AddFixed(num, rect, num3, own: true);
				}
				if (num2 < 0)
				{
					continue;
				}
				for (int k = 0; k < 2; k++)
				{
					int quarter = (num3 + k * 2) & 3;
					Vector2Int vector2Int = LocalRight(quarter);
					if (_map.IsHazard(j + vector2Int.x, i + vector2Int.y))
					{
						AddFixed(num2, rect, quarter, own: false);
					}
				}
			}
		}
	}

	private static int FirstEntry(ProceduralPropEntry[] entries, ProceduralPropPlacement placement)
	{
		for (int i = 0; i < entries.Length; i++)
		{
			ProceduralPropDefinition definition = entries[i].Definition;
			if (definition != null && definition.IsValid && definition.Placement == placement)
			{
				return i;
			}
		}
		return -1;
	}

	private int BridgeQuarter(int x, int z)
	{
		bool flag = _map.IsHazard(x - 1, z) || _map.IsHazard(x + 1, z);
		bool flag2 = _map.IsHazard(x, z - 1) || _map.IsHazard(x, z + 1);
		if (flag != flag2)
		{
			if (!flag)
			{
				return 1;
			}
			return 0;
		}
		int num = (_map.IsWalkable(x, z - 1) ? 1 : 0) + (_map.IsWalkable(x, z + 1) ? 1 : 0);
		if ((_map.IsWalkable(x - 1, z) ? 1 : 0) + (_map.IsWalkable(x + 1, z) ? 1 : 0) <= num)
		{
			return 0;
		}
		return 1;
	}

	private static Vector2Int LocalRight(int quarter)
	{
		return (quarter & 3) switch
		{
			0 => new Vector2Int(1, 0), 
			1 => new Vector2Int(0, -1), 
			2 => new Vector2Int(-1, 0), 
			_ => new Vector2Int(0, 1), 
		};
	}

	private void AddFixed(int entry, RectInt rect, int quarter, bool own)
	{
		int count = _instances.Count;
		if (own)
		{
			_owner[rect.y * _map.Size + rect.x] = count;
		}
		Vector3 vector = _map.WorldPosition(rect.x, rect.y);
		_instances.Add(new ProceduralPropInstance(entry, rect, quarter, (float)quarter * 90f, 1f, new Vector2(vector.x, vector.z)));
		_suppressed.Add(item: false);
		Register(count, rect);
	}

	public void Suppress(int index)
	{
		if (_suppressed[index])
		{
			return;
		}
		_suppressed[index] = true;
		RectInt cells = _instances[index].Cells;
		for (int i = cells.yMin; i < cells.yMax; i++)
		{
			for (int j = cells.xMin; j < cells.xMax; j++)
			{
				if (_map.Contains(j, i) && _owner[i * _map.Size + j] == index)
				{
					_owner[i * _map.Size + j] = -1;
				}
			}
		}
	}

	public int AddPlaced(ProceduralPropDefinition definition, Vector2 center, float yaw, float scale)
	{
		int num = _definitions.IndexOf(definition);
		if (num < 0)
		{
			num = _definitions.Count;
			_definitions.Add(definition);
		}
		int num2 = Mathf.RoundToInt(Mathf.Repeat(yaw, 360f) / 90f) & 3;
		int num3 = (((num2 & 1) == 0) ? definition.Footprint.x : definition.Footprint.y);
		int num4 = (((num2 & 1) == 0) ? definition.Footprint.y : definition.Footprint.x);
		Vector2Int vector2Int = _map.ToCell(new Vector3(center.x, 0f, center.y));
		RectInt rectInt = new RectInt(vector2Int.x - (num3 - 1) / 2, vector2Int.y - (num4 - 1) / 2, num3, num4);
		int count = _instances.Count;
		for (int i = rectInt.yMin; i < rectInt.yMax; i++)
		{
			for (int j = rectInt.xMin; j < rectInt.xMax; j++)
			{
				if (_map.Contains(j, i))
				{
					_owner[i * _map.Size + j] = count;
				}
			}
		}
		_instances.Add(new ProceduralPropInstance(num, rectInt, -1, yaw, scale, center));
		_suppressed.Add(item: false);
		Register(count, rectInt);
		return count;
	}

	private void Register(int index, RectInt rect)
	{
		int num = Mathf.Max(0, (rect.xMin - 2) / 8);
		int num2 = Mathf.Min(_chunkCount - 1, (rect.xMax - 1 + 2) / 8);
		int num3 = Mathf.Max(0, (rect.yMin - 2) / 8);
		int num4 = Mathf.Min(_chunkCount - 1, (rect.yMax - 1 + 2) / 8);
		for (int i = num3; i <= num4; i++)
		{
			for (int j = num; j <= num2; j++)
			{
				int num5 = i * _chunkCount + j;
				List<int>[] chunks = _chunks;
				int num6 = num5;
				(chunks[num6] ?? (chunks[num6] = new List<int>())).Add(index);
			}
		}
	}

	private bool CellAllowed(ProceduralPropPlacement placement, int x, int z)
	{
		ProceduralTileKind proceduralTileKind = _map.KindAt(x, z);
		switch (placement)
		{
		case ProceduralPropPlacement.Field:
		case ProceduralPropPlacement.Roadside:
			return proceduralTileKind == ProceduralTileKind.Grass;
		case ProceduralPropPlacement.Scatter:
			if (proceduralTileKind != ProceduralTileKind.Grass)
			{
				return proceduralTileKind == ProceduralTileKind.Boundary;
			}
			return true;
		case ProceduralPropPlacement.Shore:
			if (proceduralTileKind == ProceduralTileKind.Grass)
			{
				if (!_map.IsHazard(x - 1, z) && !_map.IsHazard(x + 1, z) && !_map.IsHazard(x, z - 1))
				{
					return _map.IsHazard(x, z + 1);
				}
				return true;
			}
			return false;
		case ProceduralPropPlacement.Boundary:
			if (_map.Contains(x, z) && (proceduralTileKind == ProceduralTileKind.Boundary || proceduralTileKind == ProceduralTileKind.Void))
			{
				return NearWalkable(x, z, 3);
			}
			return false;
		default:
			return false;
		}
	}

	private int RoadsideQuarter(int x, int z)
	{
		if (IsPath(x, z - 1))
		{
			return 0;
		}
		if (IsPath(x - 1, z))
		{
			return 1;
		}
		if (IsPath(x, z + 1))
		{
			return 2;
		}
		if (IsPath(x + 1, z))
		{
			return 3;
		}
		return -1;
	}

	private bool FacesPath(int x, int z, int quarter)
	{
		return (quarter & 3) switch
		{
			0 => IsPath(x, z - 1), 
			1 => IsPath(x - 1, z), 
			2 => IsPath(x, z + 1), 
			_ => IsPath(x + 1, z), 
		};
	}

	private bool IsPath(int x, int z)
	{
		return _map.KindAt(x, z) == ProceduralTileKind.Path;
	}

	private bool TouchesEncounterSpace(int x, int z, bool multiTile)
	{
		for (int i = -1; i <= 1; i++)
		{
			for (int j = -1; j <= 1; j++)
			{
				if (multiTile || j == 0 || i == 0)
				{
					ProceduralTileKind proceduralTileKind = _map.KindAt(x + j, z + i);
					if (proceduralTileKind == ProceduralTileKind.Path || proceduralTileKind == ProceduralTileKind.Clearing)
					{
						return true;
					}
				}
			}
		}
		return false;
	}

	private bool TouchesClearing(int x, int z)
	{
		for (int i = -1; i <= 1; i++)
		{
			for (int j = -1; j <= 1; j++)
			{
				if (_map.KindAt(x + j, z + i) == ProceduralTileKind.Clearing)
				{
					return true;
				}
			}
		}
		return false;
	}

	private bool NearWalkable(int x, int z, int reach)
	{
		for (int i = -reach; i <= reach; i++)
		{
			for (int j = -reach; j <= reach; j++)
			{
				if (_map.IsWalkable(x + j, z + i))
				{
					return true;
				}
			}
		}
		return false;
	}
}
