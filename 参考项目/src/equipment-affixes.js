import {nativeRound,sampleMonsterRandom} from './monster-motion.js';

// Native random equipment: 5fcc20 → 5fd5e0, helpers 5fd7f0..5fe645.
export function rollEquipmentAffixes(item,player={},random=Math.random){
 if(item.type<7||item.type>14)return {};
 const raw=[...item.rawFields],draw=()=>sampleMonsterRandom(random),hit=(denominator,value=1,inclusive=false)=>inclusive?draw()*denominator<=value:draw()*denominator<value;
 let tint;
 const inc=(index,price=1)=>{raw[index]++;raw[37]+=price;};
 const special=(index,denominator,price=2,inclusive=false)=>{const rolled=hit(denominator,1,inclusive);if(rolled&&raw[index]<2)inc(index,price);};
 const defense=()=>{for(const i of [12,13,14,15])if(hit(10,i%2?4:2))inc(i);};
 const offense=()=>{const index=[6,8,10][nativeRound(draw()*2)];if(hit(10,2))inc(index);if(hit(10,4))inc(index+1);};
 function attempt(full){
  if(full){const lighter=hit(10,3);if(lighter&&raw[38]>1){raw[38]--;raw[37]++;}}
  switch(item.type){
   case 7:defense();special(21,35);special(22,25);break;
   case 8:offense();if(full){special(20,15);special(23,25);}break;
   case 9:offense();defense();if(full){special(25,40);special(27,40,2,true);special(26,40);}break;
   case 10:defense();if(full){special(19,15);special(18,15);}break;
   case 11:defense();if(full){special(21,35);special(22,25);}break;
   case 12:offense();if(full){special(23,25);special(25,40);special(27,40,2,true);special(24,65,3);}break;
   case 13:defense();special(26,40);break;
   case 14:offense();special(23,25);if(full){special(16,65,3);special(17,65,3);special(20,15);special(25,40);special(27,40,2,true);if(hit(10)){tint=[0,1,2].map(()=>nativeRound(draw()*230));}}break;
  }
 }
 const fullAttempts=3+Math.min(2,Math.max(0,player.clearCount||0))+(player.gameMode===1?4:player.gameMode===2?8:0);
 for(let i=0;i<fullAttempts;i++)if(hit(10,2))attempt(true);
 // 1fd8 is the claimed collection reward stage; 100% grants one extra roll.
 if((player.collectionRewardStage||0)>=10&&hit(10,3))attempt(true);
 for(const level of [20,30,40,50,50,60,60,70,80]){const rolled=hit(10,2);if(rolled&&raw[31]>=level)attempt(false);}
 const fieldOverrides={};for(let i=0;i<39;i++)if(raw[i]!==item.rawFields[i])fieldOverrides[i]=raw[i];
 return {...(Object.keys(fieldOverrides).length?{fieldOverrides,priceBonus:raw[37]}:{}),...(tint?{tint}:{}),affixModel:'lp-122e-affixes-v1'};
}
