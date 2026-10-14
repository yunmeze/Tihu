using System;
using Scellecs.Morpeh;
using UnityEngine;
using UnityEngine.Rendering;

[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public sealed class ElementalSkillEffect : MonoBehaviour
{
	private struct FireTuft
	{
		public Vector3 Center;

		public float Arrival;

		public float Size;

		public float Burn;

		public float Seed;

		public float Lift;

		public float Temperature;
	}

	private struct GroundPiece
	{
		public Vector3 Center;

		public Vector3 Direction;

		public float Arrival;

		public float Height;

		public float Lean;

		public float Width;

		public float Length;

		public Color Face;
	}

	private const int MaxTufts = 220;

	private FireTuft[] _tufts;

	private int _tuftCount;

	private Vector3 _contactPoint;

	private static readonly int ShapeId = Shader.PropertyToID("_Shape");

	private static readonly int ClockId = Shader.PropertyToID("_Clock");

	private static readonly int StyleId = Shader.PropertyToID("_Style");

	private static readonly int ImpactId = Shader.PropertyToID("_Impact");

	private static readonly int LimitsId = Shader.PropertyToID("_Limits");

	private MaterialPropertyBlock _field;

	private readonly float[] _fieldLimits = new float[49];

	private float _fireScale;

	public ParticleSystem Sparks;

	public ParticleSystem Rubble;

	[Range(12f, 64f)]
	public int Segments = 48;

	[Range(0f, 1f)]
	public float Irregularity = 0.35f;

	public bool EarthCrests;

	[Tooltip("Fire Cleave instance: billboard flames, scorched ground layer, smoke and glow light.")]
	public bool FireFlames;

	public ParticleSystem Smoke;

	public Light Glow;

	private int Capacity;

	private GroundPiece[] _pieces;

	private int _pieceCount;

	private int _dustPending;

	private int _chipsPending;

	private int _dustTotal;

	private int _chipsTotal;

	private Vector3[] _vertices;

	private Vector3[] _normals;

	private Vector4[] _uv;

	private Color[] _colors;

	private readonly float[] _limits = new float[65];

	private const float Unclipped = 1000f;

	private Mesh _mesh;

	private MeshRenderer _renderer;

	private CombatSkillVisualEvent _event;

	private CombatSkillPresentationProfile _profile;

	private int _used;

	private float _lastAge;

	private const int ShockSegments = 56;

	private int ShockCapacity = 1680;

	private Mesh _shockMesh;

	private MeshRenderer _shockRenderer;

	private Vector3[] _shockVertices;

	private Color[] _shockColors;

	private Vector3[] _shockUv;

	private int _shockUsed;

	private float _particleLinger;

	private readonly Vector3[] _corners = new Vector3[5];

	private CombatSkillVisualKind Kind => _event.Kind;

	private bool Echo => _event.Pulse.LegendarySecondary;

	private float FireStrength
	{
		get
		{
			if (!Echo)
			{
				return 1f;
			}
			return 0.6f;
		}
	}

	public bool SupportsCrests => _pieces != null;

	public bool Busy { get; private set; }

	public bool Decorative
	{
		get
		{
			if (_event.Kind != CombatSkillVisualKind.Front && _event.Kind != CombatSkillVisualKind.Scorch)
			{
				return _event.Kind != CombatSkillVisualKind.BrokenGround;
			}
			return false;
		}
	}

	public double StartedAt => _event.StartsAt;

	public int ParticleCount => ((Sparks != null) ? Sparks.particleCount : 0) + _dustPending;

	public int RubbleCount => ((Rubble != null) ? Rubble.particleCount : 0) + ((Smoke != null) ? Smoke.particleCount : 0) + _chipsPending;

	private bool Fire => _event.Pulse.Cast.Skill.Id == CombatSkillId.Cleave;

	private int ShockCount
	{
		get
		{
			if (!(_event.Pulse.WaveWidth > 0f) && !(_event.Pulse.Angle >= 359f))
			{
				return Mathf.Max(8, Mathf.CeilToInt(56f * _event.Pulse.Angle / 360f));
			}
			return 56;
		}
	}

	private void FireBegin(int embers, int smoke)
	{
		if (_tufts == null)
		{
			_tufts = new FireTuft[220];
		}
		_tuftCount = 0;
		_fireScale = FireStrength;
		_contactPoint = Point(0.5f, (Kind == CombatSkillVisualKind.Contact) ? (_event.EndRadius * _profile.BladeContact) : 0f);
		_dustTotal = (_dustPending = ((Sparks != null) ? embers : 0));
		_chipsTotal = (_chipsPending = ((Smoke != null) ? smoke : 0));
		switch (Kind)
		{
		case CombatSkillVisualKind.Front:
			PrepareFront();
			break;
		case CombatSkillVisualKind.Scorch:
			PrepareField(_event.StartRadius * 0.6f, _event.EndRadius, 0.55f, scattered: true);
			break;
		case CombatSkillVisualKind.Burst:
			PrepareBurst();
			break;
		case CombatSkillVisualKind.Contact:
		{
			for (int i = 0; i < 9; i++)
			{
				if (_tuftCount >= 220)
				{
					break;
				}
				float f = Noise(i + 3000) * MathF.PI * 2f;
				float num = Mathf.Sqrt(Noise(i + 3010)) * 0.45f;
				AddTuft(_contactPoint + new Vector3(Mathf.Cos(f), 0f, Mathf.Sin(f)) * num, Noise(i + 3020) * 0.04f, 1.15f + Noise(i + 3030) * 0.5f, 0.28f + Noise(i + 3040) * 0.15f, i + 3000);
			}
			break;
		}
		}
		if (Glow != null)
		{
			Glow.color = _profile.LightColor;
			Glow.range = _profile.LightRange;
			Glow.intensity = 0f;
			Glow.enabled = false;
		}
	}

	private void AddTuft(Vector3 center, float arrival, float size, float burn, int seed)
	{
		if (_tuftCount < 220)
		{
			_tufts[_tuftCount++] = new FireTuft
			{
				Center = center,
				Arrival = arrival,
				Size = size,
				Burn = burn,
				Seed = Noise(seed + 77) * 10f,
				Lift = Noise(seed + 91),
				Temperature = 0.72f + Noise(seed + 97) * 0.32f
			};
		}
	}

	private float Arrival(float radius)
	{
		return Mathf.Max(0f, radius - _event.StartRadius) / Mathf.Max(0.01f, _event.Speed);
	}

	private void PrepareFront()
	{
		float start = Mathf.Max(0.3f, _event.StartRadius * 0.82f);
		PrepareField(start, _event.EndRadius, 1f, scattered: false);
	}

	private void PrepareField(float start, float end, float density, bool scattered)
	{
		bool flag = _event.Pulse.WaveWidth > 0f;
		bool flag2 = _event.Pulse.Angle >= 359f && !flag;
		float num = (flag ? _event.Pulse.WaveWidth : Mathf.Max(0.01f, _event.Pulse.Angle * (MathF.PI / 180f)));
		float b = (flag ? (num * (end - start)) : (0.5f * num * (end * end - start * start)));
		float num2 = Mathf.Max(_profile.FlameSpacing / Mathf.Sqrt(density), Mathf.Sqrt(Mathf.Max(0.01f, b) / 176f));
		float num3 = end * 1.12f;
		float num4 = (float)CastSeed() * 0.013f;
		int num5 = 0;
		for (float num6 = start + num2 * 0.4f; num6 <= num3; num6 += num2 * (0.75f + Noise(num5 + 3150) * 0.35f))
		{
			if (_tuftCount >= 220)
			{
				break;
			}
			float num7 = (flag ? num : (num6 * num));
			int num8 = Mathf.Max(1, Mathf.RoundToInt(num7 * (flag2 ? 1f : 1.24f) / num2));
			for (int i = 0; i < num8; i++)
			{
				if (_tuftCount >= 220)
				{
					break;
				}
				int num9 = num5 * 131 + i * 17 + 3100;
				float num10 = ((float)i + 0.5f + (Noise(num9) - 0.5f) * 0.9f) / (float)num8;
				num10 = (flag2 ? Mathf.Repeat(num10 + Noise(num5 + 3160), 1f) : Mathf.Lerp(-0.12f, 1.12f, num10));
				float num11 = Mathf.Max(start, num6 + (Noise(num9 + 1) - 0.5f) * num2 * 0.8f);
				if (num11 > Limit(Mathf.Clamp01(num10)))
				{
					continue;
				}
				Vector3 center = Point(num10, num11);
				float num12 = Mathf.Min(flag2 ? 1f : (Mathf.Min(num10, 1f - num10) * (flag ? 2.2f : 3.2f)), (end - num11) / Mathf.Max(0.01f, end) * 5f);
				float num13 = Mathf.PerlinNoise(center.x * 0.9f + num4, center.z * 0.9f - num4) - 0.5f;
				float num14 = num12 + num13 * 0.9f;
				if (num14 < 0f)
				{
					continue;
				}
				float num15 = Mathf.PerlinNoise(center.x * 0.7f - num4, center.z * 0.7f + num4 + 31.7f);
				if (!(Noise(num9 + 8) > 0.35f + num15 * 0.9f))
				{
					float num16 = Mathf.Clamp01(num14 * 2.5f);
					if (!(num16 < 0.3f))
					{
						num16 = Mathf.Lerp(0.6f, 1f, num16);
						float num17 = Mathf.Lerp(1.1f, 0.75f, Mathf.InverseLerp(start, Mathf.Max(start + 0.01f, end), num11));
						float arrival = (scattered ? (Noise(num9 + 2) * _event.Duration * 0.35f) : Arrival(Mathf.Min(num11, end)));
						float num18 = (scattered ? (0.35f + Noise(num9 + 3) * Noise(num9 + 6) * 1.6f) : (0.6f + Noise(num9 + 3) * 0.8f)) * (0.65f + num15 * 0.7f);
						AddTuft(center, arrival, num17 * num18 * num16, _profile.FlameBurn * (0.45f + Noise(num9 + 4) * Noise(num9 + 5) * 2.2f) * (scattered ? 1.5f : 1f), num9);
					}
				}
			}
			num5++;
		}
	}

	private void PrepareBurst()
	{
		float endRadius = _event.EndRadius;
		for (int i = 0; i < 26; i++)
		{
			if (_tuftCount >= 220)
			{
				break;
			}
			float f = (float)i * 2.39996f + Noise(i + 3300);
			float num = Mathf.Sqrt(((float)i + 0.5f) / 26f) * endRadius * 0.8f;
			Vector3 center = new Vector3(Mathf.Sin(f) * num, 0f, Mathf.Cos(f) * num);
			AddTuft(center, num / endRadius * 0.09f, (1.35f - num / endRadius * 0.6f) * (0.8f + Noise(i + 3310) * 0.4f), 0.35f + Noise(i + 3320) * 0.2f, i + 3300);
		}
	}

	private float FireHold()
	{
		return Kind switch
		{
			CombatSkillVisualKind.Contact => 0.9f, 
			CombatSkillVisualKind.Burst => 1.3f, 
			CombatSkillVisualKind.Scorch => _event.Duration + 0.7f, 
			_ => _event.Duration + Mathf.Max(Echo ? 0.9f : (_profile.ScorchLinger + 0.9f), _profile.FlameBurn * 3f) + 0.2f, 
		};
	}

	private float TuftEnvelope(in FireTuft tuft, float age)
	{
		float num = age - tuft.Arrival;
		if (num < 0f)
		{
			return 0f;
		}
		if (Kind == CombatSkillVisualKind.Scorch)
		{
			float num2 = Mathf.Max(0.05f, _event.Pulse.Cast.Skill.Action.ScorchInterval);
			float num3 = Mathf.Repeat(num + tuft.Lift * num2, num2) / num2;
			return (1f - Mathf.Clamp01((age - _event.Duration) / 0.5f)) * Mathf.Clamp01(num / 0.07f) * (0.35f + 0.65f * Mathf.Exp((0f - num3) * 4f));
		}
		if (num < 0.07f)
		{
			return Mathf.Sin(num / 0.07f * MathF.PI * 0.5f) * 1.15f;
		}
		return 1.15f * Mathf.Exp((0f - (num - 0.07f)) / Mathf.Max(0.02f, tuft.Burn));
	}

	private void FireFlamesLayer(float age)
	{
		float num = _profile.FlameHeight * _fireScale * ((Kind == CombatSkillVisualKind.Scorch) ? 0.5f : ((Kind == CombatSkillVisualKind.Burst) ? 1.25f : 1f));
		for (int i = 0; i < _tuftCount; i++)
		{
			ref FireTuft reference = ref _tufts[i];
			float num2 = TuftEnvelope(in reference, age);
			if (!(num2 < 0.03f))
			{
				float num3 = age - reference.Arrival;
				float num4 = ((Kind == CombatSkillVisualKind.Front) ? (1f + 0.8f * Mathf.Exp((0f - num3) / 0.11f)) : 1f);
				float num5 = 1f + 0.22f * Mathf.Sin(age * (8f + reference.Lift * 5f) + reference.Seed * 3f);
				float num6 = num * reference.Size * num4 * num5 * Mathf.Pow(Mathf.Min(1.15f, num2), 0.35f);
				float num7 = Mathf.Clamp01(num2);
				Tongue(reference.Center, num6 * 0.27f + 0.03f, num6, reference.Seed, num7, Mathf.Clamp01(num2 * 1.8f), reference.Temperature);
				if (i % 4 == 0 && num7 > 0.35f)
				{
					Halo(reference.Center + Vector3.up * num6 * 0.3f, num6 * 0.8f, _profile.LightColor, num7 * 0.18f * _fireScale);
				}
			}
		}
		if (Kind == CombatSkillVisualKind.Contact || Kind == CombatSkillVisualKind.Burst)
		{
			float num8 = age / 0.16f;
			if (num8 < 1f)
			{
				float size = ((Kind == CombatSkillVisualKind.Burst) ? 1.6f : 1.2f) * (0.6f + 0.4f * num8);
				Halo(_contactPoint + Vector3.up * 0.45f, size, new Color(1f, 0.8f, 0.45f, 1f), (1f - num8) * (1f - num8) * 1.4f);
			}
		}
	}

	private void Tongue(Vector3 center, float halfWidth, float height, float seed, float heat, float alpha, float temperature = 1f)
	{
		if (_used + 6 <= Capacity)
		{
			Color color = new Color(1f, temperature, 1f, alpha);
			TongueVertex(center, new Vector3(0f - halfWidth, 0f, seed), color, new Vector4(0f, 0f, 0f, heat));
			TongueVertex(center, new Vector3(halfWidth, 0f, seed), color, new Vector4(1f, 0f, 0f, heat));
			TongueVertex(center, new Vector3(halfWidth, height, seed), color, new Vector4(1f, 1f, 0f, heat));
			TongueVertex(center, new Vector3(0f - halfWidth, 0f, seed), color, new Vector4(0f, 0f, 0f, heat));
			TongueVertex(center, new Vector3(halfWidth, height, seed), color, new Vector4(1f, 1f, 0f, heat));
			TongueVertex(center, new Vector3(0f - halfWidth, height, seed), color, new Vector4(0f, 1f, 0f, heat));
		}
	}

	private void Halo(Vector3 center, float size, Color color, float alpha)
	{
		if (_used + 6 <= Capacity && !(alpha <= 0.01f))
		{
			color.a = alpha;
			float num = size * 0.5f;
			Vector3 position = center - Vector3.up * num;
			TongueVertex(position, new Vector3(0f - num, 0f, 0f), color, new Vector4(0f, 0f, 2f, 1f));
			TongueVertex(position, new Vector3(num, 0f, 0f), color, new Vector4(1f, 0f, 2f, 1f));
			TongueVertex(position, new Vector3(num, size, 0f), color, new Vector4(1f, 1f, 2f, 1f));
			TongueVertex(position, new Vector3(0f - num, 0f, 0f), color, new Vector4(0f, 0f, 2f, 1f));
			TongueVertex(position, new Vector3(num, size, 0f), color, new Vector4(1f, 1f, 2f, 1f));
			TongueVertex(position, new Vector3(0f - num, size, 0f), color, new Vector4(0f, 1f, 2f, 1f));
		}
	}

	private void TongueVertex(Vector3 position, Vector3 extent, Color color, Vector4 uv)
	{
		_vertices[_used] = position;
		_normals[_used] = extent;
		_colors[_used] = color;
		_uv[_used++] = uv;
	}

	private void FireGroundLayer(float age)
	{
		float num = ((Kind == CombatSkillVisualKind.Front) ? 0f : ((Kind == CombatSkillVisualKind.Scorch) ? 1f : ((Kind == CombatSkillVisualKind.Burst) ? 2f : (-1f))));
		if (!(num < 0f) && _shockUsed + 6 <= ShockCapacity)
		{
			float waveWidth = _event.Pulse.WaveWidth;
			bool flag = _event.Pulse.Angle >= 359f || Kind == CombatSkillVisualKind.Burst;
			float endRadius = _event.EndRadius;
			float num2;
			float num3;
			float z;
			float z2;
			if (waveWidth > 0f)
			{
				num2 = (0f - waveWidth) * 0.5f - 1.1f;
				num3 = 0f - num2;
				z = -1f;
				z2 = endRadius + 1.1f;
			}
			else if (flag || _event.Pulse.Angle > 180f)
			{
				num2 = (z = 0f - endRadius - 1.1f);
				num3 = (z2 = endRadius + 1.1f);
			}
			else
			{
				num3 = Mathf.Max(1.2f, endRadius * Mathf.Sin(_event.Pulse.Angle * 0.5f * (MathF.PI / 180f))) + 1.1f;
				num2 = 0f - num3;
				z = -1.2f;
				z2 = endRadius + 1.1f;
			}
			Color white = Color.white;
			Vector3 position = new Vector3(num2, 0.014f, z);
			Vector3 position2 = new Vector3(num3, 0.014f, z);
			Vector3 position3 = new Vector3(num3, 0.014f, z2);
			Vector3 position4 = new Vector3(num2, 0.014f, z2);
			GroundVertex(position, white, 0f, 0f, 0f);
			GroundVertex(position2, white, 0f, 0f, 0f);
			GroundVertex(position3, white, 0f, 0f, 0f);
			GroundVertex(position, white, 0f, 0f, 0f);
			GroundVertex(position3, white, 0f, 0f, 0f);
			GroundVertex(position4, white, 0f, 0f, 0f);
			if (_field == null)
			{
				_field = new MaterialPropertyBlock();
			}
			for (int i = 0; i <= Segments && i < _fieldLimits.Length; i++)
			{
				_fieldLimits[i] = Mathf.Min(_limits[i], 1000f);
			}
			CombatSkillActionSettings action = _event.Pulse.Cast.Skill.Action;
			float num4 = ((Kind == CombatSkillVisualKind.Burst) ? 0f : _event.StartRadius);
			float y = ((Kind == CombatSkillVisualKind.Burst) ? 8f : Mathf.Max(0.01f, _event.Speed));
			float w = ((Kind == CombatSkillVisualKind.Scorch) ? (_event.Duration + 0.4f) : ((Kind == CombatSkillVisualKind.Burst) ? 0.5f : (_event.Duration + (Echo ? 0.6f : _profile.ScorchLinger))));
			float y2 = ((Kind == CombatSkillVisualKind.Front && !Echo) ? 1f : 0f);
			_field.SetVector(ShapeId, new Vector4(num4, endRadius, flag ? MathF.PI : (_event.Pulse.Angle * 0.5f * (MathF.PI / 180f)), waveWidth));
			_field.SetVector(ClockId, new Vector4(age, y, _event.Duration, w));
			_field.SetVector(StyleId, new Vector4(_fireScale, y2, num, (float)(CastSeed() % 997) * 0.137f));
			_field.SetVector(ImpactId, new Vector4(num4 * _profile.BladeContact, _profile.SplitCool, action.ScorchInterval, _event.Duration));
			_field.SetFloatArray(LimitsId, _fieldLimits);
			_shockRenderer.SetPropertyBlock(_field);
		}
	}

	private void GroundVertex(Vector3 position, Color color, float heat, float profile, float mode)
	{
		_shockVertices[_shockUsed] = position;
		_shockColors[_shockUsed] = color;
		_shockUv[_shockUsed++] = new Vector3(heat, profile, mode);
	}

	private void EmitFire(float age)
	{
		if (Sparks != null)
		{
			EmitFireParticles(age, smoke: false);
		}
		if (Smoke != null)
		{
			EmitFireParticles(age, smoke: true);
		}
		if (Glow != null)
		{
			FireLight(age);
		}
	}

	private void EmitFireParticles(float age, bool smoke)
	{
		int num = (smoke ? _chipsTotal : _dustTotal);
		ref int reference = ref smoke ? ref _chipsPending : ref _dustPending;
		while (reference > 0)
		{
			int num2 = num - reference;
			float num3 = ((float)num2 + 0.5f) / (float)Mathf.Max(1, num);
			bool flag = false;
			float across = Mathf.Repeat((float)num2 * 0.618034f + 0.21f, 1f);
			float num4;
			Vector3 vector2;
			Vector3 direction;
			switch (Kind)
			{
			case CombatSkillVisualKind.Front:
			{
				float num5 = Mathf.Lerp(_event.StartRadius, _event.EndRadius, num3);
				num4 = Arrival(num5) + (smoke ? (0.12f + Noise(num2 + 5000) * 0.25f) : 0f);
				flag = num5 > Limit(across);
				if (!Echo && num2 % 2 == 0)
				{
					across = 0.5f + (Noise(num2 + 5005) - 0.5f) * 0.08f;
				}
				vector2 = Point(across, num5);
				Vector3 normalized = Point(across, 1f).normalized;
				direction = (smoke ? (normalized * 0.3f + Vector3.up * (0.45f + Noise(num2 + 5010) * 0.4f)) : (normalized * (0.5f + Noise(num2 + 5020) * 1.4f) + Vector3.up * (1.6f + Noise(num2 + 5030) * 2.4f)));
				break;
			}
			case CombatSkillVisualKind.Scorch:
			{
				num4 = num3 * _event.Duration;
				float a = Mathf.Lerp(_event.StartRadius * 0.6f, _event.EndRadius, Noise(num2 + 5040));
				vector2 = Point(across, Mathf.Min(a, Limit(across)));
				direction = (smoke ? (Vector3.up * (0.35f + Noise(num2 + 5050) * 0.3f)) : (Vector3.up * (1.2f + Noise(num2 + 5060) * 1.8f)));
				break;
			}
			default:
			{
				num4 = (smoke ? (0.05f + Noise(num2 + 5070) * 0.15f) : (Noise(num2 + 5080) * 0.03f));
				float f = (float)num2 * 2.39996f + Noise(num2 + 5090);
				Vector3 vector = new Vector3(Mathf.Sin(f), 0f, Mathf.Cos(f));
				if (Kind == CombatSkillVisualKind.Contact)
				{
					vector = (vector + Vector3.forward * 0.6f).normalized;
				}
				vector2 = _contactPoint + vector * (smoke ? 0.25f : 0.1f);
				direction = (smoke ? (vector * 0.5f + Vector3.up * (0.5f + Noise(num2 + 5100) * 0.4f)) : (vector * (1.6f + Noise(num2 + 5110) * 3.2f) + Vector3.up * (2.2f + Noise(num2 + 5120) * 3.4f)));
				break;
			}
			}
			if (age < num4)
			{
				break;
			}
			reference--;
			if (!flag && !(age - num4 > 0.2f))
			{
				ParticleSystem.EmitParams emitParams = new ParticleSystem.EmitParams
				{
					position = base.transform.TransformPoint(vector2 + Vector3.up * (smoke ? 0.25f : 0.12f)),
					velocity = base.transform.TransformDirection(direction) * (Echo ? 0.7f : 1f),
					randomSeed = (uint)(11 + num2 + CastSeed())
				};
				if (smoke)
				{
					emitParams.startSize = (0.7f + Noise(num2 + 5130) * 0.6f) * ((Kind == CombatSkillVisualKind.Front) ? 1f : 1.2f);
					Smoke.Emit(emitParams, 1);
				}
				else
				{
					emitParams.startSize = 0.035f + Noise(num2 + 5140) * 0.05f;
					emitParams.startColor = Color.Lerp(new Color(1f, 0.78f, 0.32f, 1f), new Color(1f, 0.3f, 0.04f, 1f), Noise(num2 + 5150));
					Sparks.Emit(emitParams, 1);
				}
			}
		}
	}

	private void FireLight(float age)
	{
		float num = 0.82f + 0.18f * Mathf.PerlinNoise(age * 11f, _event.Pulse.Cast.Id % 97);
		Vector3 position;
		float num2;
		switch (Kind)
		{
		case CombatSkillVisualKind.Contact:
		case CombatSkillVisualKind.Burst:
			num2 = ((age < 0.035f) ? (age / 0.035f) : Mathf.Exp((0f - (age - 0.035f)) / 0.2f)) * ((Kind == CombatSkillVisualKind.Burst) ? 1.15f : 1f);
			position = _contactPoint + Vector3.up * 0.6f;
			break;
		case CombatSkillVisualKind.Front:
		{
			float num3 = Mathf.Min(_event.EndRadius, _event.StartRadius + age * _event.Speed);
			num2 = 0.55f * ((age < _event.Duration) ? 1f : Mathf.Exp((0f - (age - _event.Duration)) / (_profile.FlameBurn * 1.2f)));
			position = Point(0.5f, num3 * 0.7f) + Vector3.up * 0.7f;
			break;
		}
		case CombatSkillVisualKind.Scorch:
			num2 = 0.3f * Mathf.Clamp01(age / 0.15f) * (1f - Mathf.Clamp01((age - _event.Duration) / 0.5f));
			position = Point(0.5f, (_event.StartRadius + _event.EndRadius) * 0.5f) + Vector3.up * 0.6f;
			break;
		default:
			num2 = 0f;
			position = Vector3.zero;
			break;
		}
		num2 *= _profile.LightIntensity * num * _fireScale;
		Glow.enabled = num2 > 0.03f;
		if (Glow.enabled)
		{
			Glow.transform.position = base.transform.TransformPoint(position);
			Glow.intensity = num2;
		}
	}

	public void Warm(bool detailedEarth = true, Material shock = null)
	{
		if (!(_mesh != null))
		{
			if (Sparks != null)
			{
				_particleLinger = Sparks.main.startLifetime.constantMax;
			}
			if (Rubble != null)
			{
				_particleLinger = Mathf.Max(_particleLinger, Rubble.main.startLifetime.constantMax);
			}
			if (Smoke != null)
			{
				_particleLinger = Mathf.Max(_particleLinger, Smoke.main.startLifetime.constantMax);
			}
			if (FireFlames)
			{
				ShockCapacity = 3024;
			}
			if (shock != null)
			{
				WarmShock(shock);
			}
			Capacity = (FireFlames ? 6000 : ((EarthCrests && detailedEarth) ? 19200 : 2304));
			_vertices = new Vector3[Capacity];
			_normals = new Vector3[Capacity];
			_uv = new Vector4[Capacity];
			_colors = new Color[Capacity];
			if (Glow != null)
			{
				Glow.enabled = false;
			}
			if (EarthCrests && detailedEarth)
			{
				_pieces = new GroundPiece[320];
			}
			_mesh = new Mesh
			{
				name = "Pooled elemental front"
			};
			_mesh.MarkDynamic();
			ushort[] array = new ushort[Capacity];
			for (int i = 0; i < array.Length; i++)
			{
				array[i] = (ushort)i;
			}
			_mesh.SetVertexBufferParams(Capacity, new VertexAttributeDescriptor(VertexAttribute.Position, VertexAttributeFormat.Float32, 3, 0), new VertexAttributeDescriptor(VertexAttribute.Normal, VertexAttributeFormat.Float32, 3, 1), new VertexAttributeDescriptor(VertexAttribute.Color, VertexAttributeFormat.Float32, 4, 2), new VertexAttributeDescriptor(VertexAttribute.TexCoord0, VertexAttributeFormat.Float32, 4, 3));
			_mesh.SetIndexBufferParams(Capacity, IndexFormat.UInt16);
			_mesh.SetIndexBufferData(array, 0, 0, Capacity);
			_mesh.subMeshCount = 1;
			GetComponent<MeshFilter>().sharedMesh = _mesh;
			_renderer = GetComponent<MeshRenderer>();
			_renderer.shadowCastingMode = ShadowCastingMode.Off;
			_renderer.receiveShadows = false;
			_renderer.lightProbeUsage = LightProbeUsage.Off;
			_renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
			if (GetComponent<CombatFlashExcluded>() == null)
			{
				base.gameObject.AddComponent<CombatFlashExcluded>();
			}
			Stop();
		}
	}

	private void WarmShock(Material material)
	{
		GameObject gameObject = new GameObject(FireFlames ? "Fire ground layer" : "Seismic shock layer");
		gameObject.transform.SetParent(base.transform, worldPositionStays: false);
		_shockMesh = new Mesh
		{
			name = "Pooled seismic shock"
		};
		_shockMesh.MarkDynamic();
		_shockVertices = new Vector3[ShockCapacity];
		_shockColors = new Color[ShockCapacity];
		_shockUv = new Vector3[ShockCapacity];
		ushort[] array = new ushort[ShockCapacity];
		for (int i = 0; i < array.Length; i++)
		{
			array[i] = (ushort)i;
		}
		_shockMesh.SetVertexBufferParams(ShockCapacity, new VertexAttributeDescriptor(VertexAttribute.Position, VertexAttributeFormat.Float32, 3, 0), new VertexAttributeDescriptor(VertexAttribute.Color, VertexAttributeFormat.Float32, 4, 1), new VertexAttributeDescriptor(VertexAttribute.TexCoord0, VertexAttributeFormat.Float32, 3, 2));
		_shockMesh.SetIndexBufferParams(ShockCapacity, IndexFormat.UInt16);
		_shockMesh.SetIndexBufferData(array, 0, 0, ShockCapacity);
		_shockMesh.subMeshCount = 1;
		gameObject.AddComponent<MeshFilter>().sharedMesh = _shockMesh;
		_shockRenderer = gameObject.AddComponent<MeshRenderer>();
		_shockRenderer.sharedMaterial = material;
		_shockRenderer.shadowCastingMode = ShadowCastingMode.Off;
		_shockRenderer.receiveShadows = false;
		_shockRenderer.lightProbeUsage = LightProbeUsage.Off;
		_shockRenderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
		_shockRenderer.enabled = false;
	}

	public void Begin(CombatSkillVisualEvent value, int particles, int rubble)
	{
		Warm();
		_event = value;
		_profile = value.Pulse.Cast.Skill.Presentation;
		_lastAge = 0f;
		_dustPending = (_chipsPending = 0);
		_pieceCount = 0;
		Busy = true;
		base.gameObject.SetActive(value: true);
		base.transform.SetPositionAndRotation(value.Pulse.Origin + Vector3.up * 0.025f, Quaternion.LookRotation(value.Pulse.Direction));
		bool flag = value.Kind == CombatSkillVisualKind.Scorch || value.Kind == CombatSkillVisualKind.BrokenGround || value.Kind == CombatSkillVisualKind.Uplift;
		_renderer.sharedMaterial = (flag ? _profile.GroundMaterial : _profile.FrontMaterial);
		if (!Fire && _profile.RockMaterial != null && value.Kind != CombatSkillVisualKind.Shadow && value.Kind != CombatSkillVisualKind.BloodLatch && value.Kind != CombatSkillVisualKind.Mark)
		{
			_renderer.sharedMaterial = _profile.RockMaterial;
		}
		if (Fire)
		{
			_renderer.sharedMaterial = _profile.FrontMaterial;
		}
		_renderer.enabled = true;
		for (int i = 0; i <= Segments; i++)
		{
			_limits[i] = (Fire ? value.EndRadius : 1000f);
			if (Fire)
			{
				Vector3 vector = base.transform.TransformPoint(Point((float)i / (float)Segments, value.EndRadius));
				Vector3 occlusionOrigin = value.Pulse.OcclusionOrigin;
				if (CombatSkillGeometry.Occluded(occlusionOrigin, vector, out var distance))
				{
					Vector3 vector2 = vector - occlusionOrigin;
					vector2.y = 0f;
					Vector3 vector3 = base.transform.InverseTransformPoint(occlusionOrigin + vector2.normalized * distance);
					_limits[i] = ((value.Pulse.WaveWidth > 0f) ? Mathf.Max(0f, vector3.z) : new Vector2(vector3.x, vector3.z).magnitude);
				}
			}
		}
		if (Fire && FireFlames)
		{
			FireBegin(particles, rubble);
			Tick();
			return;
		}
		bool flag2 = EarthCrests && !Fire && value.Kind == CombatSkillVisualKind.Front;
		if (EarthCrests && !Fire && (value.Kind == CombatSkillVisualKind.Front || value.Kind == CombatSkillVisualKind.Burst))
		{
			PrepareEarth();
		}
		if (flag2)
		{
			_dustTotal = (_dustPending = ((Sparks != null) ? particles : 0));
			_chipsTotal = (_chipsPending = ((Rubble != null) ? rubble : 0));
		}
		if (!flag2 && Sparks != null && particles > 0)
		{
			if (!Fire)
			{
				EmitImpactDust(particles);
			}
			else if (value.Kind == CombatSkillVisualKind.Front)
			{
				for (int j = 0; j < particles; j++)
				{
					Vector3 position = Point(((float)j + 0.5f) / (float)particles, value.StartRadius);
					Vector3 direction = ((value.Pulse.WaveWidth > 0f) ? Vector3.forward : position.normalized);
					ParticleSystem.EmitParams emitParams = new ParticleSystem.EmitParams
					{
						position = base.transform.TransformPoint(position),
						velocity = base.transform.TransformDirection(direction) * value.Speed * 0.55f + Vector3.up * (Fire ? 0.9f : 0.45f)
					};
					Sparks.Emit(emitParams, 1);
				}
			}
			else
			{
				Sparks.Emit(particles);
			}
		}
		if (!flag2 && Rubble != null && rubble > 0)
		{
			bool flag3 = value.Kind == CombatSkillVisualKind.Takeoff;
			bool flag4 = value.Kind == CombatSkillVisualKind.Contact;
			for (int k = 0; k < rubble; k++)
			{
				Vector3 vector4 = Point(((float)k + 0.3f) / (float)rubble, (flag3 ? 0.5f : Mathf.Min(value.EndRadius, 1.5f)) * (0.3f + Noise(k + 501) * 0.7f));
				Vector3 direction2 = ((vector4.sqrMagnitude > 0.0001f) ? vector4.normalized : Vector3.forward);
				float num = (flag3 ? (1f + Noise(k + 510) * 1.2f) : (flag4 ? (2.2f + Noise(k + 510) * 3.6f) : (1.4f + Noise(k + 510) * 2.1f)));
				float num2 = (flag3 ? (2f + Noise(k + 520) * 1.6f) : (flag4 ? (4.2f + Noise(k + 520) * 4.2f) : (2.3f + Noise(k + 520) * 2.8f)));
				float startSize = (flag3 ? (0.07f + Noise(k + 530) * 0.09f) : (flag4 ? (0.13f + Noise(k + 530) * 0.32f) : (0.12f + Noise(k + 530) * 0.3f)));
				Rubble.Emit(new ParticleSystem.EmitParams
				{
					position = base.transform.TransformPoint(vector4 + Vector3.up * 0.1f),
					velocity = base.transform.TransformDirection(direction2) * num + Vector3.up * num2,
					startColor = (Fire ? Color.white : Color.Lerp(_profile.EdgeColor, _profile.CoreColor, Noise(k + 540))),
					startSize = startSize,
					randomSeed = (uint)(7 + k + CastSeed())
				}, 1);
			}
		}
		Tick();
	}

	private void EmitImpactDust(int particles)
	{
		CombatSkillVisualKind kind = _event.Kind;
		bool flag = kind == CombatSkillVisualKind.Takeoff;
		bool flag2 = kind == CombatSkillVisualKind.Contact;
		int num = (flag2 ? Mathf.Max(1, particles / 6) : 0);
		for (int i = 0; i < particles; i++)
		{
			float across = ((float)i + Noise(i + 400) * 0.8f) / (float)Mathf.Max(1, particles);
			Vector3 normalized = Point(across, 1f).normalized;
			bool flag3 = i < num;
			float distance;
			float num2;
			float num3;
			float num4;
			if (flag3)
			{
				distance = Noise(i + 410) * 0.35f;
				num2 = 0.4f + Noise(i + 415) * 0.8f;
				num3 = 1.6f + Noise(i + 420) * 1.6f;
				num4 = 1.15f + Noise(i + 430) * 0.5f;
			}
			else if (flag)
			{
				distance = 0.2f + Noise(i + 410) * 0.3f;
				num2 = 2.4f + Noise(i + 415) * 1.8f;
				num3 = 0.2f + Noise(i + 420) * 0.35f;
				num4 = 0.24f + Noise(i + 430) * 0.22f;
			}
			else if (flag2)
			{
				distance = 0.3f + Noise(i + 410) * 0.6f;
				num2 = 4.2f + Noise(i + 415) * 4.2f;
				num3 = 0.35f + Noise(i + 420) * 0.9f;
				num4 = 0.75f + Noise(i + 430) * 0.6f;
			}
			else
			{
				distance = _event.EndRadius * (0.35f + Noise(i + 410) * 0.5f);
				num2 = 2.2f;
				num3 = 0.35f + Noise(i + 420) * 0.5f;
				num4 = 0.7f + Noise(i + 430) * 0.7f;
			}
			ParticleSystem.EmitParams emitParams = new ParticleSystem.EmitParams
			{
				position = base.transform.TransformPoint(Point(across, distance) + Vector3.up * 0.12f),
				velocity = base.transform.TransformDirection(normalized) * num2 + Vector3.up * num3,
				startSize3D = new Vector3(1f, flag3 ? 0.9f : 0.55f, 1f) * (_profile.DustSize * num4),
				randomSeed = (uint)(1 + i + CastSeed())
			};
			Sparks.Emit(emitParams, 1);
		}
	}

	private int CastSeed()
	{
		return _event.Pulse.Cast.Id % 100000 * 173;
	}

	public void Stop()
	{
		Busy = false;
		_dustPending = (_chipsPending = 0);
		if (_renderer != null)
		{
			_renderer.enabled = false;
		}
		if (_shockRenderer != null)
		{
			_shockRenderer.enabled = false;
		}
		if (Sparks != null)
		{
			Sparks.Stop(withChildren: true, ParticleSystemStopBehavior.StopEmittingAndClear);
		}
		if (Rubble != null)
		{
			Rubble.Stop(withChildren: true, ParticleSystemStopBehavior.StopEmittingAndClear);
		}
		if (Smoke != null)
		{
			Smoke.Stop(withChildren: true, ParticleSystemStopBehavior.StopEmittingAndClear);
		}
		if (Glow != null)
		{
			Glow.enabled = false;
		}
		base.gameObject.SetActive(value: false);
	}

	public void Tick()
	{
		if (!Busy)
		{
			return;
		}
		CombatSkillCast cast = _event.Pulse.Cast;
		if (_event.Generation != _event.Timeline.Generation || !CombatSkillTimeline.Alive(World.Default, cast))
		{
			Stop();
			return;
		}
		if (_event.Kind == CombatSkillVisualKind.Mark)
		{
			World world = World.Default;
			Entity followTarget = _event.FollowTarget;
			Stash<CrowdActorComponent> stash = world.GetStash<CrowdActorComponent>();
			if (followTarget.IsNullOrDisposed() || !PackEncounterService.Alive(world, followTarget) || !stash.Has(followTarget) || stash.Get(followTarget).Mark != cast)
			{
				Stop();
				return;
			}
			base.transform.position = world.GetStash<GameObjectComponent>().Get(followTarget).GameObject.transform.position + Vector3.up * 0.04f;
		}
		float num = (float)(_event.Timeline.Time - _event.StartsAt);
		if (num < 0f)
		{
			_renderer.enabled = false;
			if (_shockRenderer != null)
			{
				_shockRenderer.enabled = false;
			}
			if (Glow != null)
			{
				Glow.enabled = false;
			}
			return;
		}
		float num2 = Mathf.Max(_event.Duration + _profile.FadeDuration, 0.7f);
		if (!Fire && (_dustTotal > 0 || _chipsTotal > 0 || (Sparks != null && Sparks.particleCount > 0) || (Rubble != null && Rubble.particleCount > 0)))
		{
			num2 = Mathf.Max(num2, _event.Duration + _particleLinger);
		}
		bool flag = Fire && FireFlames && _event.Kind != CombatSkillVisualKind.BloodLatch;
		if (flag)
		{
			num2 = FireHold();
		}
		if (num > num2)
		{
			Stop();
			return;
		}
		float t = Mathf.Max(0f, num - _lastAge);
		_lastAge = num;
		if (Sparks != null)
		{
			Sparks.Simulate(t, withChildren: true, restart: false, fixedTimeStep: false);
		}
		if (Rubble != null)
		{
			Rubble.Simulate(t, withChildren: true, restart: false, fixedTimeStep: false);
		}
		if (Smoke != null)
		{
			Smoke.Simulate(t, withChildren: true, restart: false, fixedTimeStep: false);
		}
		if (flag)
		{
			EmitFire(num);
		}
		if (EarthCrests && !Fire && _event.Kind == CombatSkillVisualKind.Front)
		{
			EmitEarth(num);
		}
		_used = 0;
		if (_event.Kind == CombatSkillVisualKind.Shadow)
		{
			Stash<GameObjectComponent> stash2 = World.Default.GetStash<GameObjectComponent>();
			if (stash2.Has(cast.Source))
			{
				base.transform.position = stash2.Get(cast.Source).GameObject.transform.position + Vector3.up * 0.018f;
			}
		}
		float num3 = 1f - Mathf.Clamp01((num - _event.Duration) / Mathf.Max(0.01f, _profile.FadeDuration));
		if (flag)
		{
			FireFlamesLayer(num);
		}
		else if (num3 > 0f)
		{
			float radius = ((_event.Speed > 0f) ? Mathf.Min(_event.EndRadius, _event.StartRadius + num * _event.Speed) : Mathf.Lerp(_event.StartRadius, _event.EndRadius, Mathf.Clamp01(num / Mathf.Max(0.01f, _event.Duration))));
			bool flag2 = _event.Kind == CombatSkillVisualKind.Scorch || _event.Kind == CombatSkillVisualKind.BrokenGround || _event.Kind == CombatSkillVisualKind.Uplift;
			if (_event.Kind == CombatSkillVisualKind.Mark)
			{
				Seal(num3);
			}
			else if (_event.Kind == CombatSkillVisualKind.Shadow)
			{
				Shadow(num3);
			}
			else if (_event.Kind == CombatSkillVisualKind.BloodLatch)
			{
				Blood(radius, num3);
			}
			else if (flag2 && Fire)
			{
				Ground(radius, num, num3);
			}
			else if (_event.Kind == CombatSkillVisualKind.Uplift && !Fire)
			{
				Crater(radius, num, num3);
			}
			else if (flag2)
			{
				Fracture(radius, num, num3);
			}
			else if (Fire || (_event.Kind != CombatSkillVisualKind.Contact && _event.Kind != CombatSkillVisualKind.Takeoff))
			{
				if (Fire)
				{
					Flame(radius, num, num3);
				}
				else if (EarthCrests && (_event.Kind == CombatSkillVisualKind.Front || _event.Kind == CombatSkillVisualKind.Burst))
				{
					EarthWave(num, num3);
				}
				else
				{
					Stone(radius, num, num3);
				}
			}
		}
		_mesh.SetVertexBufferData(_vertices, 0, 0, _used, 0, MeshUpdateFlags.DontValidateIndices | MeshUpdateFlags.DontRecalculateBounds);
		_mesh.SetVertexBufferData(_normals, 0, 0, _used, 1, MeshUpdateFlags.DontValidateIndices | MeshUpdateFlags.DontRecalculateBounds);
		_mesh.SetVertexBufferData(_colors, 0, 0, _used, 2, MeshUpdateFlags.DontValidateIndices | MeshUpdateFlags.DontRecalculateBounds);
		_mesh.SetVertexBufferData(_uv, 0, 0, _used, 3, MeshUpdateFlags.DontValidateIndices | MeshUpdateFlags.DontRecalculateBounds);
		Bounds bounds = new Bounds(Vector3.zero, Vector3.one * (_event.EndRadius * 2f + 4f));
		_mesh.SetSubMesh(0, new SubMeshDescriptor(0, _used)
		{
			bounds = bounds,
			vertexCount = _used
		}, MeshUpdateFlags.DontValidateIndices | MeshUpdateFlags.DontRecalculateBounds);
		_mesh.bounds = bounds;
		_renderer.enabled = _used > 0;
		if (_shockRenderer != null)
		{
			_shockUsed = 0;
			if (!Fire)
			{
				ShockLayer(num);
			}
			else if (flag)
			{
				FireGroundLayer(num);
			}
			_shockMesh.SetVertexBufferData(_shockVertices, 0, 0, _shockUsed, 0, MeshUpdateFlags.DontValidateIndices | MeshUpdateFlags.DontRecalculateBounds);
			_shockMesh.SetVertexBufferData(_shockColors, 0, 0, _shockUsed, 1, MeshUpdateFlags.DontValidateIndices | MeshUpdateFlags.DontRecalculateBounds);
			_shockMesh.SetVertexBufferData(_shockUv, 0, 0, _shockUsed, 2, MeshUpdateFlags.DontValidateIndices | MeshUpdateFlags.DontRecalculateBounds);
			_shockMesh.SetSubMesh(0, new SubMeshDescriptor(0, _shockUsed)
			{
				bounds = bounds,
				vertexCount = _shockUsed
			}, MeshUpdateFlags.DontValidateIndices | MeshUpdateFlags.DontRecalculateBounds);
			_shockMesh.bounds = bounds;
			_shockRenderer.enabled = _shockUsed > 0;
		}
	}

	private static float EaseOut(float t)
	{
		t = Mathf.Clamp01(t);
		return 1f - (1f - t) * (1f - t);
	}

	private void ShockLayer(float age)
	{
		CombatSkillVisualKind kind = _event.Kind;
		bool secondary = _event.Pulse.Secondary;
		Color shockColor = _profile.ShockColor;
		Color shadowColor = _profile.ShadowColor;
		shadowColor.a = 0.55f;
		switch (kind)
		{
		case CombatSkillVisualKind.Contact:
		{
			float num13 = age / 0.14f;
			if (num13 < 1f)
			{
				Color color2 = shockColor;
				color2.a *= (1f - num13) * (1f - num13) * 0.85f;
				Disc(_event.EndRadius * (1f + 0.8f * EaseOut(num13)), color2);
			}
			float num14 = age / 0.2f;
			if (num14 < 1f)
			{
				float num15 = Mathf.Lerp(0.25f, _event.EndRadius * 1.5f, EaseOut(num14));
				Color color3 = shockColor;
				color3.a *= 1f - num14;
				Ring(num15, _profile.ShockWidth * 0.6f, color3, 0.45f);
				shadowColor.a *= 1f - num14;
				Ring(num15 * 0.72f, _profile.ShockWidth * 0.9f, shadowColor, 0.8f);
			}
			break;
		}
		case CombatSkillVisualKind.Front:
		case CombatSkillVisualKind.Takeoff:
		{
			bool flag = kind == CombatSkillVisualKind.Takeoff;
			float num = _event.StartRadius;
			float num2 = _event.EndRadius;
			float num3 = (num2 - num) / Mathf.Max(0.01f, _event.Speed);
			if (flag)
			{
				num = 0.15f;
				num2 = 1.25f;
				num3 = 0.16f;
			}
			float num4 = (flag ? 0.5f : (secondary ? 0.7f : 1f));
			float num5 = num2 * (1f + _profile.ShockOvershoot);
			float num6 = num3 * 1.7f + 0.05f;
			float num7 = ((age < num3) ? Mathf.Lerp(num, num2, age / Mathf.Max(0.001f, num3)) : Mathf.Lerp(num2, num5, EaseOut((age - num3) / Mathf.Max(0.001f, num6 - num3))));
			float num8 = num6 + 0.12f;
			float num9 = Mathf.Clamp01(age / num8);
			if (num9 < 1f)
			{
				float num10 = _profile.ShockWidth * (flag ? 0.55f : (secondary ? 0.75f : 1f)) * Mathf.Lerp(1.15f, 0.55f, num9);
				Color color = shockColor;
				color.a *= num4 * Mathf.Pow(1f - num9, 1.3f);
				if (!flag)
				{
					shadowColor.a *= num4 * (1f - num9);
					Ring(Mathf.Max(0f, num7 - num10 * 0.85f), num10 * 1.1f, shadowColor, 0.8f);
				}
				Ring(num7, num10, color, 0.7f);
			}
			float num11 = num8 + 0.4f;
			float num12 = Mathf.Clamp01(age / num11);
			if (num12 < 1f && _profile.DustWallHeight > 0f)
			{
				float radius = Mathf.Lerp(num, num5 * 0.96f, EaseOut(age / (num6 * 1.3f)));
				float height = _profile.DustWallHeight * (flag ? 0.35f : (secondary ? 0.6f : 1f)) * EaseOut(age / 0.13f) * (1f + 0.45f * num12);
				Color dustWallColor = _profile.DustWallColor;
				dustWallColor.a *= Mathf.Pow(1f - num12, 1.5f) * (flag ? 0.8f : 1f);
				Curtain(radius, height, dustWallColor);
			}
			break;
		}
		}
	}

	private void ShockVertex(Vector3 position, Color color, Vector3 uv)
	{
		_shockVertices[_shockUsed] = position;
		_shockColors[_shockUsed] = color;
		_shockUv[_shockUsed++] = uv;
	}

	private void ShockQuad(Vector3 a, Vector3 b, Vector3 c, Vector3 d, Color color, float ua, float ub, float lower, float upper, float breakup)
	{
		if (_shockUsed + 6 <= ShockCapacity)
		{
			ShockVertex(a, color, new Vector3(ua, lower, breakup));
			ShockVertex(b, color, new Vector3(ub, lower, breakup));
			ShockVertex(c, color, new Vector3(ub, upper, breakup));
			ShockVertex(a, color, new Vector3(ua, lower, breakup));
			ShockVertex(c, color, new Vector3(ub, upper, breakup));
			ShockVertex(d, color, new Vector3(ua, upper, breakup));
		}
	}

	private void Ring(float radius, float width, Color color, float breakup)
	{
		if (color.a <= 0.003f || radius <= 0.01f)
		{
			return;
		}
		int shockCount = ShockCount;
		Vector3 vector = Vector3.up * 0.035f;
		for (int i = 0; i < shockCount; i++)
		{
			float across = (float)i / (float)shockCount;
			float across2 = ((float)i + 1f) / (float)shockCount;
			float num = Mathf.Min(Limit(across), Limit(across2));
			if (!(radius - width * 0.5f > num))
			{
				float num2 = Mathf.Min(radius + width * 0.5f, num + 0.05f);
				float distance = Mathf.Max(0f, radius - width * 0.5f);
				float distance2 = Mathf.Min(radius, num2);
				ShockQuad(Point(across, distance) + vector, Point(across2, distance) + vector, Point(across2, distance2) + vector, Point(across, distance2) + vector, color, i, i + 1, 0f, 0.5f, breakup);
				ShockQuad(Point(across, distance2) + vector, Point(across2, distance2) + vector, Point(across2, num2) + vector, Point(across, num2) + vector, color, i, i + 1, 0.5f, 1f, breakup);
			}
		}
	}

	private float CurtainHeight(int vertex, int count)
	{
		return 0.4f + Noise(vertex % count + 1200) * 0.75f + Noise(vertex % count + 1260) * Noise(vertex % count + 1230) * 0.6f;
	}

	private void Curtain(float radius, float height, Color color)
	{
		if (!(color.a <= 0.003f) && !(height <= 0.01f))
		{
			int shockCount = ShockCount;
			for (int i = 0; i < shockCount; i++)
			{
				float across = (float)i / (float)shockCount;
				float across2 = ((float)i + 1f) / (float)shockCount;
				float num = height * CurtainHeight(i, shockCount);
				float num2 = height * CurtainHeight(i + 1, shockCount);
				float num3 = Mathf.Min(radius, Limit(across));
				float num4 = Mathf.Min(radius, Limit(across2));
				ShockQuad(Point(across, num3) + Vector3.up * 0.02f, Point(across2, num4) + Vector3.up * 0.02f, Point(across2, num4 + num2 * 0.4f) + Vector3.up * num2, Point(across, num3 + num * 0.4f) + Vector3.up * num, color, i, i + 1, 0.5f, 1f, 1f);
			}
		}
	}

	private void Disc(float radius, Color color)
	{
		if (color.a <= 0.003f)
		{
			return;
		}
		int shockCount = ShockCount;
		Vector3 vector = Vector3.up * 0.03f;
		Vector3 position = Point(0.5f, 0f) + vector;
		for (int i = 0; i < shockCount; i++)
		{
			if (_shockUsed + 3 > ShockCapacity)
			{
				break;
			}
			float across = (float)i / (float)shockCount;
			float across2 = ((float)i + 1f) / (float)shockCount;
			ShockVertex(position, color, new Vector3(i, 0.5f, 0.3f));
			ShockVertex(Point(across, Mathf.Min(radius, Limit(across))) + vector, color, new Vector3(i, 1f, 0.3f));
			ShockVertex(Point(across2, Mathf.Min(radius, Limit(across2))) + vector, color, new Vector3(i + 1, 1f, 0.3f));
		}
	}

	private Vector3 Point(float across, float distance)
	{
		if (_event.Pulse.WaveWidth > 0f)
		{
			return new Vector3((across - 0.5f) * _event.Pulse.WaveWidth, 0f, distance);
		}
		float f = (across - 0.5f) * _event.Pulse.Angle * (MathF.PI / 180f);
		return new Vector3(Mathf.Sin(f) * distance, 0f, Mathf.Cos(f) * distance);
	}

	private float Noise(int seed)
	{
		return Mathf.Repeat(Mathf.Sin((float)seed * 12.9898f + (float)_event.Pulse.Cast.Id * 2.73f) * 43758.547f, 1f);
	}

	private Color Shade(Color c, float alpha)
	{
		c.a *= alpha;
		return c;
	}

	private void Triangle(Vector3 a, Vector3 b, Vector3 c, Color ca, Color cb, Color cc, Vector2 ua, Vector2 ub, Vector2 uc)
	{
		if (_used + 3 <= Capacity)
		{
			Vector3 vector = Vector3.Cross(b - a, c - a).normalized;
			if (vector.y < 0f)
			{
				vector = -vector;
			}
			_normals[_used] = (_normals[_used + 1] = (_normals[_used + 2] = vector));
			float z = (Fire ? 3f : 0f);
			_vertices[_used] = a;
			_colors[_used] = ca;
			_uv[_used++] = new Vector4(ua.x, ua.y, z, 0f);
			_vertices[_used] = b;
			_colors[_used] = cb;
			_uv[_used++] = new Vector4(ub.x, ub.y, z, 0f);
			_vertices[_used] = c;
			_colors[_used] = cc;
			_uv[_used++] = new Vector4(uc.x, uc.y, z, 0f);
		}
	}

	private void Quad(Vector3 a, Vector3 b, Vector3 c, Vector3 d, Color lower, Color upper, float u)
	{
		Triangle(a, b, c, lower, lower, upper, new Vector2(u, 0f), new Vector2(u + 1f, 0f), new Vector2(u + 1f, 1f));
		Triangle(a, c, d, lower, upper, upper, new Vector2(u, 0f), new Vector2(u + 1f, 1f), new Vector2(u, 1f));
	}

	private void Flame(float radius, float age, float fade)
	{
		float num = (_event.Pulse.LegendarySecondary ? 0.5f : 1f);
		for (int i = 0; i < Segments; i++)
		{
			if (!(radius > Mathf.Min(_limits[i], _limits[i + 1]) + 0.08f))
			{
				Vector3 vector = Point((float)i / (float)Segments, radius);
				Vector3 vector2 = Point(((float)i + 1f) / (float)Segments, radius);
				float num2 = 0.55f + Noise(i) * 0.55f + Mathf.Sin(age * 22f + (float)i * 2.1f) * 0.12f;
				float num3 = _profile.FrontHeight * num2;
				if (_event.Kind == CombatSkillVisualKind.Contact)
				{
					num3 *= 1.1f;
				}
				if (_event.Kind == CombatSkillVisualKind.Burst)
				{
					num3 *= 1.45f;
				}
				Vector3 vector3 = Point((float)i / (float)Segments, Mathf.Max(0f, radius - _profile.FrontDepth));
				Vector3 b = Point(((float)i + 1f) / (float)Segments, Mathf.Max(0f, radius - _profile.FrontDepth));
				Color color = Shade(_profile.CoreColor, fade * num);
				Color color2 = Shade(_profile.EdgeColor, fade * 0.65f * num);
				Color cc = Shade(_profile.EdgeColor, 0f);
				Quad(vector3, b, vector2 + Vector3.up * 0.09f, vector + Vector3.up * 0.09f, Shade(_profile.ShadowColor, fade * 0.75f), color, i);
				Quad(vector + Vector3.up * 0.08f, vector2 + Vector3.up * 0.08f, vector2 + Vector3.up * (num3 * 0.4f), vector + Vector3.up * (num3 * 0.4f), color, color2, i);
				Vector3 c = Vector3.Lerp(vector, vector2, 0.3f + Noise(i + 60) * 0.4f) + Vector3.up * num3 + (vector3 - vector) * 0.35f;
				Triangle(vector + Vector3.up * (num3 * 0.38f), vector2 + Vector3.up * (num3 * 0.38f), c, color2, color2, cc, new Vector2(i, 0f), new Vector2(i + 1, 0f), new Vector2((float)i + 0.5f, 1f));
			}
		}
	}

	private void Stone(float radius, float age, float fade)
	{
		if (_event.Kind == CombatSkillVisualKind.Takeoff)
		{
			return;
		}
		bool secondary = _event.Pulse.Secondary;
		int num = ((_event.Kind == CombatSkillVisualKind.Front) ? 14 : 11);
		for (int i = 0; i < num; i++)
		{
			float across = ((float)i + Noise(i + 710) * 0.8f) / (float)num;
			float num2 = radius * (0.84f + Noise(i + 720) * 0.16f);
			if (!(num2 > Limit(across)))
			{
				Vector3 center = Point(across, num2);
				float width = _profile.RockWidth * (0.35f + Noise(i + 740) * 0.55f);
				float num3 = (secondary ? 0.4f : 0.7f);
				float height = _profile.DebrisHeight * num3 * (0.4f + Noise(i + 730) * 0.6f) * fade;
				Plate(center, width, height, i + 700, fade, Noise(i + 750) * 360f);
			}
		}
	}

	private void PrepareEarth()
	{
		float waveStoneSpacing = _profile.WaveStoneSpacing;
		float num = Mathf.Max(0.01f, _event.Pulse.Angle * (MathF.PI / 180f));
		bool flag = _event.Pulse.Angle >= 359f;
		bool secondary = _event.Pulse.Secondary;
		int num2 = 0;
		float num3 = Mathf.Max(_event.StartRadius, 0.35f) + waveStoneSpacing * 0.55f;
		while (num3 <= _event.EndRadius + 0.05f && _pieceCount < _pieces.Length)
		{
			int num4 = Mathf.Max(1, Mathf.RoundToInt(num3 * num / (waveStoneSpacing * 0.95f)));
			float num5 = Noise(num2 + 2100);
			for (int i = 0; i < num4; i++)
			{
				if (_pieceCount >= _pieces.Length)
				{
					break;
				}
				int num6 = num2 * 97 + i * 13 + 2200;
				float num7 = ((float)i + (flag ? num5 : 0.5f) + (Noise(num6) - 0.5f) * 0.55f) / (float)num4;
				num7 = (flag ? Mathf.Repeat(num7, 1f) : Mathf.Clamp(num7, 0.04f, 0.96f));
				float num8 = Mathf.Min(_event.EndRadius, num3 + (Noise(num6 + 1) - 0.5f) * waveStoneSpacing * 0.55f);
				float length = waveStoneSpacing * (0.8f + Noise(num6 + 7) * 0.5f);
				float lean = 0.25f + Noise(num6 + 5) * 0.45f;
				if (!secondary || !(Noise(num6 + 9) < 0.35f))
				{
					Vector3 center = Point(num7, num8);
					Vector3 vector = ((center.sqrMagnitude > 0.0001f) ? center.normalized : Vector3.forward);
					float y = (Noise(num6 + 2) - 0.5f) * 40f;
					float width = waveStoneSpacing * (0.34f + Noise(num6 + 6) * 0.22f);
					Vector3 direction = Quaternion.Euler(0f, y, 0f) * vector;
					float num9 = Mathf.Lerp(1.2f, 0.5f, Mathf.Clamp01(num8 / Mathf.Max(0.01f, _event.EndRadius)));
					_pieces[_pieceCount++] = new GroundPiece
					{
						Center = center,
						Direction = direction,
						Arrival = ((_event.Kind == CombatSkillVisualKind.Burst) ? (Noise(num6 + 3) * 0.03f) : (Mathf.Max(0f, num8 - _event.StartRadius) / Mathf.Max(0.01f, _event.Speed))),
						Height = _profile.DebrisHeight * (0.5f + Noise(num6 + 4) * 0.9f) * num9 * (secondary ? _profile.AftershockHeight : 1f),
						Lean = lean,
						Width = width,
						Length = length,
						Face = Color.Lerp(_profile.EdgeColor, _profile.CoreColor, 0.2f + Noise(num6 + 8) * 0.8f)
					};
				}
			}
			num3 += waveStoneSpacing * (0.78f + Noise(num2 + 2150) * 0.4f);
			num2++;
		}
	}

	private void EarthWave(float age, float fade)
	{
		float waveRiseTime = _profile.WaveRiseTime;
		float waveSettleTime = _profile.WaveSettleTime;
		for (int i = 0; i < _pieceCount; i++)
		{
			ref GroundPiece reference = ref _pieces[i];
			float num = age - reference.Arrival;
			if (!(num < 0f) && !(num > waveRiseTime + waveSettleTime))
			{
				float num2 = ((num < waveRiseTime) ? (Mathf.Sin(num / waveRiseTime * MathF.PI * 0.5f) * 1.15f) : Mathf.Lerp(1.15f, 0f, Mathf.SmoothStep(0f, 1f, (num - waveRiseTime) / waveSettleTime)));
				float num3 = reference.Height * num2;
				float alpha = fade * Mathf.Clamp01(num2 * 5f);
				float num4 = 0.55f + 0.45f * Mathf.Clamp01(num2);
				Vector3 vector = Vector3.Cross(Vector3.up, reference.Direction) * (reference.Width * 0.5f * num4);
				Vector3 vector2 = reference.Direction * (reference.Length * 0.5f * num4);
				Vector3 vector3 = reference.Center - vector2 * 0.8f;
				Vector3 vector4 = reference.Center + vector2;
				Vector3 vector5 = reference.Center - vector - vector2 * 0.15f;
				Vector3 vector6 = reference.Center + vector - vector2 * 0.15f;
				Vector3 vector7 = reference.Center + reference.Direction * (reference.Length * reference.Lean) + Vector3.up * num3;
				Vector3 vector8 = Vector3.Lerp(vector3, vector7, 0.55f) + Vector3.up * num3 * 0.08f;
				Color color = Shade(reference.Face, alpha);
				Color cc = Shade(Color.Lerp(reference.Face, _profile.CoreColor, 0.6f), alpha);
				Color color2 = Shade(_profile.ShadowColor, alpha);
				Triangle(vector5, vector4, vector7, color2, color2, cc, Vector2.zero, Vector2.right, Vector2.up);
				Triangle(vector4, vector6, vector7, color2, color2, cc, Vector2.zero, Vector2.right, Vector2.up);
				Triangle(vector6, vector3, vector8, color2, color2, color, Vector2.zero, Vector2.right, Vector2.up);
				Triangle(vector3, vector5, vector8, color2, color2, color, Vector2.zero, Vector2.right, Vector2.up);
				Triangle(vector6, vector8, vector7, color2, color, cc, Vector2.zero, Vector2.right, Vector2.up);
				Triangle(vector8, vector5, vector7, color, color2, cc, Vector2.zero, Vector2.right, Vector2.up);
			}
		}
	}

	private void EmitEarth(float age)
	{
		EmitEarthParticles(age, chips: false);
		EmitEarthParticles(age, chips: true);
	}

	private void EmitEarthParticles(float age, bool chips)
	{
		int num = (chips ? _chipsTotal : _dustTotal);
		ref int reference = ref chips ? ref _chipsPending : ref _dustPending;
		while (reference > 0)
		{
			int num2 = num - reference;
			float num3 = Mathf.Lerp(_event.StartRadius, _event.EndRadius, ((float)num2 + 0.5f) / (float)num);
			float num4 = (num3 - _event.StartRadius) / Mathf.Max(0.01f, _event.Speed);
			if (age < num4)
			{
				break;
			}
			reference--;
			float across = Mathf.Repeat((float)num2 * 0.618034f + 0.13f, 1f);
			if (!(num3 > Limit(across)) && !(age - num4 > 0.15f))
			{
				Vector3 vector = Point(across, num3);
				Vector3 normalized = Point(across, 1f).normalized;
				ParticleSystem.EmitParams emitParams = new ParticleSystem.EmitParams
				{
					position = base.transform.TransformPoint(vector + Vector3.up * 0.07f),
					velocity = base.transform.TransformDirection(normalized) * (chips ? 1.1f : (1.4f + Noise(num2 + 925) * 1.6f)) + Vector3.up * (chips ? (2.4f + Noise(num2 + 930) * 2.2f) : (0.3f + Noise(num2 + 935) * 0.5f)),
					randomSeed = (uint)(1 + num2 + CastSeed())
				};
				if (chips)
				{
					emitParams.startSize = 0.09f + Noise(num2 + 940) * 0.14f;
					emitParams.startColor = _profile.EdgeColor;
					Rubble.Emit(emitParams, 1);
				}
				else
				{
					emitParams.startSize3D = new Vector3(1f, 0.42f, 1f) * (_profile.DustSize * (0.65f + Noise(num2 + 950) * 0.35f));
					Sparks.Emit(emitParams, 1);
				}
			}
		}
	}

	private float Limit(float across)
	{
		int num = Mathf.Clamp(Mathf.FloorToInt(across * (float)Segments), 0, Segments - 1);
		return Mathf.Min(_limits[num], _limits[num + 1]);
	}

	private void Plate(Vector3 center, float width, float height, int seed, float fade, float rotation)
	{
		Vector3 b = center + new Vector3((Noise(seed + 17) - 0.5f) * width * 0.3f, height, (Noise(seed + 18) - 0.5f) * width * 0.3f);
		Color color = Shade(Color.Lerp(_profile.EdgeColor, _profile.CoreColor, Noise(seed + 11) * 0.55f), fade);
		Color lower = Shade(_profile.ShadowColor, fade);
		for (int i = 0; i < 5; i++)
		{
			float f = (rotation + (float)(i * 72) + (Noise(seed + i * 7) - 0.5f) * 29f) * (MathF.PI / 180f);
			float num = width * (0.7f + Noise(seed + i * 9) * 0.5f);
			_corners[i] = center + new Vector3(Mathf.Cos(f) * num, height * (0.42f + Noise(seed + i * 13) * 0.42f), Mathf.Sin(f) * num * 0.77f);
		}
		for (int j = 0; j < 5; j++)
		{
			Vector3 vector = _corners[j];
			Vector3 vector2 = _corners[(j + 1) % 5];
			Vector3 a = vector;
			Vector3 b2 = vector2;
			a.y = (b2.y = 0.005f);
			Triangle(vector, b, vector2, color, Shade(_profile.CoreColor, fade), color, Vector2.zero, Vector2.up, Vector2.one);
			Quad(a, b2, vector2, vector, lower, color, j);
		}
	}

	private void Crater(float radius, float age, float fade)
	{
		float craterRadius = _profile.CraterRadius;
		float num = ((age < 0.05f) ? (Mathf.Sin(age / 0.05f * MathF.PI * 0.5f) * 1.2f) : Mathf.Lerp(1.2f, 1f, Mathf.Clamp01((age - 0.05f) / 0.14f)));
		float num2 = Mathf.Clamp01(fade * 1.4f);
		Color ca = Shade(_profile.ShadowColor, 0.92f * fade);
		Color color = Shade(_profile.ShadowColor, 0.6f * fade);
		Color upper = Shade(_profile.ShadowColor, 0f);
		Vector3 a = new Vector3(0f, 0.011f, 0f);
		for (int i = 0; i < 22; i++)
		{
			float across = (float)i / 22f;
			float across2 = ((float)i + 1f) / 22f;
			float num3 = Mathf.Min(craterRadius * (0.72f + Noise(i % 22 + 300) * 0.3f) * Mathf.Min(1f, num), Limit(across));
			float num4 = Mathf.Min(craterRadius * (0.72f + Noise((i + 1) % 22 + 300) * 0.3f) * Mathf.Min(1f, num), Limit(across2));
			Vector3 vector = Point(across, num3) + Vector3.up * 0.011f;
			Vector3 vector2 = Point(across2, num4) + Vector3.up * 0.011f;
			Triangle(a, vector, vector2, ca, color, color, Vector2.zero, Vector2.right, Vector2.up);
			Vector3 d = Point(across, Mathf.Min(num3 * 1.45f, Limit(across))) + Vector3.up * 0.011f;
			Vector3 c = Point(across2, Mathf.Min(num4 * 1.45f, Limit(across2))) + Vector3.up * 0.011f;
			Quad(vector, vector2, c, d, color, upper, i);
		}
		int craterCracks = _profile.CraterCracks;
		Color dark = Shade(_profile.ShadowColor, 0.95f * fade);
		Color lip = Shade(Color.Lerp(_profile.CoreColor, Color.white, 0.15f), 0.55f * fade);
		for (int j = 0; j < craterCracks; j++)
		{
			float num5 = ((float)j + 0.5f + (Noise(j + 820) - 0.5f) * 0.6f) / (float)craterCracks;
			float num6 = Mathf.Min(radius, Limit(num5)) * (0.62f + Noise(j + 830) * 0.38f);
			float num7 = craterRadius * 0.45f;
			if (!(num6 <= num7))
			{
				Crack(num5, num7, num6, 0.11f, j * 17 + 840, dark, lip);
				if (Noise(j + 860) < 0.65f)
				{
					float num8 = Mathf.Lerp(num7, num6, 0.4f + Noise(j + 870) * 0.3f);
					float across3 = Mathf.Clamp01(num5 + (float)((!(Noise(j + 880) < 0.5f)) ? 1 : (-1)) * (0.02f + Noise(j + 890) * 0.025f));
					Crack(across3, num8, Mathf.Min(num6 * 0.9f, Limit(across3)), 0.06f, j * 17 + 900, dark, lip);
				}
			}
		}
		int craterSlabs = _profile.CraterSlabs;
		Color a2 = Color.Lerp(_profile.EdgeColor, _profile.CoreColor, 0.75f);
		Color color2 = Shade(_profile.ShadowColor, fade);
		for (int k = 0; k < craterSlabs; k++)
		{
			float num9 = ((float)k + Noise(k + 950) * 0.6f) / (float)craterSlabs;
			float num10 = craterRadius * (0.62f + Noise(k + 955) * 0.28f);
			float num11 = 0.32f + Noise(k + 960) * 0.26f;
			if (!(num10 + num11 > Limit(num9)))
			{
				float num12 = (0.17f + Noise(k + 965) * 0.13f) / Mathf.Max(0.5f, num10) / Mathf.Max(0.01f, _event.Pulse.Angle * (MathF.PI / 180f));
				float num13 = _profile.CraterSlabHeight * (0.55f + Noise(k + 970) * 0.7f) * num * num2;
				float num14 = (Noise(k + 975) - 0.5f) * 0.5f;
				Vector3 vector3 = Point(num9 - num12, num10);
				Vector3 vector4 = Point(num9 + num12, num10);
				Vector3 vector5 = Point(num9 - num12 * (1f + num14), num10 + num11);
				Vector3 vector6 = Point(num9 + num12 * (1f - num14), num10 + num11);
				Vector3 vector7 = vector3 + Vector3.up * num13 * (0.85f + Noise(k + 980) * 0.3f);
				Vector3 vector8 = vector4 + Vector3.up * num13 * (0.85f + Noise(k + 985) * 0.3f);
				vector5.y = (vector6.y = 0.02f);
				Color color3 = Shade(Color.Lerp(a2, _profile.EdgeColor, Noise(k + 990) * 0.4f), fade);
				Quad(vector5, vector6, vector8, vector7, color3, Shade(_profile.CoreColor, fade), k);
				Quad(vector3, vector4, vector8, vector7, color2, Shade(_profile.EdgeColor, fade), k);
				Triangle(vector3, vector7, vector5, color2, color3, color3, Vector2.zero, Vector2.up, Vector2.right);
				Triangle(vector4, vector8, vector6, color2, color3, color3, Vector2.zero, Vector2.up, Vector2.right);
			}
		}
		for (int l = 0; l < 7; l++)
		{
			float across4 = Noise(l + 1010);
			float num15 = craterRadius * (0.2f + Noise(l + 1020) * 0.9f);
			if (!(num15 > Limit(across4)))
			{
				Plate(Point(across4, num15), _profile.RockWidth * (0.35f + Noise(l + 1030) * 0.4f), _profile.DebrisHeight * 0.28f * num * num2, l + 1040, fade, Noise(l + 1050) * 360f);
			}
		}
	}

	private void Crack(float across, float from, float to, float width, int seed, Color dark, Color lip)
	{
		Vector3 vector = Point(across, from);
		vector.y = 0.014f;
		float num = 0f;
		for (int i = 1; i <= 6; i++)
		{
			float num2 = Mathf.Lerp(from, to, (float)i / 6f);
			num += (Noise(seed + i) - 0.5f) * 0.18f;
			Vector3 vector2 = Point(Mathf.Clamp01(across + num / Mathf.Max(0.5f, num2) / Mathf.Max(0.01f, _event.Pulse.Angle * (MathF.PI / 180f))), num2);
			vector2.y = 0.014f;
			Vector3 vector3 = vector2 - vector;
			if (!(vector3.sqrMagnitude < 0.0001f))
			{
				float num3 = width * (1f - ((float)i - 1f) / 6f * 0.8f);
				float num4 = width * (1f - (float)i / 6f * 0.8f);
				Vector3 vector4 = Vector3.Cross(vector3.normalized, Vector3.up);
				Quad(vector - vector4 * num3, vector + vector4 * num3, vector2 + vector4 * num4, vector2 - vector4 * num4, dark, dark, i);
				Quad(vector + vector4 * num3, vector + vector4 * num3 * 1.9f, vector2 + vector4 * num4 * 1.9f, vector2 + vector4 * num4, lip, Shade(lip, 0f), i);
				vector = vector2;
			}
		}
	}

	private void Fracture(float radius, float age, float fade)
	{
		bool flag = _event.Kind == CombatSkillVisualKind.BrokenGround;
		int num = (flag ? (_profile.RockCount / 2) : _profile.RockCount);
		for (int i = 0; i < num; i++)
		{
			float across = Mathf.Repeat((float)i * 0.618034f + Noise(i + 200) * 0.09f, 1f);
			float num2 = _event.EndRadius * Mathf.Sqrt(((float)i + 0.5f) / (float)num) * (0.85f + Noise(i + 210) * 0.15f);
			if (!(num2 > radius) && !(num2 > Limit(across)))
			{
				Vector3 center = Point(across, num2);
				float num3 = Mathf.Max(0f, num2 - _event.StartRadius) / Mathf.Max(0.01f, _event.Speed);
				float num4 = age - num3;
				float num5 = (flag ? 0.13f : (Mathf.Clamp01(num4 / 0.055f) * 0.12f));
				float width = _profile.RockWidth * (0.55f + Noise(i + 220) * 0.8f);
				float height = _profile.DebrisHeight * (0.5f + Noise(i + 230) * 0.9f) * num5;
				Plate(center, width, height, i + 200, fade, Noise(i + 240) * 360f);
			}
		}
		for (int j = 0; j < 9; j++)
		{
			float num6 = ((float)j + 0.2f + Noise(j + 800) * 0.5f) / 9f;
			float num7 = Mathf.Min(radius, Limit(num6)) * (0.75f + Noise(j + 810) * 0.25f);
			Vector3 vector = Point(num6, 0.16f);
			vector.y = 0.012f;
			for (int k = 1; k <= 4; k++)
			{
				Vector3 vector2 = Point(Mathf.Clamp01(num6 + (Noise(j * 9 + k + 820) - 0.5f) * 0.07f), num7 * (float)k / 4f);
				vector2.y = 0.012f;
				Vector3 vector3 = Vector3.Cross((vector2 - vector).normalized, Vector3.up) * (0.025f * (1f - (float)k * 0.14f));
				Quad(vector - vector3, vector + vector3, vector2 + vector3, vector2 - vector3, Shade(_profile.ShadowColor, fade), Shade(_profile.ShadowColor, fade), k);
				vector = vector2;
			}
		}
	}

	private void Ground(float radius, float age, float fade)
	{
		for (int i = 0; i < Segments; i++)
		{
			float num = Mathf.Min(radius, Mathf.Min(_limits[i], _limits[i + 1]));
			for (int j = 0; j < 3; j++)
			{
				float across = ((float)i + 0.06f) / (float)Segments;
				float across2 = ((float)i + 0.9f) / (float)Segments;
				float distance = num * ((float)j + 0.12f + Noise(i + j * 19) * 0.12f) / 3f;
				float distance2 = num * ((float)j + 0.82f + Noise(i + j * 23) * 0.14f) / 3f;
				Vector3 a = Point(across, distance);
				Vector3 b = Point(across2, distance);
				Vector3 vector = Point(across2, distance2);
				Vector3 vector2 = Point(across, distance2);
				bool flag = _event.Kind == CombatSkillVisualKind.Uplift;
				if (!flag || !(Noise(i + j * 13) < 0.35f))
				{
					float num2 = (Fire ? 0.008f : (_profile.DebrisHeight * (flag ? (0.45f + Noise(i + j * 13) * 0.55f) : 0.18f) * fade));
					if (flag)
					{
						num2 *= Mathf.Clamp01(age / 0.06f) * Mathf.Clamp01((_event.Duration - age) / 0.28f);
					}
					vector.y = (vector2.y = num2);
					float num3 = (Fire ? Mathf.Pow(Mathf.Clamp01(1f - age / Mathf.Max(0.01f, _event.Duration)), 0.7f) : 0.25f);
					Color color = Color.Lerp(_profile.ShadowColor, _profile.EdgeColor, num3 * (Fire ? 0.14f : 0.6f));
					Quad(a, b, vector, vector2, Shade(color, fade * (Fire ? 0.3f : 0.9f)), Shade(flag ? _profile.EdgeColor : color, fade * (Fire ? 0.3f : 0.9f)), (float)i + (float)j * 0.31f);
					if (flag)
					{
						Vector3 c = vector;
						Vector3 d = vector2;
						c.y = (d.y = 0f);
						Quad(vector2, vector, c, d, Shade(_profile.CoreColor, fade * 0.9f), Shade(_profile.ShadowColor, fade), i);
					}
				}
			}
		}
	}

	private void Shadow(float fade)
	{
		for (int i = 0; i < 24; i++)
		{
			float f = (float)i * MathF.PI * 2f / 24f;
			float f2 = (float)(i + 1) * MathF.PI * 2f / 24f;
			Triangle(Vector3.zero, new Vector3(Mathf.Sin(f) * 0.5f, 0f, Mathf.Cos(f) * 0.4f), new Vector3(Mathf.Sin(f2) * 0.5f, 0f, Mathf.Cos(f2) * 0.4f), new Color(0f, 0f, 0f, 0.4f * fade), Color.clear, Color.clear, Vector2.zero, Vector2.right, Vector2.up);
		}
	}

	private void Blood(float radius, float fade)
	{
		for (int i = 0; i < Segments; i++)
		{
			Vector3 vector = Point((float)i / (float)Segments, radius);
			Vector3 vector2 = Point(((float)i + 1f) / (float)Segments, radius);
			Quad(vector, vector2, vector2 + Vector3.up * 0.22f, vector + Vector3.up * 0.22f, Shade(_profile.BloodAccent, fade), Shade(_profile.BloodAccent, 0f), i);
		}
	}

	private void Seal(float fade)
	{
		for (int i = 0; i < 4; i++)
		{
			Quaternion quaternion = Quaternion.Euler(0f, 45 + i * 90, 0f);
			Quad(quaternion * new Vector3(-0.08f, 0f, 0.28f), quaternion * new Vector3(0.08f, 0f, 0.28f), quaternion * new Vector3(0.05f, 0.11f, 0.38f), quaternion * new Vector3(-0.05f, 0.11f, 0.38f), Shade(_profile.ShadowColor, fade), Shade(_profile.CoreColor, fade * 0.8f), i);
		}
	}

	private void OnDestroy()
	{
		if (_mesh != null)
		{
			UnityEngine.Object.Destroy(_mesh);
		}
		if (_shockMesh != null)
		{
			UnityEngine.Object.Destroy(_shockMesh);
		}
	}
}
