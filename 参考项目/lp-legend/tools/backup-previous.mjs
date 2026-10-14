import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = path.resolve(import.meta.dirname, '../..');
const stamp = new Intl.DateTimeFormat('sv-SE', {timeZone:'Asia/Shanghai',dateStyle:'short',timeStyle:'medium'}).format(new Date()).replace(/[^0-9]/g,'');
const destination = path.join(root, 'backups', 'hellfarmer-'+stamp);
const entries = ['.gitignore','.tools','asset-source','dist','node_modules','package-lock.json','package.json','public','README.md','reports','src','tools'];
const files=[];
function scan(p){for(const entry of fs.readdirSync(p,{withFileTypes:true})){const file=path.join(p,entry.name);if(entry.isSymbolicLink())throw Error('Unexpected symbolic link: '+file);if(entry.isDirectory())scan(file);else files.push(path.relative(root,file));}}
for(const entry of entries){const p=path.join(root,entry);if(fs.statSync(p).isDirectory())scan(p);else files.push(entry);}
fs.mkdirSync(destination,{recursive:true});
const buffer=Buffer.alloc(4*1024*1024);
function hash(p){const fd=fs.openSync(p,'r'),h=crypto.createHash('sha256');try{for(;;){const n=fs.readSync(fd,buffer,0,buffer.length,null);if(!n)break;h.update(buffer.subarray(0,n));}return h.digest('hex');}finally{fs.closeSync(fd);}}
const records=[];let bytes=0,last=Date.now();
for(const rel of files){const from=path.join(root,rel),to=path.join(destination,rel);fs.mkdirSync(path.dirname(to),{recursive:true});let verified=false;
 for(let attempt=0;attempt<3&&!verified;attempt++){const before=fs.statSync(from);fs.copyFileSync(from,to);const sourceHash=hash(from),backupHash=hash(to),after=fs.statSync(from);verified=sourceHash===backupHash&&before.size===after.size&&before.mtimeMs===after.mtimeMs;if(verified){fs.utimesSync(to,after.atime,after.mtime);records.push({file:rel.replaceAll('\\','/'),bytes:after.size,sha256:backupHash});bytes+=after.size;}}
 if(!verified)throw Error('Source changed during backup: '+rel);
 if(Date.now()-last>5000){console.log(JSON.stringify({phase:'copy-verify',done:records.length,total:files.length,MiB:Math.round(bytes/1048576)}));last=Date.now();}
}
const report={createdAt:new Date().toISOString(),source:root,destination,verified:true,files:records.length,bytes,sharedReferenceDirectory:path.join(root,'reference'),records};
fs.writeFileSync(path.join(destination,'backup-manifest.json'),JSON.stringify(report,null,2));
fs.writeFileSync(path.join(destination,'BACKUP.md'),'# Previous project backup\n\nAll application files, dependencies, extracted assets, tools, reports and build outputs are copied and SHA-256 verified.\n\nOriginal game inputs remain in '+report.sharedReferenceDirectory+' and are shared read-only.\n');
fs.writeFileSync(path.join(root,'lp-legend','previous-backup.json'),JSON.stringify({...report,records:undefined},null,2));
console.log(JSON.stringify({...report,records:undefined}));
