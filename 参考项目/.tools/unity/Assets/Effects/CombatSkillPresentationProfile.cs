using UnityEngine;

[CreateAssetMenu(menuName = "Desktop Hellfarmer/Combat Skill Presentation")]
public sealed class CombatSkillPresentationProfile : ScriptableObject
{
	public GameObject EffectPrefab;

	public Material FrontMaterial;

	public Material GroundMaterial;

	public Material DebrisMaterial;

	public Material RockMaterial;

	[Tooltip("Contact points in the authored leap clip; independent of the gameplay flight duration.")]
	public Vector2 LeapClipContacts = new Vector2(0.17142859f, 62f / 105f);

	[Tooltip("Clip phases where the overhead hold begins and where the downswing starts.")]
	public Vector2 LeapOverheadClip = new Vector2(0.29f, 0.49f);

	[Tooltip("Normalized airtime at which those two clip phases are reached; the downswing fills the rest of the descent.")]
	public Vector2 LeapOverheadAir = new Vector2(0.25f, 0.75f);

	[Tooltip("Seconds the landing pose is held after contact before the recovery plays.")]
	[Range(0f, 0.2f)]
	public float ImpactHold = 0.07f;

	[Tooltip("Clip phase advanced during the landing hold, settling deeper into the impact crouch.")]
	[Range(0f, 0.1f)]
	public float ImpactHoldCreep = 0.03f;

	[Tooltip("Temporary rear-camera pullback per metre of leap height; keeps the full arc in frame without following animated bones.")]
	[Range(0f, 3f)]
	public float RearLeapPullback = 2f;

	[Tooltip("Share of the leap height the camera follows upward, keeping the apex inside the small window.")]
	[Range(0f, 1f)]
	public float LeapCameraFollow = 0.45f;

	[Header("Leap squash and stretch (presentation only)")]
	[Range(0f, 0.3f)]
	public float CrouchSquash = 0.08f;

	[Range(0f, 0.3f)]
	public float LaunchStretch = 0.12f;

	[Range(0f, 0.3f)]
	public float FallStretch = 0.06f;

	[Range(0f, 0.4f)]
	public float LandingSquash = 0.18f;

	[Min(0f)]
	public float LandingRecover = 0.3f;

	[Tooltip("Forward body pitch in degrees during the descent; a third of it leans back on the launch.")]
	[Range(0f, 30f)]
	public float LeapLean = 10f;

	[Header("Shock ring and dust curtain")]
	public Material ShockMaterial;

	public Color ShockColor = new Color(1f, 0.86f, 0.62f, 0.9f);

	public Color DustWallColor = new Color(0.62f, 0.55f, 0.46f, 0.7f);

	[Min(0.05f)]
	public float ShockWidth = 0.45f;

	[Min(0f)]
	public float DustWallHeight = 1.1f;

	[Tooltip("Shock ring and dust-curtain overshoot beyond the damage radius, as a fraction of it.")]
	[Range(0f, 0.5f)]
	public float ShockOvershoot = 0.12f;

	[Header("Crater")]
	[Range(0f, 24f)]
	public int CraterSlabs = 12;

	[Range(0f, 24f)]
	public int CraterCracks = 12;

	[Min(0.1f)]
	public float CraterRadius = 1.25f;

	[Min(0f)]
	public float CraterSlabHeight = 0.45f;

	[Header("Earth fracture")]
	[Range(12f, 64f)]
	public int RockCount = 38;

	public float RockWidth = 0.55f;

	public float DustSize = 1.1f;

	public float FractureLifetime = 1.1f;

	[Header("Travelling earth crest")]
	[Min(0.25f)]
	public float WaveStoneSpacing = 0.65f;

	[Min(0.01f)]
	public float WaveRiseTime = 0.05f;

	[Min(0.05f)]
	public float WaveSettleTime = 0.24f;

	[Range(0.2f, 1f)]
	public float AftershockHeight = 0.72f;

	[Range(0f, 48f)]
	public int WaveDustCount = 28;

	[Range(0f, 12f)]
	public int WaveChipCount = 6;

	[Header("Fire cleave")]
	[Tooltip("Burning weapon ribbon; the weapon motion style material is used when empty.")]
	public Material TrailMaterial;

	[Tooltip("Clip phase at which the swing whoosh is cued, just ahead of the release.")]
	[Range(0f, 1f)]
	public float SwingSoundPhase = 0.34f;

	[Tooltip("Blade heat envelope phases: start heating, fully hot, start cooling, cold.")]
	public Vector4 BladeHeat = new Vector4(0.08f, 0.38f, 0.52f, 0.75f);

	public Vector4 BackswingBladeHeat = new Vector4(0.58f, 0.7f, 0.8f, 0.95f);

	[Tooltip("Distance of the blade's ground contact as a fraction of the action contact radius.")]
	[Range(0.3f, 1.5f)]
	public float BladeContact = 1f;

	[Min(0.1f)]
	public float FlameHeight = 0.95f;

	[Tooltip("Spacing of the flame tongues that ignite as the front passes.")]
	[Min(0.12f)]
	public float FlameSpacing = 0.3f;

	[Tooltip("Seconds a tongue takes to die down after the front has passed it.")]
	[Min(0.05f)]
	public float FlameBurn = 0.5f;

	[Min(0f)]
	public float SheetHeight = 0.5f;

	[Min(0.01f)]
	public float SplitWidth = 0.12f;

	[Tooltip("Seconds for the molten split to cool from white heat.")]
	[Min(0.1f)]
	public float SplitCool = 1.1f;

	[Range(0f, 6f)]
	public int SplitBranches = 4;

	[Tooltip("Seconds the scorched ground stays after the front passed.")]
	[Min(0.2f)]
	public float ScorchLinger = 1.7f;

	[Min(0f)]
	public float ImpactFlashRadius = 1.1f;

	[Range(0f, 60f)]
	public int EmberCount = 32;

	[Range(0f, 24f)]
	public int SmokeCount = 8;

	public Color LightColor = new Color(1f, 0.5f, 0.16f, 1f);

	[Min(0f)]
	public float LightIntensity = 4f;

	[Min(0.5f)]
	public float LightRange = 5f;

	public Color CoreColor;

	public Color EdgeColor;

	public Color ShadowColor;

	public Color BloodAccent = new Color(0.55f, 0.008f, 0.014f, 0.8f);

	public float FrontHeight = 0.65f;

	public float FrontDepth = 0.35f;

	public float FadeDuration = 0.25f;

	public float DebrisHeight = 0.35f;

	public float TrailLifetime = 0.16f;

	public Vector2 TrailWindow = new Vector2(0.28f, 0.56f);

	public Vector2 BackswingTrailWindow = new Vector2(0.64f, 0.83f);

	[Header("Camera impulses")]
	public CombatCameraShake TakeoffShake = new CombatCameraShake
	{
		Pixels = 0f,
		Duration = 0.12f,
		Frequency = 20f
	};

	public CombatCameraShake ImpactShake = new CombatCameraShake
	{
		Pixels = 1f,
		Duration = 0.15f,
		Frequency = 20f
	};

	public CombatCameraShake AftershockShake = new CombatCameraShake
	{
		Pixels = 0.3f,
		Duration = 0.15f,
		Frequency = 20f
	};

	public GameAudioCueId SwingSound;

	public GameAudioCueId ImpactSound;

	public GameAudioCueId AftershockSound;
}
