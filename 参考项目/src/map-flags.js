// LP's signed cell flags, retained in maps/*.json. 10+ identifies portals.
// Verified from the original editor's o_Flag controls and native assignment code.
// See reports/native-map-flags.json for indices, code bytes and source hashes.
// The editor separates render priority from whether an actor can enter the cell.
export const MAP_FLAG=Object.freeze({
 NORMAL:0,GROUND_BLOCKED:-2,MIDDLE_BLOCKED:-1,
 GROUND:1,FOREGROUND:2,PLAYER_BLOCKED:-3,MONSTER_BLOCKED:-4,
});
export function mapLayer(flag){
 if(flag===MAP_FLAG.GROUND||flag===MAP_FLAG.GROUND_BLOCKED)return 0;
 if(flag===MAP_FLAG.FOREGROUND)return 2;
 return 1;
}
export function canEnterCell(flag,actor='player'){
 return flag!==MAP_FLAG.GROUND_BLOCKED&&flag!==MAP_FLAG.MIDDLE_BLOCKED&&
  flag!==(actor==='monster'?MAP_FLAG.MONSTER_BLOCKED:MAP_FLAG.PLAYER_BLOCKED);
}
export function compareWorldObjects(a,b){return a.layer-b.layer||a.y-b.y;}
