using System;


using UnityEngine;

[Serializable]



public struct PlayerStatsComponent
{
	[Header("Base Stats")]
	public float BaseDamage;

	public float BaseAttackSpeed;

	public float BaseAttackRange;

	public int BaseMaxHealth;

	public int BaseMaxEnergy;

	public float BaseArmor;

	public float BaseCritChance;

	public float BaseCritDamage;

	public float BaseLifeSteal;

	[Header("Final Stats")]
	public float Damage;

	public float AttackSpeed;

	public float AttackRange;

	public int MaxHealth;

	public int MaxEnergy;

	public float Armor;

	public float CritChance;

	public float CritDamage;

	public float LifeSteal;

	public float ExperienceGain;

	public float GoldFind;

	public float RareFind;

	public float ItemSellValue;

	public float OfflineProgress;

	public float HealthRegen;

	public float BleedChance;

	public float BleedDamage;

	public float DamageVsUndead;

	public float DamageVsElite;

	public float BossDamage;

	public float ItemDropChance;
}
