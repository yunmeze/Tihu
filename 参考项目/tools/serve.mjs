import http from 'node:http';import fs from 'node:fs';import path from 'node:path';import os from 'node:os';
const args=process.argv.slice(2);let host=process.env.HOST||'127.0.0.1',port=Number(process.env.PORT||5180);
for(let i=0;i<args.length;i++){
 const arg=args[i];
 if(arg==='--host')host=args[i+1]&&!args[i+1].startsWith('--')?args[++i]:'0.0.0.0';
 else if(arg.startsWith('--host='))host=arg.slice(7);
 else if(arg==='--port'){if(!args[i+1]||args[i+1].startsWith('--'))throw Error('--port requires a number');port=Number(args[++i]);}
 else if(arg.startsWith('--port='))port=Number(arg.slice(7));
 else throw Error('Unknown preview option: '+arg);
}
if(!host||!Number.isInteger(port)||port<0||port>65535)throw Error('Invalid preview host or port');
const root=process.cwd(),mime={'.html':'text/html;charset=utf-8','.js':'application/javascript;charset=utf-8','.json':'application/json;charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.wav':'audio/wav','.map':'application/json'};
const server=http.createServer((req,res)=>{try{let route=decodeURIComponent(new URL(req.url,'http://localhost').pathname);if(route==='/')route='/dist/browser/index.html';else if(route==='/game.js')route='/dist/browser/game.js';else if(route.startsWith('/assets/'))route='/public'+route;const file=path.resolve(root,'.'+route);if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}const stat=fs.statSync(file);if(!stat.isFile())throw Error('Not a file');res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Cache-Control':'no-cache'});fs.createReadStream(file).pipe(res);}catch{res.writeHead(404);res.end('Not found');}});
server.listen(port,host,()=>{
 const bound=server.address(),all=host==='0.0.0.0'||host==='::',address=all?'127.0.0.1':host,url=ip=>'http://'+(ip.includes(':')?'['+ip+']':ip)+':'+bound.port;
 console.log('LP Legend preview '+url(address));console.log('Listening on '+bound.address+':'+bound.port);
 if(all)for(const ip of new Set(Object.values(os.networkInterfaces()).flat().filter(i=>i&&!i.internal&&i.family==='IPv4').map(i=>i.address)))console.log('Network: '+url(ip));
});
for(const event of ['SIGINT','SIGTERM'])process.on(event,()=>server.close(()=>process.exit(0)));
