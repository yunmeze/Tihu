import {emitNativeParticle} from './native-particles.js';

// The native scene-name branches 5b58cb/5b5dbf use Data8, not a generic
// weather guess. Coordinates remain in map space while the camera moves.
export const AMBIENT_PARTICLES={'天界-天路':{type:9,period:2},'天界-三明界':{type:20,period:3},'天界-轮回':{type:20,period:3}};
export function ambientParticlePack(c){return AMBIENT_PARTICLES[c?.map?.name]?'Data8':null;}
export function emitAmbientParticles(c){
 const rule=AMBIENT_PARTICLES[c.map?.name];if(!rule||c.ruleFrame%rule.period||(c.particles?.length||0)>=1024)return;
 const rnd=c.visualRandom||Math.random,view=c.particleView||c.position;
 emitNativeParticle(c,rule.type,{x:view.x+(rnd()*2800-1000)/48,y:view.y+(rnd()*1700-600)/32});
}
