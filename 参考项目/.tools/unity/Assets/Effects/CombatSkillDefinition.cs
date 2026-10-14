using System;
using UnityEngine;

[Serializable]
public sealed class CombatSkillDefinition
{
	public CombatSkillId Id;

	public string Key;

	public string Name;

	public string Description;

	public int Cost;

	public float Cooldown = 4f;

	public float Radius = 3f;

	public float DamageMultiplier = 1f;

	public float Duration = 1.2f;

	[Tooltip("Seconds between pulses, or attack intervals when PulseInAttackIntervals is enabled.")]
	public float PulseInterval = 0.3f;

	public bool PulseInAttackIntervals;

	[Tooltip("Final pulse multiplier; multiplied by AttackSpeed when DamageFromAttackSpeed is enabled.")]
	public float FinisherDamageMultiplier = 2f;

	public float Angle = 120f;

	public float ControlDuration = 0.6f;

	public float[] CooldownsByStage = Array.Empty<float>();

	public float[] DurationsByStage = Array.Empty<float>();

	public bool CooldownInAttackIntervals;

	public bool DamageFromAttackSpeed;

	public CombatSkillModifier[] Modifiers;

	public CombatSkillActionSettings Action;

	public CombatSkillPresentationProfile Presentation;

	public bool HasAction
	{
		get
		{
			if (Id != CombatSkillId.Whirlwind && Action != null)
			{
				return Action.Enabled;
			}
			return false;
		}
	}
}
