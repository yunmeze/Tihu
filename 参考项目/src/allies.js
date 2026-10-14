// Native owner 0x34 identifies allies; 0x36 identifies the three following pets.
export const followingPet=u=>!!u.summoned&&!u.mercenary&&!u.defenseFlag;
export const friendlyCount=combat=>[...(combat.units||[]),...(combat.waitingPets||[])].filter(u=>u.alive&&u.summoned&&!u.defenseFlag).length;
