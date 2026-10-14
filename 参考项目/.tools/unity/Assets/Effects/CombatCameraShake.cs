using System;
using UnityEngine;

[Serializable]
public struct CombatCameraShake
{
	[Min(0f)]
	public float Pixels;

	[Min(0.05f)]
	public float Duration;

	[Tooltip("Noise oscillations per second.")]
	[Min(1f)]
	public float Frequency;

	[Tooltip("Share of the amplitude spent on a single downward slam that rebounds, instead of noise.")]
	[Range(0f, 1f)]
	public float Kick;

	[Tooltip("Peak camera roll in degrees; zero keeps the horizon fixed.")]
	[Range(0f, 4f)]
	public float RollDegrees;
}
