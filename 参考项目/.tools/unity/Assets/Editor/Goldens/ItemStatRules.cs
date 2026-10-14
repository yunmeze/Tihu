public static class ItemStatRules
{
	private static readonly ItemStatType[] PlayerFacingStatsInternal = new ItemStatType[19]
	{
		ItemStatType.Damage,
		ItemStatType.AttackSpeed,
		ItemStatType.MaxHealth,
		ItemStatType.Armor,
		ItemStatType.CritChance,
		ItemStatType.CritDamage,
		ItemStatType.LifeSteal,
		ItemStatType.GoldFind,
		ItemStatType.ExperienceGain,
		ItemStatType.RareFind,
		ItemStatType.ItemSellValue,
		ItemStatType.OfflineProgress,
		ItemStatType.HealthRegen,
		ItemStatType.BleedChance,
		ItemStatType.BleedDamage,
		ItemStatType.DamageVsUndead,
		ItemStatType.DamageVsElite,
		ItemStatType.BossDamage,
		ItemStatType.ItemDropChance
	};

	public static ItemStatType[] PlayerFacingStats => (ItemStatType[])PlayerFacingStatsInternal.Clone();

	public static bool IsPlayerFacing(ItemStatType statType)
	{
		return statType != ItemStatType.MaxEnergy;
	}

	public static bool CanRollOnLoot(ItemStatType statType)
	{
		return IsPlayerFacing(statType);
	}

	public static bool TryGetDisplayName(ItemStatType statType, out string displayName)
	{
		if (!IsPlayerFacing(statType))
		{
			displayName = string.Empty;
			return false;
		}
		switch (statType)
		{
		case ItemStatType.AttackSpeed:
			displayName = "Attack Speed";
			return true;
		case ItemStatType.MaxHealth:
			displayName = "Max HP";
			return true;
		case ItemStatType.CritChance:
			displayName = "Crit Chance";
			return true;
		case ItemStatType.CritDamage:
			displayName = "Crit Damage";
			return true;
		case ItemStatType.LifeSteal:
			displayName = "Life Steal";
			return true;
		case ItemStatType.GoldFind:
			displayName = "Gold Find";
			return true;
		case ItemStatType.ExperienceGain:
			displayName = "XP Gain";
			return true;
		case ItemStatType.RareFind:
			displayName = "Rare Find";
			return true;
		case ItemStatType.ItemSellValue:
			displayName = "Sell Value";
			return true;
		case ItemStatType.OfflineProgress:
			displayName = "Offline Progress";
			return true;
		case ItemStatType.HealthRegen:
			displayName = "Health Regen";
			return true;
		case ItemStatType.BleedChance:
			displayName = "Bleed Chance";
			return true;
		case ItemStatType.BleedDamage:
			displayName = "Bleed Damage";
			return true;
		case ItemStatType.DamageVsUndead:
			displayName = "Damage vs Undead";
			return true;
		case ItemStatType.DamageVsElite:
			displayName = "Damage vs Elite";
			return true;
		case ItemStatType.BossDamage:
			displayName = "Boss Damage";
			return true;
		case ItemStatType.ItemDropChance:
			displayName = "Item Drop Chance";
			return true;
		default:
			displayName = statType.ToString();
			return true;
		}
	}
}
