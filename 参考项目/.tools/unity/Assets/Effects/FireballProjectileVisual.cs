using System;
using UnityEngine;

[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public sealed class FireballProjectileVisual : EnemyProjectileVisual
{
	private enum Phase
	{
		Idle,
		Charging,
		Flying,
		Bursting
	}

	private enum Kind : byte
	{
		Ball,
		Tail,
		Glow,
		Spark,
		Smoke
	}

	private struct Particle
	{
		public Vector3 Position;

		public Vector3 Velocity;

		public float Age;

		public float Life;

		public float StartSize;

		public float EndSize;

		public float Seed;

		public float Heat;

		public float Drag;

		public Kind Kind;
	}

	private const int MaxParticles = 160;

	private const int MaxQuads = 164;

	private const float Gravity = 6f;

	[Header("Size (caster view scale 1)")]
	[SerializeField]
	[Min(0.01f)]
	private float radius = 0.23f;

	[SerializeField]
	[Min(0f)]
	[Tooltip("Tail length in core radii.")]
	private float tailLength = 6f;

	[SerializeField]
	[Range(0f, 1f)]
	[Tooltip("Core size while gathering in the hand, relative to flight.")]
	private float chargedSize = 0.7f;

	[SerializeField]
	[Range(0f, 1f)]
	[Tooltip("Share of the windup before fire appears in the hand.")]
	private float chargeStart = 0.3f;

	[Header("Emission per second")]
	[SerializeField]
	[Min(0f)]
	private float flightSparks = 55f;

	[SerializeField]
	[Min(0f)]
	private float flightSmoke = 26f;

	[SerializeField]
	[Min(0f)]
	private float chargeSparks = 34f;

	[Header("Burst")]
	[SerializeField]
	[Min(1f)]
	private int burstFireballs = 7;

	[SerializeField]
	[Min(0f)]
	private int burstSparks = 26;

	[SerializeField]
	[Min(0f)]
	private int burstSmoke = 6;

	[Header("Light")]
	[SerializeField]
	private Light glowLight;

	[SerializeField]
	private Color lightColor = new Color(1f, 0.47f, 0.16f);

	[SerializeField]
	[Min(0f)]
	private float lightIntensity = 2.4f;

	[SerializeField]
	[Min(0f)]
	[Tooltip("Light range in core radii.")]
	private float lightRange = 15f;

	[SerializeField]
	private Color glowColor = new Color(1f, 0.42f, 0.1f, 0.26f);

	private readonly Particle[] _particles = new Particle[160];

	private int _particleCount;

	private Phase _phase;

	private Vector3 _position;

	private Vector3 _direction;

	private Vector3 _flightStart;

	private float _scale = 1f;

	private float _charge;

	private float _grow;

	private float _phaseTime;

	private float _sparkDebt;

	private float _smokeDebt;

	private float _flash;

	private bool _launchBurstPending;

	private uint _random = 2654435769u;

	private float _lightSeed;

	private Mesh _mesh;

	private Vector3[] _vertices;

	private Vector3[] _normals;

	private Vector4[] _tangents;

	private Vector4[] _uv0;

	private Vector4[] _uv1;

	private Color[] _colors;

	private int[] _indices;

	private int _quads;

	private Bounds _bounds;

	public override bool Charges => true;

	public int ParticleCount => _particleCount;

	private float Radius => radius * _scale;

	private void Awake()
	{
		EnsureMesh();
		_random ^= (uint)(GetInstanceID() * -1640531535);
		_lightSeed = Range(0f, 100f);
	}

	public override void Charge(Vector3 position, float casterScale, float progress)
	{
		if (_phase != Phase.Charging)
		{
			Begin(Phase.Charging, position, casterScale);
		}
		_position = position;
		_charge = progress;
	}

	public override void Launch(Vector3 position, float casterScale)
	{
		if (_phase != Phase.Charging)
		{
			Begin(Phase.Flying, position, casterScale);
		}
		_phase = Phase.Flying;
		_phaseTime = 0f;
		_position = (_flightStart = position);
		_launchBurstPending = true;
		_flash = 0.6f;
	}

	public override void Move(Vector3 position, Vector3 direction)
	{
		_position = position;
		if (direction.sqrMagnitude > 1E-06f)
		{
			_direction = direction.normalized;
		}
	}

	public override void Impact()
	{
		if (_phase != Phase.Flying)
		{
			Release();
			return;
		}
		_position -= _direction * Radius * 0.9f;
		Burst(impact: true);
	}

	public override void Dissipate()
	{
		if (_phase != Phase.Idle && _phase != Phase.Bursting)
		{
			if (_phase == Phase.Charging && _charge < chargeStart)
			{
				Release();
			}
			else
			{
				Burst(impact: false);
			}
		}
	}

	public override void Release()
	{
		_phase = Phase.Idle;
		_particleCount = 0;
		if (glowLight != null)
		{
			glowLight.enabled = false;
		}
		base.gameObject.SetActive(value: false);
	}

	private void Begin(Phase phase, Vector3 position, float casterScale)
	{
		_phase = phase;
		_scale = Mathf.Max(0.1f, casterScale);
		_position = (_flightStart = position);
		_direction = Vector3.zero;
		_particleCount = 0;
		_charge = (_grow = (_phaseTime = (_sparkDebt = (_smokeDebt = (_flash = 0f)))));
		_launchBurstPending = false;
		base.transform.SetPositionAndRotation(position, Quaternion.identity);
		base.transform.localScale = Vector3.one;
		base.gameObject.SetActive(value: true);
	}

	private void Burst(bool impact)
	{
		_phase = Phase.Bursting;
		_phaseTime = 0f;
		float num = Radius * (impact ? 1f : Mathf.Lerp(0.4f, 1f, _grow));
		int num2 = (impact ? burstFireballs : Mathf.Max(1, burstFireballs / 3));
		for (int i = 0; i < num2; i++)
		{
			Vector3 vector = OnSphere();
			Emit(Kind.Ball, _position + vector * num * Range(0.3f, 0.7f), vector * num * Range(3f, 6f), Range(0.28f, 0.5f), num * Range(0.8f, 1.15f), num * Range(1.7f, 2.5f), 1f, 3.5f);
		}
		int num3 = (impact ? burstSparks : (burstSparks / 4));
		for (int j = 0; j < num3; j++)
		{
			Vector3 vector2 = OnSphere();
			if (vector2.y < 0f)
			{
				vector2.y *= -0.4f;
			}
			Emit(Kind.Spark, _position + vector2 * num * Range(0.3f, 0.8f), vector2 * Range(1.2f, 5f) * Mathf.Sqrt(_scale), Range(0.2f, 0.55f), num * 0.05f, num * 0.03f, Range(0.7f, 1f), 1.5f);
		}
		int num4 = (impact ? burstSmoke : 2);
		for (int k = 0; k < num4; k++)
		{
			Emit(Kind.Smoke, _position + OnSphere() * num * 0.6f, (Vector3.up * Range(0.5f, 1f) + OnSphere() * 0.5f) * num * 2.4f, Range(0.8f, 1.15f), num * 1.2f, num * Range(2.8f, 3.8f), 0.9f, 1.6f);
		}
		if (impact)
		{
			_flash = 1f;
		}
	}

	private void LateUpdate()
	{
		float deltaTime = Time.deltaTime;
		if (_phase != Phase.Idle && !(deltaTime <= 0f))
		{
			_phaseTime += deltaTime;
			_flash = Mathf.Max(0f, _flash - deltaTime * 7f);
			switch (_phase)
			{
			case Phase.Charging:
				EmitCharge(deltaTime);
				break;
			case Phase.Flying:
				EmitFlight(deltaTime);
				break;
			}
			Simulate(deltaTime);
			UpdateLight();
			Build();
			if (_phase == Phase.Bursting && _particleCount == 0 && _flash <= 0f)
			{
				Release();
			}
		}
	}

	private void EmitCharge(float dt)
	{
		float num = Mathf.InverseLerp(chargeStart, 1f, _charge);
		_grow = chargedSize * num * num * (3f - 2f * num);
		if (!(num <= 0f))
		{
			float num2 = Radius;
			_sparkDebt += chargeSparks * dt * (0.4f + _grow);
			while (_sparkDebt >= 1f)
			{
				Vector3 vector = OnSphere();
				Vector3 vector2 = _position + vector * num2 * Range(2.5f, 4f);
				float num3 = Range(0.16f, 0.26f);
				Emit(Kind.Spark, vector2, (_position - vector2) / num3, num3, num2 * 0.05f, num2 * 0.03f, 0.9f, 0f);
				_sparkDebt -= 1f;
			}
			_smokeDebt += 5f * dt * _grow;
			while (_smokeDebt >= 1f)
			{
				Emit(Kind.Smoke, _position + OnSphere() * num2 * 0.4f, Vector3.up * num2 * 3f, Range(0.45f, 0.65f), num2 * 0.5f * _grow, num2 * 1.4f * _grow, 0.7f, 1f);
				_smokeDebt -= 1f;
			}
		}
	}

	private void EmitFlight(float dt)
	{
		_grow = Mathf.MoveTowards(_grow, 1f, dt / 0.08f);
		float num = Radius * _grow;
		if (_launchBurstPending && _direction.sqrMagnitude > 0f)
		{
			_launchBurstPending = false;
			for (int i = 0; i < 12; i++)
			{
				Vector3 normalized = (_direction * 1.3f + OnSphere()).normalized;
				Emit(Kind.Spark, _position + normalized * num * 0.3f, normalized * Range(3f, 6f) * Mathf.Sqrt(_scale), Range(0.15f, 0.3f), num * 0.07f, num * 0.04f, 1f, 2f);
			}
			Emit(Kind.Smoke, _position - _direction * num * 0.3f, Vector3.up * num, 0.5f, num * 0.8f, num * 2f, 1f, 2f);
		}
		_sparkDebt += flightSparks * dt;
		while (_sparkDebt >= 1f)
		{
			Vector3 vector = OnSphere();
			Vector3 velocity = (vector * Range(0.8f, 2.2f) - _direction * Range(0.5f, 1.8f) + Vector3.up * 0.6f) * Mathf.Sqrt(_scale);
			Emit(Kind.Spark, _position + vector * num * 0.7f, velocity, Range(0.22f, 0.5f), num * 0.06f, num * 0.03f, Range(0.75f, 1f), 1.5f);
			_sparkDebt -= 1f;
		}
		_smokeDebt += flightSmoke * dt;
		while (_smokeDebt >= 1f)
		{
			Vector3 vector2 = OnSphere() * num * 0.35f - _direction * num * Range(0.6f, 1.6f);
			Emit(Kind.Smoke, _position + vector2, (Vector3.up * 0.5f + OnSphere() * 0.25f) * num * 1.8f, Range(0.4f, 0.6f), num * 0.55f, num * Range(1.6f, 2.2f), 0.8f, 2.5f);
			_smokeDebt -= 1f;
		}
	}

	private void Emit(Kind kind, Vector3 position, Vector3 velocity, float life, float startSize, float endSize, float heat, float drag)
	{
		if (_particleCount < 160)
		{
			_particles[_particleCount++] = new Particle
			{
				Kind = kind,
				Position = position,
				Velocity = velocity,
				Life = Mathf.Max(0.01f, life),
				StartSize = startSize,
				EndSize = endSize,
				Heat = heat,
				Drag = drag,
				Seed = Range(0f, 64f)
			};
		}
	}

	private void Simulate(float dt)
	{
		for (int i = 0; i < _particleCount; i++)
		{
			ref Particle reference = ref _particles[i];
			reference.Age += dt;
			if (reference.Age >= reference.Life)
			{
				_particles[i--] = _particles[--_particleCount];
				continue;
			}
			reference.Velocity *= Mathf.Max(0f, 1f - reference.Drag * dt);
			if (reference.Kind == Kind.Spark)
			{
				reference.Velocity.y -= 6f * dt * Mathf.Sqrt(_scale);
			}
			else if (reference.Kind == Kind.Smoke)
			{
				reference.Velocity.y += Radius * 2f * dt;
			}
			reference.Position += reference.Velocity * dt;
		}
	}

	private void UpdateLight()
	{
		if (!(glowLight == null))
		{
			float num = 0.82f + 0.18f * Mathf.PerlinNoise(Time.time * 11f, _lightSeed);
			float num2 = (((_phase == Phase.Flying || _phase == Phase.Charging) ? _grow : 0f) + _flash * 1.6f) * num;
			glowLight.enabled = num2 > 0.02f;
			glowLight.color = lightColor;
			glowLight.intensity = lightIntensity * num2;
			glowLight.range = lightRange * Radius;
			glowLight.transform.position = _position;
		}
	}

	private void Build()
	{
		EnsureMesh();
		_quads = 0;
		Vector3 position = base.transform.position;
		_bounds = new Bounds(_position - position, Vector3.zero);
		float num = Radius * _grow;
		bool flag = _phase == Phase.Flying || (_phase == Phase.Charging && _grow > 0f);
		for (int i = 0; i < _particleCount; i++)
		{
			if (_particles[i].Kind == Kind.Smoke)
			{
				AddParticle(ref _particles[i], position);
			}
		}
		if (flag && _phase == Phase.Flying && _direction.sqrMagnitude > 0f)
		{
			float num2 = Mathf.Min(tailLength * Radius, Vector3.Distance(_position, _flightStart) + num);
			if (num2 > num * 0.5f)
			{
				AddQuad(_position - position, -_direction * num2, num * 1.05f, num, Kind.Tail, 1f, Color.white, num2 / (num * 1.05f), 0f, 11f);
			}
		}
		for (int j = 0; j < _particleCount; j++)
		{
			if (_particles[j].Kind == Kind.Ball)
			{
				AddParticle(ref _particles[j], position);
			}
		}
		if (flag && num > 0f)
		{
			AddQuad(_position - position, _direction, num * 1.9f, num * 1.9f, Kind.Ball, 1f, Color.white, 1f, 0f, 3f);
		}
		for (int k = 0; k < _particleCount; k++)
		{
			if (_particles[k].Kind == Kind.Spark)
			{
				AddParticle(ref _particles[k], position);
			}
		}
		float num3 = (flag ? _grow : 0f) + _flash;
		if (num3 > 0f)
		{
			Color color = glowColor;
			color.a *= Mathf.Min(1.6f, num3);
			AddQuad(_position - position, Vector3.zero, Radius * (2.6f + _flash * 2f), Radius * (2.6f + _flash * 2f), Kind.Glow, 1f, color, 1f, 0f, 0f);
		}
		_mesh.Clear(keepVertexLayout: true);
		_mesh.SetVertices(_vertices, 0, _quads * 4);
		_mesh.SetNormals(_normals, 0, _quads * 4);
		_mesh.SetTangents(_tangents, 0, _quads * 4);
		_mesh.SetUVs(0, _uv0, 0, _quads * 4);
		_mesh.SetUVs(1, _uv1, 0, _quads * 4);
		_mesh.SetColors(_colors, 0, _quads * 4);
		_mesh.SetIndices(_indices, 0, _quads * 6, MeshTopology.Triangles, 0, calculateBounds: false);
		_mesh.bounds = _bounds;
	}

	private void AddParticle(ref Particle p, Vector3 origin)
	{
		float num = p.Age / p.Life;
		float num2 = Mathf.Lerp(p.StartSize, p.EndSize, 1f - (1f - num) * (1f - num));
		switch (p.Kind)
		{
		case Kind.Spark:
			AddQuad(p.Position - origin, -p.Velocity * 0.022f, num2, num2, Kind.Spark, p.Heat * (1f - num * 0.5f), new Color(1f, 1f, 1f, 1f - num * num), 1f, 0f, p.Seed);
			break;
		case Kind.Smoke:
			AddQuad(p.Position - origin, Vector3.zero, num2, num2, Kind.Smoke, p.Heat * Mathf.Max(0f, 1f - num * 2.5f), new Color(1f, 1f, 1f, Mathf.Sin(MathF.PI * Mathf.Sqrt(num)) * 0.9f), 1f, 0f, p.Seed);
			break;
		default:
			AddQuad(p.Position - origin, (p.Velocity.sqrMagnitude > 0.0001f) ? (p.Velocity.normalized * 0.4f) : Vector3.zero, num2, num2, Kind.Ball, Mathf.Lerp(0.95f, 0.3f, num), new Color(1f, 1f, 1f, 1f - num * num * num), 1f, Mathf.Min(1f, num * 1.1f), p.Seed);
			break;
		}
	}

	private void AddQuad(Vector3 anchor, Vector3 axis, float halfWidth, float halfHeight, Kind kind, float heat, Color color, float aspect, float erosion, float seed)
	{
		if (_quads < 164)
		{
			int num = _quads * 4;
			Vector3 vector = new Vector3(halfWidth, halfHeight, seed);
			Vector4 vector2 = new Vector4(axis.x, axis.y, axis.z, 0f);
			Vector4 vector3 = new Vector4(aspect, erosion, 0f, 0f);
			for (int i = 0; i < 4; i++)
			{
				_vertices[num + i] = anchor;
				_normals[num + i] = vector;
				_tangents[num + i] = vector2;
				_uv0[num + i] = new Vector4((i == 1 || i == 2) ? 1f : 0f, (i >= 2) ? 1f : 0f, (int)kind, heat);
				_uv1[num + i] = vector3;
				_colors[num + i] = color;
			}
			_quads++;
			float num2 = Mathf.Max(halfWidth, halfHeight) + axis.magnitude;
			_bounds.Encapsulate(new Bounds(anchor, Vector3.one * num2 * 2f));
		}
	}

	private void EnsureMesh()
	{
		if (!(_mesh != null))
		{
			_mesh = new Mesh
			{
				name = "Fireball"
			};
			_mesh.MarkDynamic();
			GetComponent<MeshFilter>().sharedMesh = _mesh;
			_vertices = new Vector3[656];
			_normals = new Vector3[656];
			_tangents = new Vector4[656];
			_uv0 = new Vector4[656];
			_uv1 = new Vector4[656];
			_colors = new Color[656];
			_indices = new int[984];
			for (int i = 0; i < 164; i++)
			{
				int num = i * 4;
				_indices[i * 6] = num;
				_indices[i * 6 + 1] = num + 2;
				_indices[i * 6 + 2] = num + 1;
				_indices[i * 6 + 3] = num;
				_indices[i * 6 + 4] = num + 3;
				_indices[i * 6 + 5] = num + 2;
			}
		}
	}

	private void OnDestroy()
	{
		if (_mesh != null)
		{
			UnityEngine.Object.Destroy(_mesh);
		}
	}

	private float Range(float min, float max)
	{
		_random ^= _random << 13;
		_random ^= _random >> 17;
		_random ^= _random << 5;
		return min + (max - min) * (float)(_random & 0xFFFFFF) / 16777216f;
	}

	private Vector3 OnSphere()
	{
		float num = Range(-1f, 1f);
		float f = Range(0f, MathF.PI * 2f);
		float num2 = Mathf.Sqrt(1f - num * num);
		return new Vector3(num2 * Mathf.Cos(f), num, num2 * Mathf.Sin(f));
	}
}
