export const SHIELD_RULES=Object.freeze({sourceFps:50,frameTicks:5,warningFrames:250,flashTicks:12});
// The native +63f784 counter decrements once per five engine ticks while
// holding. Store actual 50Hz ticks in the existing *Frames field so status UI
// and saved web fields retain their time unit (61dc9f..61dcbb, 5c2b4e).
export function startMagicShield(combat,nativeCount){
 combat.player.magicShieldFrames=Math.max(0,nativeCount*SHIELD_RULES.frameTicks);
 combat.magicShieldState={phase:1,frame:1};
 const shell=combat.effects?.find(e=>e.shield);if(shell)shell.shieldFrame=1;
}
export function hitMagicShield(combat){
 if(combat.player.magicShieldFrames>0){combat.magicShieldState={phase:3,frame:13};const shell=combat.effects?.find(e=>e.shield);if(shell)shell.shieldFrame=13;}
}
export function advanceMagicShield(combat){
 const p=combat.player;if(!(p.magicShieldFrames>0)||p.hp<=0){combat.magicShieldState=null;return;}
 const s=combat.magicShieldState||={phase:2,frame:11};
 if(combat.ruleFrame%SHIELD_RULES.frameTicks)return;
 s.frame++;
 if(s.phase===1){if(s.frame===10)s.phase=2;}
 else if(s.phase===2){if(s.frame===14)s.frame=11;p.magicShieldFrames=Math.max(0,p.magicShieldFrames-SHIELD_RULES.frameTicks);}
 else if(s.phase===3&&s.frame>=17){s.phase=2;s.frame=11;}
}
// Native 5c2c9f: below 50 counter units, draw only phases 1..7 out of 12.
export function magicShieldVisible(combat){
 if(!(combat.player.magicShieldFrames>0)||combat.player.hp<=0)return false;
 if(combat.player.magicShieldFrames>=SHIELD_RULES.warningFrames)return true;
 const phase=(combat.ruleFrame||0)%SHIELD_RULES.flashTicks;return phase>0&&phase<8;
}
