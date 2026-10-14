// Platform drivers own playback resources. Gameplay only emits named events.
export function browserAudioDevice(){
 let context,unlocked=false,paused=false,disposed=false,generation=0,battleGeneration=0,bytes=0,errors=0,played=0,master=1;
 const buffers=new Map(),pending=new Map(),fetches=new Set(),sources=new Set(),loops=new Map();
 const limit=24*1024*1024;
 const fail=e=>{if(!disposed&&e?.name!=='AbortError')errors++;};
 function media(key){if(!loops.has(key)){const element=new Audio();element.loop=true;element.preload='none';const onError=()=>fail();element.addEventListener('error',onError);loops.set(key,{element,onError,active:false});}return loops.get(key);}
 function runLoop(l){if(disposed||!unlocked||paused||!l.active||l.element.volume<=0){l.element.pause();return;}const result=l.element.play();result?.catch(()=>{if(!disposed&&!paused)fail();});}
 async function buffer(url){
  if(buffers.has(url)){const b=buffers.get(url);buffers.delete(url);buffers.set(url,b);return b;}
  if(!context||disposed)return null;
  if(!pending.has(url)){const token=generation;const promise=(async()=>{const controller=new AbortController();fetches.add(controller);try{const response=await fetch(url,{signal:controller.signal});if(!response.ok)throw Error('Audio HTTP '+response.status);const data=await response.arrayBuffer();if(disposed||token!==generation)return null;const b=await context.decodeAudioData(data);if(disposed||token!==generation)return null;buffers.set(url,b);bytes+=b.length*b.numberOfChannels*4;while((bytes>limit||buffers.size>48)&&buffers.size>1){const [key,old]=buffers.entries().next().value;buffers.delete(key);bytes-=old.length*old.numberOfChannels*4;}return b;}finally{fetches.delete(controller);}})().catch(e=>{fail(e);return null;}).finally(()=>pending.delete(url));pending.set(url,promise);}return pending.get(url);
 }
 function stopEffects(battleOnly=false){if(battleOnly)battleGeneration++;else generation++;for(const voice of [...sources]){if(battleOnly&&voice.ui)continue;try{voice.source.stop();}catch{}voice.source.disconnect();voice.gain.disconnect();sources.delete(voice);}if(!battleOnly){for(const controller of fetches)controller.abort();fetches.clear();}}
 return {
  unlock(){if(disposed)return;unlocked=true;if(!context){const AudioContext=globalThis.AudioContext||globalThis.webkitAudioContext;if(AudioContext)context=new AudioContext();}context?.resume().catch(fail);for(const l of loops.values())runLoop(l);},
  loop(key,url,volume,active){if(disposed)return;const l=media(key);if(l.url!==url){l.url=url;l.element.src=url;}l.element.volume=Math.max(0,Math.min(1,volume));l.active=active;runLoop(l);},
  async play(url,volume,deadline,{ui=false}={}){if(disposed||paused||!unlocked||!context)return false;const token=generation,battleToken=battleGeneration,b=await buffer(url);if(!b||disposed||paused||token!==generation||!ui&&battleToken!==battleGeneration||Date.now()>deadline||context.state!=='running')return false;
   if(sources.size>=8){const oldest=sources.values().next().value;oldest.source.stop();oldest.source.disconnect();oldest.gain.disconnect();sources.delete(oldest);}
   const source=context.createBufferSource(),gain=context.createGain();source.buffer=b;gain.gain.value=volume;source.connect(gain);gain.connect(context.destination);const voice={source,gain,ui,relative:master>0?volume/master:0};sources.add(voice);source.onended=()=>{sources.delete(voice);source.disconnect();gain.disconnect();};source.start();played++;return true;
  },
  preload(urls){return Promise.all(urls.map(buffer));},
  stopEffects,
  pause(value){paused=value;if(value){stopEffects();context?.suspend().catch(fail);}else if(unlocked)context?.resume().catch(fail);for(const l of loops.values())runLoop(l);},
  volume(value){master=value;for(const v of sources)v.gain.gain.value=v.relative*value;},
  stats(){return {available:!!(globalThis.AudioContext||globalThis.webkitAudioContext),state:context?.state||'locked',voices:sources.size,buffers:buffers.size,decodedBytes:bytes,played,errors,loops:[...loops].map(([key,l])=>({key,active:l.active,playing:!l.element.paused,time:l.element.currentTime,volume:l.element.volume}))};},
  dispose(){if(disposed)return;disposed=true;stopEffects();for(const l of loops.values()){l.element.pause();l.element.removeEventListener('error',l.onError);l.element.removeAttribute('src');l.element.load();}loops.clear();buffers.clear();bytes=0;context?.close().catch(()=>{});}
 };
}

export function wechatAudioDevice(wx,resolve){
 let unlocked=false,paused=false,disposed=false,generation=0,battleGeneration=0,played=0,errors=0,master=1;
 const loops=new Map(),voices=[],files=new Map();
 function local(url){if(!files.has(url))files.set(url,resolve(url).catch(e=>{files.delete(url);throw e;}));return files.get(url);}
 function voice(){const audio=wx.createInnerAudioContext();audio.autoplay=false;audio.obeyMuteSwitch=true;const v={audio,busy:false,token:0,started:0};v.end=()=>{v.busy=false;v.playing=false;};v.error=()=>{v.busy=false;v.playing=false;errors++;};audio.onEnded?.(v.end);audio.onError?.(v.error);return v;}
 async function runLoop(l){const token=++l.token;if(disposed||!unlocked||paused||!l.active||l.volume<=0){l.audio.pause();l.playing=false;return;}l.audio.volume=l.volume;if(l.playing&&l.loadedUrl===l.url)return;try{const path=await local(l.url);if(disposed||token!==l.token||paused||!l.active)return;if(l.audio.src!==path)l.audio.src=path;l.loadedUrl=l.url;l.audio.volume=l.volume;l.audio.loop=true;l.audio.play();l.playing=true;}catch{if(!disposed)errors++;}}
 function stopEffects(battleOnly=false){if(battleOnly)battleGeneration++;else generation++;for(const v of voices){if(battleOnly&&v.ui)continue;v.token++;v.audio.stop();v.busy=false;}}
 const available=!!wx.createInnerAudioContext;
 return {
  unlock(){if(disposed)return;unlocked=true;for(const l of loops.values())runLoop(l);},
  loop(key,url,volume,active){if(disposed||!available)return;let l=loops.get(key);if(!l){l=voice();loops.set(key,l);}Object.assign(l,{url,volume,active});runLoop(l);},
  async play(url,volume,deadline,{ui=false}={}){if(disposed||paused||!unlocked||!available)return false;const generationAtRequest=generation,battleToken=battleGeneration;let v=voices.find(v=>!v.busy);if(!v){if(voices.length<8){v=voice();voices.push(v);}else v=voices.reduce((a,b)=>a.started<b.started?a:b);}v.audio.stop();v.busy=true;v.ui=ui;v.started=Date.now();const token=++v.token;
   try{const path=await local(url);if(disposed||paused||generationAtRequest!==generation||token!==v.token||!ui&&battleToken!==battleGeneration)return false;if(Date.now()>deadline){v.busy=false;return false;}v.audio.src=path;v.audio.loop=false;v.relative=master>0?volume/master:0;v.audio.volume=volume;v.audio.play();played++;return true;}catch{if(token===v.token)v.busy=false;if(!disposed)errors++;return false;}
  },
  preload(urls){return Promise.all(urls.map(url=>local(url).catch(()=>null)));},stopEffects,
  pause(value){paused=value;if(value)stopEffects();for(const l of loops.values())runLoop(l);},
  volume(value){master=value;for(const v of voices)v.audio.volume=(v.relative||0)*value;},
  stats(){return {available,state:disposed?'closed':paused?'suspended':unlocked?'running':'locked',voices:voices.filter(v=>v.busy).length,buffers:files.size,played,errors,loops:[...loops].map(([key,l])=>({key,active:l.active,volume:l.volume}))};},
  dispose(){if(disposed)return;disposed=true;stopEffects();for(const v of [...voices,...loops.values()]){v.token++;v.audio.offEnded?.(v.end);v.audio.offError?.(v.error);v.audio.stop();v.audio.destroy();}voices.length=0;loops.clear();files.clear();}
 };
}
