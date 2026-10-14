import {spawn} from 'node:child_process';
import net from 'node:net';
const files=process.argv.slice(2);if(!files.length)throw Error('Provide one or more test scripts');
const open=()=>new Promise(resolve=>{const s=net.createConnection({host:'127.0.0.1',port:5180});s.once('connect',()=>{s.destroy();resolve(true);});s.once('error',()=>resolve(false));s.setTimeout(800,()=>{s.destroy();resolve(false);});});
let server,closed;
try{
 if(!await open()){
  server=spawn(process.execPath,['tools/serve.mjs','--host','127.0.0.1'],{stdio:['ignore','pipe','pipe'],windowsHide:true});closed=new Promise(resolve=>server.once('exit',resolve));console.log('Owned test preview PID',server.pid);
  await new Promise((resolve,reject)=>{let text='';const timer=setTimeout(()=>reject(Error('Preview startup timeout')),20000);server.stdout.on('data',data=>{process.stdout.write(data);text+=data;if(text.includes('Listening on')){clearTimeout(timer);resolve();}});server.once('error',e=>{clearTimeout(timer);reject(e);});server.once('exit',code=>{clearTimeout(timer);reject(Error('Preview exited '+code));});});
 }else console.log('Reusing an existing preview; it will remain running');
 const results=await Promise.allSettled(files.map(file=>new Promise((resolve,reject)=>{const child=spawn(process.execPath,[file],{stdio:'inherit',windowsHide:true});console.log('Owned test',file,'PID',child.pid);child.once('error',reject);child.once('exit',code=>code===0?resolve(file):reject(Error(file+' exited '+code)));})));
 for(const r of results)console.log(r.status,r.status==='fulfilled'?r.value:r.reason.message);if(results.some(r=>r.status==='rejected'))process.exitCode=1;
}finally{if(server&&server.exitCode===null&&server.signalCode===null){server.kill();await closed;}if(server)console.log('Owned preview stopped; port open:',await open());}
