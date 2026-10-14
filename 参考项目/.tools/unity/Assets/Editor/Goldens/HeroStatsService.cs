using System.Collections.Generic;

using UnityEngine;

public static class GoldenHeroStatsService
{
	private struct StatAccumulator
	{
		public float FlatDamage;

		public float PercentDamage;

		public float WeaponBaseDamage;

		public bool HasWeaponBaseDamage;

		public float FlatAttackSpeed;

		public float PercentAttackSpeed;

		public float WeaponBaseAttackSpeed;

		public bool HasWeaponBaseAttackSpeed;

		public float FlatMaxHealth;

		public float PercentMaxHealth;

		public float FlatArmor;

		public float PercentArmor;

		public float CritChance;

		public float CritDamage;

		public float LifeSteal;

		public float ExperienceGain;

		public float GoldFind;

		public float RareFind;

		public float ItemSellValue;

		public float OfflineProgress;

		public float FlatHealthRegen;

		public float PercentHealthRegen;

		public float BleedChance;

		public float BleedDamage;

		public float DamageVsUndead;

		public float DamageVsElite;

		public float BossDamage;

		public float ItemDropChance;
	}

	public const float DefaultDamage = 3f;

	public const float DefaultAttackSpeed = 1.1f;

	public const float DefaultAttackRange = 1.35f;

	public const int DefaultMaxHealth = 160;

	public const int DefaultMaxEnergy = 20;

	public const float DefaultArmor = 4f;

	public const float DefaultCritChance = 0.05f;

	public const float DefaultCritDamage = 1.5f;

	public const float DefaultLifeSteal = 0f;

	public static void EnsureBaseStats(ref PlayerStatsComponent stats)
	{
		if (stats.BaseDamage <= 0f)
		{
			stats.BaseDamage = 3f;
		}
		if (stats.BaseAttackSpeed <= 0f)
		{
			stats.BaseAttackSpeed = 1.1f;
		}
		if (stats.BaseAttackRange <= 0f)
		{
			stats.BaseAttackRange = 1.35f;
		}
		if (stats.BaseMaxHealth <= 0)
		{
			stats.BaseMaxHealth = 160;
		}
		if (stats.BaseMaxEnergy <= 0)
		{
			stats.BaseMaxEnergy = 20;
		}
		if (stats.BaseArmor <= 0f)
		{
			stats.BaseArmor = 4f;
		}
		if (stats.BaseCritChance <= 0f)
		{
			stats.BaseCritChance = 0.05f;
		}
		if (stats.BaseCritDamage <= 0f)
		{
			stats.BaseCritDamage = 1.5f;
		}
		stats.BaseLifeSteal = Mathf.Max(0f, stats.BaseLifeSteal);
	}

	public static void Recalculate(ref PlayerStatsComponent stats, EquipmentState equipment)
	{
		Recalculate(ref stats, equipment, null);
	}

	public static void Recalculate(ref PlayerStatsComponent stats, EquipmentState equipment, SkillTreeBonusState skillBonus)
	{
		Recalculate(ref stats, equipment, skillBonus, 1);
	}

	public static void Recalculate(ref PlayerStatsComponent stats, EquipmentState equipment, SkillTreeBonusState skillBonus, int heroLevel)
	{
		EnsureBaseStats(ref stats);
		StatAccumulator bonuses = default(StatAccumulator);
		AddEquipmentStats(equipment, ref bonuses);
		AddSkillStats(skillBonus, ref bonuses);
		AddLevelStats(heroLevel, ref bonuses);
		float num = (bonuses.HasWeaponBaseDamage ? bonuses.WeaponBaseDamage : stats.BaseDamage);
		stats.Damage = Mathf.Max(1f, (num + bonuses.FlatDamage) * (1f + bonuses.PercentDamage));
		float num2 = (bonuses.HasWeaponBaseAttackSpeed ? bonuses.WeaponBaseAttackSpeed : stats.BaseAttackSpeed);
		stats.AttackSpeed = Mathf.Max(0.1f, (num2 + bonuses.FlatAttackSpeed) * (1f + bonuses.PercentAttackSpeed));
		stats.AttackRange = Mathf.Max(0.1f, stats.BaseAttackRange);
		stats.MaxHealth = Mathf.Max(1, Mathf.RoundToInt(((float)stats.BaseMaxHealth + bonuses.FlatMaxHealth) * (1f + bonuses.PercentMaxHealth)));
		stats.MaxEnergy = Mathf.Max(0, stats.BaseMaxEnergy);
		stats.Armor = Mathf.Max(0f, (stats.BaseArmor + bonuses.FlatArmor) * (1f + bonuses.PercentArmor));
		stats.CritChance = Mathf.Clamp01(stats.BaseCritChance + bonuses.CritChance);
		stats.CritDamage = Mathf.Max(1f, stats.BaseCritDamage + bonuses.CritDamage);
		stats.LifeSteal = Mathf.Clamp01(stats.BaseLifeSteal + bonuses.LifeSteal);
		stats.ExperienceGain = Mathf.Max(0f, bonuses.ExperienceGain);
		stats.GoldFind = Mathf.Max(0f, bonuses.GoldFind);
		stats.RareFind = Mathf.Max(0f, bonuses.RareFind);
		stats.ItemSellValue = Mathf.Max(0f, bonuses.ItemSellValue);
		stats.OfflineProgress = Mathf.Max(0f, bonuses.OfflineProgress);
		stats.HealthRegen = Mathf.Max(0f, (Mathf.Max(0f, BalanceSettingsService.Current.HeroBaseHealthRegen) + bonuses.FlatHealthRegen) * (1f + bonuses.PercentHealthRegen));
		stats.BleedChance = Mathf.Clamp01(bonuses.BleedChance);
		stats.BleedDamage = Mathf.Max(0f, bonuses.BleedDamage);
		stats.DamageVsUndead = Mathf.Max(0f, bonuses.DamageVsUndead);
		stats.DamageVsElite = Mathf.Max(0f, bonuses.DamageVsElite);
		stats.BossDamage = Mathf.Max(0f, bonuses.BossDamage);
		stats.ItemDropChance = Mathf.Max(0f, bonuses.ItemDropChance);
	}

	public static float GetAttackRange(ref PlayerStatsComponent stats)
	{
		if (stats.AttackRange > 0f)
		{
			return stats.AttackRange;
		}
		if (stats.BaseAttackRange > 0f)
		{
			return stats.BaseAttackRange;
		}
		return 1.35f;
	}

	private static void AddLevelStats(int heroLevel, ref StatAccumulator bonuses)
	{
		int num = Mathf.Max(0, heroLevel - 1);
		if (num != 0)
		{
			BalanceSettings current = BalanceSettingsService.Current;
			bonuses.PercentDamage += (float)num * Mathf.Max(0f, current.LevelDamagePercent);
			bonuses.PercentMaxHealth += (float)num * Mathf.Max(0f, current.LevelMaxHealthPercent);
		}
	}

	private static void AddSkillStats(SkillTreeBonusState bonus, ref StatAccumulator bonuses)
	{
		if (bonus != null)
		{
			bonuses.PercentDamage += bonus.PercentDamage;
			bonuses.PercentAttackSpeed += bonus.PercentAttackSpeed;
			bonuses.PercentMaxHealth += bonus.PercentMaxHealth;
			bonuses.PercentArmor += bonus.PercentArmor;
			bonuses.CritChance += bonus.CritChance;
			bonuses.CritDamage += bonus.CritDamage;
			bonuses.LifeSteal += bonus.LifeSteal;
			bonuses.ExperienceGain += bonus.ExperienceGain;
			bonuses.GoldFind += bonus.GoldFind;
			bonuses.RareFind += bonus.RareFind;
			bonuses.ItemSellValue += bonus.ItemSellValue;
			if (bonus.OfflineProgressUnlocked)
			{
				bonuses.OfflineProgress += bonus.OfflineProgress;
			}
			bonuses.FlatHealthRegen += bonus.FlatHealthRegen;
			bonuses.PercentHealthRegen += bonus.PercentHealthRegen;
			bonuses.BleedChance += bonus.BleedChance;
			bonuses.BleedDamage += bonus.BleedDamage;
			bonuses.DamageVsUndead += bonus.DamageVsUndead;
			bonuses.DamageVsElite += bonus.DamageVsElite;
			bonuses.BossDamage += bonus.BossDamage;
			bonuses.ItemDropChance += bonus.ItemDropChance;
		}
	}

	private static void AddEquipmentStats(EquipmentState equipment, ref StatAccumulator bonuses)
	{
		if (equipment != null)
		{
			AddWeaponStats(equipment.Weapon, ref bonuses);
			AddItemStats(equipment.Helmet, ref bonuses);
			AddItemStats(equipment.Armor, ref bonuses);
			AddItemStats(equipment.Ring, ref bonuses);
			AddItemStats(equipment.Trinket, ref bonuses);
		}
	}

	private static void AddWeaponStats(ItemInstance item, ref StatAccumulator bonuses)
	{
		if (item == null || string.IsNullOrWhiteSpace(item.ItemId))
		{
			return;
		}
		AddWeaponBaseStats(item.BaseStats, ref bonuses);
		if (item.Affixes == null)
		{
			return;
		}
		for (int i = 0; i < item.Affixes.Count; i++)
		{
			if (item.Affixes[i].Stat != null)
			{
				AddStat(item.Affixes[i].Stat, ref bonuses);
			}
		}
	}

	private static void AddItemStats(ItemInstance item, ref StatAccumulator bonuses)
	{
		if (item == null || string.IsNullOrWhiteSpace(item.ItemId))
		{
			return;
		}
		AddStats(item.BaseStats, ref bonuses);
		if (item.Affixes == null)
		{
			return;
		}
		for (int i = 0; i < item.Affixes.Count; i++)
		{
			if (item.Affixes[i].Stat != null)
			{
				AddStat(item.Affixes[i].Stat, ref bonuses);
			}
		}
	}

	private static void AddWeaponBaseStats(List<ItemStatRoll> stats, ref StatAccumulator bonuses)
	{
		if (stats == null)
		{
			return;
		}
		for (int i = 0; i < stats.Count; i++)
		{
			ItemStatRoll itemStatRoll = stats[i];
			if (itemStatRoll != null && itemStatRoll.StatType == ItemStatType.Damage && !itemStatRoll.IsPercent)
			{
				bonuses.WeaponBaseDamage = Mathf.Max(1f, itemStatRoll.Value);
				bonuses.HasWeaponBaseDamage = true;
			}
			else if (itemStatRoll != null && itemStatRoll.StatType == ItemStatType.AttackSpeed && !itemStatRoll.IsPercent)
			{
				bonuses.WeaponBaseAttackSpeed = Mathf.Max(0.1f, itemStatRoll.Value);
				bonuses.HasWeaponBaseAttackSpeed = true;
			}
			else
			{
				AddStat(itemStatRoll, ref bonuses);
			}
		}
	}

	private static void AddStats(List<ItemStatRoll> stats, ref StatAccumulator bonuses)
	{
		if (stats != null)
		{
			for (int i = 0; i < stats.Count; i++)
			{
				AddStat(stats[i], ref bonuses);
			}
		}
	}

	private static void AddStat(ItemStatRoll stat, ref StatAccumulator bonuses)
	{
		if (stat != null)
		{
			float num = (stat.IsPercent ? (stat.Value * 0.01f) : stat.Value);
			switch (stat.StatType)
			{
			case ItemStatType.Damage:
				AddFlatOrPercent(stat, num, ref bonuses.FlatDamage, ref bonuses.PercentDamage);
				break;
			case ItemStatType.AttackSpeed:
				AddFlatOrPercent(stat, num, ref bonuses.FlatAttackSpeed, ref bonuses.PercentAttackSpeed);
				break;
			case ItemStatType.MaxHealth:
				AddFlatOrPercent(stat, num, ref bonuses.FlatMaxHealth, ref bonuses.PercentMaxHealth);
				break;
			case ItemStatType.Armor:
				AddFlatOrPercent(stat, num, ref bonuses.FlatArmor, ref bonuses.PercentArmor);
				break;
			case ItemStatType.CritChance:
				bonuses.CritChance += stat.Value * 0.01f;
				break;
			case ItemStatType.CritDamage:
				bonuses.CritDamage += stat.Value * 0.01f;
				break;
			case ItemStatType.LifeSteal:
				bonuses.LifeSteal += stat.Value * 0.01f;
				break;
			case ItemStatType.ExperienceGain:
				bonuses.ExperienceGain += num;
				break;
			case ItemStatType.GoldFind:
				bonuses.GoldFind += num;
				break;
			case ItemStatType.RareFind:
				bonuses.RareFind += num;
				break;
			case ItemStatType.ItemSellValue:
				bonuses.ItemSellValue += num;
				break;
			case ItemStatType.OfflineProgress:
				bonuses.OfflineProgress += num;
				break;
			case ItemStatType.HealthRegen:
				AddFlatOrPercent(stat, num, ref bonuses.FlatHealthRegen, ref bonuses.PercentHealthRegen);
				break;
			case ItemStatType.BleedChance:
				bonuses.BleedChance += num;
				break;
			case ItemStatType.BleedDamage:
				bonuses.BleedDamage += num;
				break;
			case ItemStatType.DamageVsUndead:
				bonuses.DamageVsUndead += num;
				break;
			case ItemStatType.DamageVsElite:
				bonuses.DamageVsElite += num;
				break;
			case ItemStatType.BossDamage:
				bonuses.BossDamage += num;
				break;
			case ItemStatType.ItemDropChance:
				bonuses.ItemDropChance += num;
				break;
			case ItemStatType.MaxEnergy:
				break;
			}
		}
	}

	private static void AddFlatOrPercent(ItemStatRoll stat, float normalizedValue, ref float flatValue, ref float percentValue)
	{
		if (stat.IsPercent)
		{
			percentValue += normalizedValue;
		}
		else
		{
			flatValue += stat.Value;
		}
	}
}
