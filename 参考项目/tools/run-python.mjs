import {spawn} from 'node:child_process';
const executable=process.env.LP_PYTHON||'C:/Users/lvan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const process2=spawn(executable,process.argv.slice(2),{stdio:'inherit',env:{...process.env,PYTHONIOENCODING:'utf-8'}});
process2.on('error',e=>{console.error(e.message);process.exitCode=1;});process2.on('exit',code=>process.exitCode=code??1);
