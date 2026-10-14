using UnityEngine;

public class EnemyProjectileVisual : MonoBehaviour
{
	[Tooltip("Humanoid bone the shot leaves from. LastBone keeps a fixed chest-height origin above the caster.")]
	[SerializeField]
	private HumanBodyBones launchBone = HumanBodyBones.LastBone;

	private TrailRenderer[] _trails;

	public HumanBodyBones LaunchBone => launchBone;

	public virtual bool Charges => false;

	public virtual bool Busy => base.gameObject.activeSelf;

	public virtual void Charge(Vector3 position, float casterScale, float progress)
	{
	}

	public virtual void Launch(Vector3 position, float casterScale)
	{
		base.transform.position = position;
		if (_trails == null)
		{
			_trails = GetComponentsInChildren<TrailRenderer>(includeInactive: true);
		}
		base.gameObject.SetActive(value: true);
		TrailRenderer[] trails = _trails;
		for (int i = 0; i < trails.Length; i++)
		{
			trails[i].Clear();
		}
	}

	public virtual void Move(Vector3 position, Vector3 direction)
	{
		base.transform.position = position;
		if (direction.sqrMagnitude > 0.0001f)
		{
			base.transform.rotation = Quaternion.LookRotation(direction);
		}
	}

	public virtual void Impact()
	{
		Release();
	}

	public virtual void Dissipate()
	{
		Release();
	}

	public virtual void Release()
	{
		base.gameObject.SetActive(value: false);
		if (_trails != null)
		{
			TrailRenderer[] trails = _trails;
			for (int i = 0; i < trails.Length; i++)
			{
				trails[i].Clear();
			}
		}
	}
}
