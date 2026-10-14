using UnityEngine;

public readonly struct ProceduralPropInstance
{
	public readonly int Entry;

	public readonly RectInt Cells;

	public readonly int Quarter;

	public readonly float Yaw;

	public readonly float Scale;

	public readonly Vector2 Center;

	public ProceduralPropInstance(int entry, RectInt cells, int quarter, float yaw, float scale, Vector2 center)
	{
		Entry = entry;
		Cells = cells;
		Quarter = quarter;
		Yaw = yaw;
		Scale = scale;
		Center = center;
	}
}
