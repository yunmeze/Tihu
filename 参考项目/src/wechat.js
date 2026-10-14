import {LPApp} from './game.js';import {wechatPlatform} from './platform.js';
const app=new LPApp(wechatPlatform(wx,GameGlobal.LP_CONFIG||{}));GameGlobal.lpLegend=app;app.init().catch(e=>console.error(e));
