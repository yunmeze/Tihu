using Scellecs.Morpeh;

public struct CombatSkillVisualEvent
{
	public CombatSkillPulse Pulse;

	public CombatSkillVisualKind Kind;

	public double StartsAt;

	public float Duration;

	public float StartRadius;

	public float EndRadius;

	public float Speed;

	public CombatSkillTimeline Timeline;

	public int Generation;

	public Entity FollowTarget;
}
