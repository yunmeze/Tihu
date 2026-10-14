using System;

[Serializable]
public sealed class ItemStatRoll
{
	public ItemStatType StatType;

	public float Value;

	public bool IsPercent;

	public ItemStatRoll()
	{
	}

	public ItemStatRoll(ItemStatType statType, float value, bool isPercent = false)
	{
		StatType = statType;
		Value = value;
		IsPercent = isPercent;
	}
}
