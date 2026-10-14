import fs from 'node:fs/promises';
import {spawn} from 'node:child_process';

const dir=process.env.LP_RULE_REPORT_DIR||'reports/game-recheck-20261012';
const names=(await fs.readdir('tools')).filter(name=>name.endsWith('-tests.mjs')&&name!=='run-preview-tests.mjs').sort();
const report={passed:false,count:names.length,startedAt:new Date().toISOString(),results:[]};
await fs.mkdir(dir,{recursive:true});
for(const file of names){
 const result=await new Promise(resolve=>{
  const child=spawn(process.execPath,['tools/'+file],{stdio:['ignore','pipe','pipe'],windowsHide:true});
  let output='';child.stdout.on('data',data=>output+=data);child.stderr.on('data',data=>output+=data);
  child.once('error',error=>resolve({file,passed:false,pid:child.pid,error:String(error),output}));
  child.once('exit',(code,signal)=>resolve({file,passed:code===0,code,signal,pid:child.pid,output}));
 });
 report.results.push(result);await fs.writeFile(dir+'/rule-regressions.json',JSON.stringify(report,null,2));
 console.log(result.passed?'PASS':'FAIL',file);if(!result.passed)console.log(result.output);
}
report.passed=report.results.every(result=>result.passed);report.completedAt=new Date().toISOString();
await fs.writeFile(dir+'/rule-regressions.json',JSON.stringify(report,null,2));
console.log({passed:report.passed,suites:report.count});if(!report.passed)process.exitCode=1;
