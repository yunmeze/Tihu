using System;
using System.Collections.Generic;
using UnityEngine;

public sealed class ProceduralTileMap
{
	private sealed class MinHeap
	{
		private readonly int[] _items;

		private readonly float[] _keys;

		public int Count { get; private set; }

		public MinHeap(int capacity)
		{
			_items = new int[capacity * 4 + 4];
			_keys = new float[capacity * 4 + 4];
		}

		public void Push(int item, float key)
		{
			int num = Count++;
			_items[num] = item;
			_keys[num] = key;
			while (num > 0)
			{
				int num2 = (num - 1) / 2;
				if (!(_keys[num2] <= _keys[num]))
				{
					Swap(num, num2);
					num = num2;
					continue;
				}
				break;
			}
		}

		public int Pop(out float key)
		{
			int result = _items[0];
			key = _keys[0];
			Count--;
			_items[0] = _items[Count];
			_keys[0] = _keys[Count];
			int num = 0;
			while (true)
			{
				int num2 = num * 2 + 1;
				if (num2 >= Count)
				{
					break;
				}
				int num3 = ((num2 + 1 < Count && _keys[num2 + 1] < _keys[num2]) ? (num2 + 1) : num2);
				if (_keys[num] <= _keys[num3])
				{
					break;
				}
				Swap(num, num3);
				num = num3;
			}
			return result;
		}

		private void Swap(int a, int b)
		{
			ref int reference = ref _items[a];
			ref int reference2 = ref _items[b];
			int num = _items[b];
			int num2 = _items[a];
			reference = num;
			reference2 = num2;
			ref float reference3 = ref _keys[a];
			ref float reference4 = ref _keys[b];
			float num3 = _keys[b];
			float num4 = _keys[a];
			reference3 = num3;
			reference4 = num4;
		}
	}

	private readonly ProceduralTileKind[] _tiles;

	private readonly bool[] _bridges;

	private readonly float _halfExtent;

	public int Size { get; }

	public float TileSize { get; }

	public int Seed { get; }

	public List<Vector2Int> Clearings { get; } = new List<Vector2Int>();

	public ProceduralTileKind RiverKind { get; private set; }

	private ProceduralTileMap(int size, float tileSize, int seed)
	{
		Size = size;
		TileSize = tileSize;
		Seed = seed;
		_halfExtent = (float)(size - 1) * 0.5f;
		_tiles = new ProceduralTileKind[size * size];
		_bridges = new bool[size * size];
	}

	public static ProceduralTileMap Generate(ProceduralZoneSettings settings, int seed)
	{
		if (settings == null)
		{
			throw new ArgumentNullException("settings");
		}
		ProceduralTileMap proceduralTileMap = new ProceduralTileMap(settings.MapSize, settings.TileSize, seed);
		proceduralTileMap.FillLand();
		proceduralTileMap.CarveClearingNetwork(settings);
		proceduralTileMap.MarkBoundary();
		proceduralTileMap.CarveRivers(settings);
		proceduralTileMap.CarvePools(settings);
		proceduralTileMap.RemoveDisconnectedGrass();
		return proceduralTileMap;
	}

	public bool Contains(int x, int z)
	{
		if (x >= 0 && z >= 0 && x < Size)
		{
			return z < Size;
		}
		return false;
	}

	public ProceduralTileKind KindAt(int x, int z)
	{
		if (!Contains(x, z))
		{
			return ProceduralTileKind.Void;
		}
		return _tiles[z * Size + x];
	}

	public bool IsWalkable(int x, int z)
	{
		ProceduralTileKind proceduralTileKind = KindAt(x, z);
		if (proceduralTileKind != ProceduralTileKind.Grass && proceduralTileKind != ProceduralTileKind.Path)
		{
			return proceduralTileKind == ProceduralTileKind.Clearing;
		}
		return true;
	}

	public bool IsHazard(int x, int z)
	{
		ProceduralTileKind proceduralTileKind = KindAt(x, z);
		if (proceduralTileKind != ProceduralTileKind.Liquid)
		{
			return proceduralTileKind == ProceduralTileKind.Chasm;
		}
		return true;
	}

	public bool IsBridge(int x, int z)
	{
		if (Contains(x, z))
		{
			return _bridges[z * Size + x];
		}
		return false;
	}

	public ProceduralTileKind SunkenAt(int x, int z)
	{
		if (IsBridge(x, z))
		{
			return RiverKind;
		}
		if (!IsHazard(x, z))
		{
			return ProceduralTileKind.Void;
		}
		return KindAt(x, z);
	}

	public void Pave(Vector2Int center, float radius)
	{
		int num = Mathf.CeilToInt(radius);
		for (int i = -num; i <= num; i++)
		{
			for (int j = -num; j <= num; j++)
			{
				int num2 = center.x + j;
				int num3 = center.y + i;
				if (Contains(num2, num3) && !((float)(j * j + i * i) > radius * radius))
				{
					int num4 = num3 * Size + num2;
					_bridges[num4] = false;
					ProceduralTileKind proceduralTileKind = _tiles[num4];
					if (proceduralTileKind != ProceduralTileKind.Path && proceduralTileKind != ProceduralTileKind.Clearing)
					{
						_tiles[num4] = ProceduralTileKind.Grass;
					}
				}
			}
		}
	}

	public Vector3 WorldPosition(int x, int z)
	{
		return new Vector3(((float)x - _halfExtent) * TileSize, 0f, ((float)z - _halfExtent) * TileSize);
	}

	public Vector2Int ToCell(Vector3 worldPosition)
	{
		return new Vector2Int(Mathf.FloorToInt(worldPosition.x / TileSize + _halfExtent + 0.5f), Mathf.FloorToInt(worldPosition.z / TileSize + _halfExtent + 0.5f));
	}

	public uint CellHash(int x, int z, int salt = 0)
	{
		int num = Seed ^ (x * -1640531527) ^ (z * -2048144789) ^ (salt * -1028477387);
		int num2 = (num ^ (num >>> 16)) * 2146121005;
		int num3 = (num2 ^ (num2 >>> 15)) * -2073254261;
		return (uint)(num3 ^ (num3 >>> 16));
	}

	public float VariationAt(int x, int z, int salt = 0)
	{
		return (float)(CellHash(x, z, salt) & 0xFFFFFF) / 16777216f;
	}

	private void FillLand()
	{
		float num = _halfExtent - 1.5f;
		for (int i = 1; i < Size - 1; i++)
		{
			for (int j = 1; j < Size - 1; j++)
			{
				float num2 = Mathf.Abs((float)j - _halfExtent);
				float num3 = Mathf.Abs((float)i - _halfExtent);
				float num4 = Mathf.Max(0f, num2 + num3 - num * 1.65f);
				float num5 = SmoothVariation(j, i) * 1.8f;
				if (Mathf.Max(num2, num3) + num4 <= num - num5)
				{
					Set(j, i, ProceduralTileKind.Grass);
				}
			}
		}
	}

	private float SmoothVariation(int x, int z)
	{
		int num = x / 4;
		int num2 = z / 4;
		float num3 = (float)(x % 4) / 4f;
		float num4 = (float)(z % 4) / 4f;
		num3 = num3 * num3 * (3f - 2f * num3);
		num4 = num4 * num4 * (3f - 2f * num4);
		return Mathf.Lerp(Mathf.Lerp(VariationAt(num, num2, 17), VariationAt(num + 1, num2, 17), num3), Mathf.Lerp(VariationAt(num, num2 + 1, 17), VariationAt(num + 1, num2 + 1, 17), num3), num4);
	}

	private void CarveClearingNetwork(ProceduralZoneSettings settings)
	{
		int clearingGridSize = settings.ClearingGridSize;
		Vector2Int[,] array = new Vector2Int[clearingGridSize, clearingGridSize];
		int num = clearingGridSize / 2;
		int num2 = Size / 2;
		for (int i = 0; i < clearingGridSize; i++)
		{
			for (int j = 0; j < clearingGridSize; j++)
			{
				int num3 = num2 + (j - num) * settings.ClearingSpacing;
				int num4 = num2 + (i - num) * settings.ClearingSpacing;
				if (j != num || i != num)
				{
					num3 += (int)(CellHash(j, i, 31) % 3 - 1);
					num4 += (int)(CellHash(j, i, 37) % 3 - 1);
				}
				array[j, i] = new Vector2Int(num3, num4);
				CarveClearing(array[j, i], settings.ClearingRadius);
			}
		}
		for (int k = 0; k < clearingGridSize; k++)
		{
			for (int l = 0; l < clearingGridSize; l++)
			{
				int num5 = (((k & 1) == 0) ? l : (clearingGridSize - 1 - l));
				Vector2Int vector2Int = array[num5, k];
				if (Clearings.Count > 0)
				{
					CarvePath(Clearings[Clearings.Count - 1], vector2Int, 53 + Clearings.Count);
				}
				Clearings.Add(vector2Int);
			}
		}
		for (int m = 0; m < clearingGridSize - 1; m++)
		{
			for (int n = 0; n < clearingGridSize; n++)
			{
				int num6 = (((m & 1) == 0) ? (clearingGridSize - 1) : 0);
				if (n != num6 && (n == num || VariationAt(n, m, 71) < 0.35f))
				{
					CarvePath(array[n, m], array[n, m + 1], 97 + m * clearingGridSize + n);
				}
			}
		}
	}

	private void CarveClearing(Vector2Int center, int radius)
	{
		for (int i = -radius; i <= radius; i++)
		{
			for (int j = -radius; j <= radius; j++)
			{
				if (j * j + i * i <= radius * radius + 1)
				{
					CarveWithShoulder(center.x + j, center.y + i, ProceduralTileKind.Clearing);
				}
			}
		}
	}

	private void CarvePath(Vector2Int start, Vector2Int end, int salt)
	{
		bool num = Mathf.Abs(end.x - start.x) >= Mathf.Abs(end.y - start.y);
		int num2 = (int)(CellHash(start.x, start.y, salt) % 5 - 2);
		Vector2Int vector2Int = new Vector2Int((start.x + end.x) / 2, (start.y + end.y) / 2);
		if (num)
		{
			vector2Int.y += num2;
		}
		else
		{
			vector2Int.x += num2;
		}
		vector2Int.x = Mathf.Clamp(vector2Int.x, 3, Size - 4);
		vector2Int.y = Mathf.Clamp(vector2Int.y, 3, Size - 4);
		CarvePathSegment(start, vector2Int);
		CarvePathSegment(vector2Int, end);
	}

	private void CarvePathSegment(Vector2Int start, Vector2Int end)
	{
		int num = start.x;
		int num2 = start.y;
		int num3 = Mathf.Abs(end.x - num);
		int num4 = Mathf.Abs(end.y - num2);
		int num5 = ((num < end.x) ? 1 : (-1));
		int num6 = ((num2 < end.y) ? 1 : (-1));
		int num7 = num3 - num4;
		while (true)
		{
			for (int i = 0; i <= 1; i++)
			{
				for (int j = 0; j <= 1; j++)
				{
					CarveWithShoulder(num + j, num2 + i, ProceduralTileKind.Path);
				}
			}
			if (num != end.x || num2 != end.y)
			{
				int num8 = 2 * num7;
				if (num8 > -num4)
				{
					num7 -= num4;
					num += num5;
				}
				if (num8 < num3)
				{
					num7 += num3;
					num2 += num6;
				}
				continue;
			}
			break;
		}
	}

	private void CarveWithShoulder(int x, int z, ProceduralTileKind kind)
	{
		if (x < 2 || z < 2 || x >= Size - 2 || z >= Size - 2)
		{
			return;
		}
		for (int i = -1; i <= 1; i++)
		{
			for (int j = -1; j <= 1; j++)
			{
				if (KindAt(x + j, z + i) == ProceduralTileKind.Void)
				{
					Set(x + j, z + i, ProceduralTileKind.Grass);
				}
			}
		}
		if (KindAt(x, z) != ProceduralTileKind.Clearing)
		{
			Set(x, z, kind);
		}
	}

	private void CarveRivers(ProceduralZoneSettings settings)
	{
		ProceduralTileKind proceduralTileKind = HazardTile(settings.RiverKind);
		if (proceduralTileKind == ProceduralTileKind.Void || settings.RiverCount <= 0)
		{
			return;
		}
		RiverKind = proceduralTileKind;
		bool[] array = new bool[_tiles.Length];
		for (int i = 0; i < Size; i++)
		{
			for (int j = 0; j < Size; j++)
			{
				for (int k = -1; k <= 1; k++)
				{
					for (int l = -1; l <= 1; l++)
					{
						if (KindAt(j + l, i + k) == ProceduralTileKind.Clearing)
						{
							array[i * Size + j] = true;
						}
					}
				}
			}
		}
		int[] array2 = new int[_tiles.Length];
		Queue<int> queue = new Queue<int>();
		for (int m = 0; m < _tiles.Length; m++)
		{
			ProceduralTileKind proceduralTileKind2 = _tiles[m];
			array2[m] = ((proceduralTileKind2 != ProceduralTileKind.Void && proceduralTileKind2 != ProceduralTileKind.Boundary) ? int.MaxValue : 0);
			if (array2[m] == 0)
			{
				queue.Enqueue(m);
			}
		}
		while (queue.Count > 0)
		{
			int num = queue.Dequeue();
			for (int n = -1; n <= 1; n++)
			{
				for (int num2 = -1; num2 <= 1; num2++)
				{
					int num3 = num % Size + num2;
					int num4 = num / Size + n;
					if (Contains(num3, num4) && array2[num4 * Size + num3] == int.MaxValue)
					{
						array2[num4 * Size + num3] = array2[num] + 1;
						queue.Enqueue(num4 * Size + num3);
					}
				}
			}
		}
		for (int num5 = 0; num5 < settings.RiverCount; num5++)
		{
			bool horizontal = (num5 & 1) == 0;
			int salt = 1301 + num5 * 17;
			List<Vector2Int> list = FindRiverRoute(horizontal, salt, array, array2);
			if (list == null)
			{
				continue;
			}
			for (int num6 = 0; num6 < list.Count; num6++)
			{
				Vector2Int vector2Int = list[num6];
				Vector2Int vector2Int2 = list[Mathf.Min(num6 + 1, list.Count - 1)];
				Vector2Int vector2Int3 = list[Mathf.Max(num6 - 1, 0)];
				Vector2Int vector2Int4 = ((Mathf.Abs(vector2Int2.x - vector2Int3.x) >= Mathf.Abs(vector2Int2.y - vector2Int3.y)) ? new Vector2Int(0, 1) : new Vector2Int(1, 0));
				for (int num7 = 0; num7 < settings.RiverWidth; num7++)
				{
					int num8 = ((num7 != 0) ? (((num7 & 1) == 1) ? ((num7 + 1) / 2) : (-(num7 / 2))) : 0);
					MarkRiver(vector2Int + vector2Int4 * num8, proceduralTileKind, array);
				}
			}
		}
	}

	private void MarkRiver(Vector2Int cell, ProceduralTileKind kind, bool[] blocked)
	{
		if (Contains(cell.x, cell.y) && !blocked[cell.y * Size + cell.x])
		{
			switch (KindAt(cell.x, cell.y))
			{
			case ProceduralTileKind.Path:
				_bridges[cell.y * Size + cell.x] = true;
				break;
			default:
				Set(cell.x, cell.y, kind);
				break;
			case ProceduralTileKind.Clearing:
				break;
			}
		}
	}

	private List<Vector2Int> FindRiverRoute(bool horizontal, int salt, bool[] blocked, int[] coast)
	{
		int num = Size * Size;
		float[] array = new float[num];
		int[] array2 = new int[num];
		for (int i = 0; i < num; i++)
		{
			array[i] = float.PositiveInfinity;
			array2[i] = -1;
		}
		MinHeap minHeap = new MinHeap(num);
		int num2 = Size / 4 + (int)(CellHash(salt, 3, 5) % (uint)(Size / 2));
		int num3 = (horizontal ? (num2 * Size) : num2);
		if (blocked[num3])
		{
			return null;
		}
		array[num3] = 0f;
		minHeap.Push(num3, 0f);
		int num4 = -1;
		while (minHeap.Count > 0)
		{
			float key;
			int num5 = minHeap.Pop(out key);
			if (key > array[num5])
			{
				continue;
			}
			int num6 = num5 % Size;
			int num7 = num5 / Size;
			if (horizontal ? (num6 == Size - 1) : (num7 == Size - 1))
			{
				num4 = num5;
				break;
			}
			for (int j = 0; j < 4; j++)
			{
				int num8 = num6 + j switch
				{
					1 => -1, 
					0 => 1, 
					_ => 0, 
				};
				int num9 = num7 + j switch
				{
					3 => -1, 
					2 => 1, 
					_ => 0, 
				};
				if (!Contains(num8, num9))
				{
					continue;
				}
				int num10 = num9 * Size + num8;
				if (!blocked[num10])
				{
					float num11 = key + RiverStepCost(num8, num9, salt, coast[num10]);
					if (!(num11 >= array[num10]))
					{
						array[num10] = num11;
						array2[num10] = num5;
						minHeap.Push(num10, num11);
					}
				}
			}
		}
		if (num4 < 0)
		{
			return null;
		}
		List<Vector2Int> list = new List<Vector2Int>();
		for (int num12 = num4; num12 >= 0; num12 = array2[num12])
		{
			list.Add(new Vector2Int(num12 % Size, num12 / Size));
		}
		list.Reverse();
		return list;
	}

	private float RiverStepCost(int x, int z, int salt, int coastDistance)
	{
		ProceduralTileKind proceduralTileKind = KindAt(x, z);
		if (proceduralTileKind == ProceduralTileKind.Liquid || proceduralTileKind == ProceduralTileKind.Chasm)
		{
			return 1f;
		}
		float num = ((coastDistance < 4) ? (14f - (float)coastDistance * 3f) : 0f);
		if (proceduralTileKind == ProceduralTileKind.Path)
		{
			return num + 7f;
		}
		float num2 = SmoothNoise(x, z, 5, salt);
		num += 1f + 5f * num2 * num2;
		for (int i = -1; i <= 1; i++)
		{
			for (int j = -1; j <= 1; j++)
			{
				if (KindAt(x + j, z + i) == ProceduralTileKind.Path)
				{
					return num + 1.5f;
				}
			}
		}
		return num;
	}

	private void CarvePools(ProceduralZoneSettings settings)
	{
		ProceduralTileKind proceduralTileKind = HazardTile(settings.PoolKind);
		if (proceduralTileKind == ProceduralTileKind.Void || settings.PoolCount <= 0)
		{
			return;
		}
		int num = 0;
		for (int i = 0; i < settings.PoolCount * 30; i++)
		{
			if (num >= settings.PoolCount)
			{
				break;
			}
			int num2 = (int)(3 + CellHash(i, 11, 1409) % (uint)(Size - 6));
			int num3 = (int)(3 + CellHash(i, 13, 1423) % (uint)(Size - 6));
			if (KindAt(num2, num3) != ProceduralTileKind.Grass || !PoolCellAllowed(num2, num3, proceduralTileKind, 2))
			{
				continue;
			}
			float num4 = settings.PoolRadius * Mathf.Lerp(0.7f, 1.2f, VariationAt(i, 7, 1433));
			int num5 = Mathf.CeilToInt(num4 * 1.3f);
			int num6 = 0;
			for (int j = -num5; j <= num5; j++)
			{
				for (int k = -num5; k <= num5; k++)
				{
					int x = num2 + k;
					int z = num3 + j;
					float num7 = num4 * Mathf.Lerp(0.7f, 1.3f, SmoothNoise(x, z, 3, 1447 + i));
					if (!((float)(k * k + j * j) > num7 * num7) && KindAt(x, z) == ProceduralTileKind.Grass && PoolCellAllowed(x, z, proceduralTileKind, 1))
					{
						Set(x, z, proceduralTileKind);
						num6++;
					}
				}
			}
			if (num6 > 0)
			{
				num++;
			}
		}
	}

	private bool PoolCellAllowed(int x, int z, ProceduralTileKind kind, int margin)
	{
		for (int i = -margin; i <= margin; i++)
		{
			for (int j = -margin; j <= margin; j++)
			{
				ProceduralTileKind proceduralTileKind = KindAt(x + j, z + i);
				if (proceduralTileKind == ProceduralTileKind.Path || proceduralTileKind == ProceduralTileKind.Clearing)
				{
					return false;
				}
				if (IsBridge(x + j, z + i))
				{
					return false;
				}
				if ((proceduralTileKind == ProceduralTileKind.Liquid || proceduralTileKind == ProceduralTileKind.Chasm) && proceduralTileKind != kind)
				{
					return false;
				}
			}
		}
		return true;
	}

	private static ProceduralTileKind HazardTile(ProceduralHazardKind kind)
	{
		return kind switch
		{
			ProceduralHazardKind.Chasm => ProceduralTileKind.Chasm, 
			ProceduralHazardKind.Liquid => ProceduralTileKind.Liquid, 
			_ => ProceduralTileKind.Void, 
		};
	}

	private float SmoothNoise(int x, int z, int scale, int salt)
	{
		int num = Mathf.FloorToInt((float)x / (float)scale);
		int num2 = Mathf.FloorToInt((float)z / (float)scale);
		float num3 = (float)(x - num * scale) / (float)scale;
		float num4 = (float)(z - num2 * scale) / (float)scale;
		num3 = num3 * num3 * (3f - 2f * num3);
		num4 = num4 * num4 * (3f - 2f * num4);
		return Mathf.Lerp(Mathf.Lerp(VariationAt(num, num2, salt), VariationAt(num + 1, num2, salt), num3), Mathf.Lerp(VariationAt(num, num2 + 1, salt), VariationAt(num + 1, num2 + 1, salt), num3), num4);
	}

	private void MarkBoundary()
	{
		for (int i = 0; i < Size; i++)
		{
			for (int j = 0; j < Size; j++)
			{
				if (KindAt(j, i) != ProceduralTileKind.Grass)
				{
					continue;
				}
				bool flag = false;
				for (int k = -1; k <= 1; k++)
				{
					if (flag)
					{
						break;
					}
					for (int l = -1; l <= 1; l++)
					{
						if (KindAt(j + l, i + k) == ProceduralTileKind.Void)
						{
							flag = true;
							break;
						}
					}
				}
				if (flag)
				{
					Set(j, i, ProceduralTileKind.Boundary);
				}
			}
		}
	}

	private void RemoveDisconnectedGrass()
	{
		bool[] array = new bool[_tiles.Length];
		Queue<Vector2Int> queue = new Queue<Vector2Int>();
		Vector2Int item = new Vector2Int(Size / 2, Size / 2);
		array[item.y * Size + item.x] = true;
		queue.Enqueue(item);
		while (queue.Count > 0)
		{
			Vector2Int vector2Int = queue.Dequeue();
			EnqueueIfWalkable(vector2Int.x - 1, vector2Int.y, array, queue);
			EnqueueIfWalkable(vector2Int.x + 1, vector2Int.y, array, queue);
			EnqueueIfWalkable(vector2Int.x, vector2Int.y - 1, array, queue);
			EnqueueIfWalkable(vector2Int.x, vector2Int.y + 1, array, queue);
		}
		for (int i = 0; i < _tiles.Length; i++)
		{
			if (_tiles[i] == ProceduralTileKind.Grass && !array[i])
			{
				_tiles[i] = ProceduralTileKind.Boundary;
			}
		}
	}

	private void EnqueueIfWalkable(int x, int z, bool[] reached, Queue<Vector2Int> pending)
	{
		if (IsWalkable(x, z))
		{
			int num = z * Size + x;
			if (!reached[num])
			{
				reached[num] = true;
				pending.Enqueue(new Vector2Int(x, z));
			}
		}
	}

	private void Set(int x, int z, ProceduralTileKind kind)
	{
		_tiles[z * Size + x] = kind;
	}
}
