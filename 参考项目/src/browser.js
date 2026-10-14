import {LPApp} from './game.js';import {browserPlatform} from './platform.js';
const canvas=document.createElement('canvas');canvas.style.cssText='position:fixed;inset:0;width:100%;height:100%;touch-action:none;';document.body.style.margin='0';document.body.style.background='#100f0b';document.body.append(canvas);
const loading=document.createElement('div');loading.style.cssText='position:fixed;inset:0;z-index:5;display:grid;place-content:center;gap:20px;padding:32px;text-align:center;background:#17120f;color:#ead3a0;font:20px SimSun,serif';loading.setAttribute('role','status');document.body.append(loading);
let app,busy=false;
async function boot(){
 if(busy)return;busy=true;loading.replaceChildren();loading.style.display='grid';loading.textContent='正在载入小小传奇…';globalThis.lpLegendReady=false;delete globalThis.lpLegendError;
 try{app=new LPApp(browserPlatform(canvas));globalThis.lpLegend=app;await app.init();globalThis.lpLegendReady=true;loading.style.display='none';}
 catch(e){globalThis.lpLegendError=String(e.stack||e);console.error(e);app?.dispose();loading.textContent='游戏资源加载失败，请检查连接后重试。';const retry=document.createElement('button');retry.textContent='重新加载';retry.style.cssText='padding:14px 30px;background:#302219;border:1px solid #af8c52;color:#f0d8a6;font:20px SimSun,serif';retry.onclick=boot;loading.append(retry);}
 finally{busy=false;}
}
boot();addEventListener('pagehide',()=>app?.dispose());
