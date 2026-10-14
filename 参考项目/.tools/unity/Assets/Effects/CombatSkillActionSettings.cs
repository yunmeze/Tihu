using System;
using UnityEngine;

[Serializable]
public sealed class CombatSkillActionSettings
{
	public bool Enabled;

	public float ReferenceAttackSpeed = 1.1f;

	public float MinimumDuration = 0.7f;

	public float MaximumDuration = 1.1f;

	public float ImpactPhase = 0.5f;

	public float BackswingPhase = 0.78f;

	public float ContactRadius = 1.1f;

	public float WaveSpeed = 9f;

	public float ExtendedRange = 1.7f;

	public float FissureAngle = 55f;

	[Tooltip("Damage multiplier on all Seismic Leap fronts with Fissure, offsetting its narrow sector.")]
	public float FissureDamageMultiplier = 1f;

	public float RingRange = 1.6f;

	public float TakeoffTime = 0.18f;

	public float LandingTime = 0.86f;

	public float LeapDistance = 7.2f;

	public float LeapHeight = 2.6f;

	[Tooltip("Normalized airtime of the apex; earlier values give a fast launch and a longer slam.")]
	[Range(0.2f, 0.8f)]
	public float LeapApex = 0.5f;

	[Tooltip("Ease-out exponent of the climb; higher values leave the ground harder and hang longer.")]
	[Range(1f, 4f)]
	public float LeapRiseSharpness = 2f;

	[Tooltip("Ease-in exponent of the descent; higher values accelerate the slam into the ground.")]
	[Range(1f, 4f)]
	public float LeapFallSharpness = 2f;

	[Tooltip("Ease-out exponent of horizontal travel; higher values cover distance early and drop more vertically.")]
	[Range(1f, 4f)]
	public float LeapTravelSharpness = 1f;

	public float LandingClearance = 0.05f;

	public float GroundSampleDistance = 0.35f;

	public float PrimaryTravelTime = 0.18f;

	public float AftershockTravelTime = 0.22f;

	public float PrimaryFraction = 0.7f;

	public float[] AftershockDelays = new float[2] { 0.28f, 0.58f };

	public float AftershockFraction = 0.15f;

	public float ScorchInterval = 0.4f;

	public int ScorchTicks = 3;

	public float ScorchFraction = 0.15f;

	public float ExecutionDelay = 0.1f;

	public float ExecutionRadius = 1.3f;
}
