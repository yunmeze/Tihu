"""Keep the native WAVs intact; publish the recovered playback dispatch table."""
import hashlib, json, pathlib, wave, importlib, sys

root = pathlib.Path.cwd()
effects = {6:'符',28:'符爆炸',12:'炼尸咒',13:'炼尸咒',91:'炼尸咒',7:'HP恢复',8:'HP恢复2',9:'精神盾',22:'诱惑',10:'下毒',11:'下毒',14:'火球',15:'火球',16:'火球',17:'火球',18:'雷电术',56:'小雷电',20:'冰咆哮',90:'地狱雷光',24:'火球爆炸',26:'火球爆炸',25:'符爆炸',27:'符爆炸',72:'伤害反弹',21:'魔法盾'}
rules = {'version':1,'music':'Sound/bgm.wav','effects':effects,'monsterVariants':{'idle':1,'attack':2,'hurt':3,'death':4}}
sys.path.insert(0, str(root/'tools'))
native = importlib.import_module('native-code').NativeCode()
instructions = {a:(m,o) for a,m,o in native.disasm(native.prolog(0x61ef00),0x61f175)}
addresses = sorted(instructions)
next_address = dict(zip(addresses, addresses[1:]))
def footstep(index):
    address, difference = 0x61ee70, 0
    for _ in range(200):
        mnemonic, operand = instructions[address]
        if mnemonic == 'cmp' and operand.startswith('si, '): difference = index-int(operand.split(', ')[1],0)
        elif mnemonic == 'mov' and operand.startswith('edx, 0x'): return native.string(int(operand.split(', ')[1],0))
        elif mnemonic == 'jmp' or mnemonic == 'jl' and difference<0 or mnemonic == 'jle' and difference<=0 or mnemonic == 'jg' and difference>0 or mnemonic == 'jge' and difference>=0:
            address = int(operand,0); continue
        address = next_address[address]
    raise ValueError(index)
ranges=[]
for index in range(1100):
    stem=footstep(index)
    if ranges and ranges[-1][2]==stem: ranges[-1][1]=index
    else: ranges.append([index,index,stem])
rules['footsteps']=ranges
rules['itemSounds']={}
for index in range(8):
    address=native.number(0x5ef098+index*4,'<I')
    _,_,operand=native.disasm(address,address+5)[0]
    rules['itemSounds'][index+7]=native.string(int(operand.split(', ')[1],0))
(root/'public/assets/data/audio.json').write_text(json.dumps(rules, ensure_ascii=False), encoding='utf-8')
records = []
for file in sorted((root/'public/assets/Sound').rglob('*.wav')):
    with wave.open(str(file),'rb') as wav:
        records.append({'file':file.relative_to(root/'public/assets').as_posix(),'channels':wav.getnchannels(),'rate':wav.getframerate(),'sampleBytes':wav.getsampwidth(),'duration':round(wav.getnframes()/wav.getframerate(),4),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
report = {'source':'LP传奇单机版_重生.exe','sourceSha256':hashlib.sha256((root/'reference/LP传奇单机版-重生v1.2.2E/LP传奇单机版_重生.exe').read_bytes()).hexdigest(),'heroPlayer':'0x636ac0','monsterPlayer':'0x6367d0','effectDispatch':'0x5a2d15–0x5a3094','backgroundCall':'0x58a5d0','firewallLoopCall':'0x59b6a9','footstepDispatch':'0x61ee70–0x61f16b','monsterCalls':{'idle':'0x5ca4f5','attack':'0x5ccccb','hurt':'0x5ccdb1 / 0x625d14','death':'0x5cd029'},'rules':rules,'adaptations':['Browser music streams the one native BGM; no map-specific tracks exist in this resource set.','SFX use bounded channels, distance attenuation, per-file throttling and late-load rejection.','Idle cries use deterministic timers without consuming gameplay random numbers.'],'files':records}
(root/'reports/native-audio-source.json').write_text(json.dumps(report, ensure_ascii=False,indent=2), encoding='utf-8')
print(json.dumps({'music':1,'effects':len(records)-1,'duration':next(r['duration'] for r in records if r['file']==rules['music']),'mappedEffectTypes':len(effects)},ensure_ascii=False))
