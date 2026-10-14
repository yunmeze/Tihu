import {chromium} from 'playwright';
import fs from 'node:fs/promises';

// Record the actual Chromium process as well as the test process. launchServer
// exposes that child PID, making cancellation cleanup independent of WMI.
export async function ownedTestBrowser(name,options={}){
 const dir='reports/audit-fixes-20261012/lifecycle';await fs.mkdir(dir,{recursive:true});
 const file=`${dir}/${name}.json`,record={purpose:name,testPid:process.pid,startedAt:new Date().toISOString(),closed:false};
 const server=await chromium.launchServer({headless:true,executablePath:process.env.LP_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader'],...options});
 record.browserPid=server.process().pid;await fs.writeFile(file,JSON.stringify(record,null,2));
 let browser;try{browser=await chromium.connect(server.wsEndpoint());}catch(error){await server.close();record.closed=true;record.error=String(error);await fs.writeFile(file,JSON.stringify(record,null,2));throw error;}
 let closing;const close=()=>closing||=(async()=>{try{await browser.close();}finally{await server.close();record.closed=true;record.closedAt=new Date().toISOString();record.exitCode=server.process().exitCode;await fs.writeFile(file,JSON.stringify(record,null,2));}})();
 return {browser,close};
}
