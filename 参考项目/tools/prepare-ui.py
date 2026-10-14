from pathlib import Path
import sys,json,struct,re
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image,ImageFont,ImageDraw
A=ROOT/'public/assets';S=ROOT/'reference/LP传奇单机版-重生v1.2.2E'
def save(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':')),encoding='utf8')

if '--font-only' not in sys.argv:
    # Discard unused atlas borders without changing a source pixel or frame coordinate.
    for p in (A/'sprites').rglob('index.json'):
        o=json.loads(p.read_text(encoding='utf8'));changed=False
        for i,page in enumerate(o['pages']):
            frames=[f for f in o['frames'] if f['page']==i]
            w=max(f['rect'][0]+f['rect'][2]+1 for f in frames);h=max(f['rect'][1]+f['rect'][3]+1 for f in frames)
            if page['width']!=w or page['height']!=h:
                image=Image.open(A/page['file']).crop((0,0,w,h));image.save(A/page['file'],compress_level=6);page['width']=w;page['height']=h;changed=True
        if changed:save(p,o)

    exe=(S/'LP传奇单机版_重生.exe').read_bytes();strings=[];p=90252
    while p<93532:
        n=struct.unpack_from('<I',exe,p)[0]
        if 0<n<600 and n%2==0:
            t=exe[p+4:p+4+n].decode('utf-16le',errors='replace')
            if re.match(r'^[\x20-\x7e\u3000-\u9fff\uff00-\uffef]+$',t):strings.append({'offset':p,'text':t});p+=n+4;continue
        p+=2
    skills=json.loads((A/'data/skills.json').read_text(encoding='utf8'))
    # Reused VB literals are not in skill order. Recover each actual panel/click case.
    from importlib import import_module
    skills['records']=import_module('inspect-growth').recover()[0];skills['recordSource']='native-panel-and-click-v1';skills['nativeStrings']=strings;save(A/'data/skills.json',skills)

chars=set(' LP传奇重生自动战斗暂停继续装备背包技能任务图鉴地图职业战士道士法师金币等级生命魔法物攻道术魔攻物防魔防重量价格出售穿戴返回移动地图传送物品数量下一页上一页全部头盔项链衣服鞋手镯戒指盾牌武器药品当前目标攻击恢复快速慢速确定关闭原版数值新游戏选择角色英雄海曦村北树林深处加载中保存成功未学习已学习技能点条件升级获得欢迎战斗场景准备中路线查看属性开悟当前任务商城仓库原始数据输入规则待核对图像索引筛选说明展示当前地图怪物物品金创药小魔法药小伤害技能状态fpsABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-×/%:.，。！？（）[]=<>·：');texts=[]
for p in (A/'data').glob('*.json'):
    texts.append(p.read_text(encoding='utf8'))
for p in (ROOT/'src').glob('*.js'):
    texts.append(p.read_text(encoding='utf8'))
for p in (A/'maps').glob('*.json'):
    o=json.loads(p.read_text(encoding='utf8'));texts.extend(n['script']+n['name'] for n in o['npcs']);texts.append(o['loadScript'])
for t in texts:
    chars.update(c for c in t if 32<=ord(c)<0xe000 and c!='\ufffd')
font=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',32);size=2048;cell=38;columns=size//cell;capacity=columns*columns;glyphs={};pages=[];ordered=sorted(chars);image=None
for i,c in enumerate(ordered):
    page=i//capacity;slot=i%capacity
    if slot==0:image=Image.new('RGBA',(size,size));draw=ImageDraw.Draw(image);pages.append({'file':f'fonts/{page}.png','width':size,'height':size})
    x=(slot%columns)*cell;y=(slot//columns)*cell;draw.text((x+2,y+2),c,font=font,fill=(255,255,255,255),anchor='lt');glyphs[c]={'page':page,'rect':[x,y,cell,cell],'advance':font.getlength(c)}
    if slot==capacity-1 or i==len(ordered)-1:
        target=A/f'fonts/{page}.png';target.parent.mkdir(parents=True,exist_ok=True);height=min(size,y+cell);image.crop((0,0,size,height)).save(target,compress_level=6);pages[page]['height']=height
save(A/'fonts/index.json',{'size':32,'cell':cell,'sourceFont':'宋体 / simsun.ttc','pages':pages,'glyphs':glyphs})

if '--font-only' not in sys.argv:
    sheet=Image.new('RGB',(1000,600),(30,34,29));draw=ImageDraw.Draw(sheet)
    for pack,row in [('Hero/0',0),('Mon/4',3)]:
        index=json.loads((A/f'sprites/{pack}/index.json').read_text(encoding='utf8'));pages2=[Image.open(A/p['file']) for p in index['pages']]
        for j,num in enumerate([1,5,9,13,17,21,25,29,33,37,41,45,49,53,57,61,65,69,73,77,81,85,89,93,97,101,105,109,113,117]):
            f=index['frames'][num];x,y,w,h=f['rect'];im=pages2[f['page']].crop((x,y,x+w,y+h));xx=(j%10)*100;yy=(j//10+row)*100;sheet.paste(im,(xx+(100-w)//2,yy+10),im);draw.text((xx+6,yy+80),str(num),fill='white')
    sheet.save(ROOT/'reports/native-frame-layout.png')
    print(json.dumps({'glyphs':len(glyphs),'fontPages':len(pages),'skillRecords':len(json.loads((A/'data/skills.json').read_text(encoding='utf8'))['records'])}))
