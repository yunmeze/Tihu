#!/usr/bin/env python3
"""Replay static animation research. Read source bytes only; never execute the EXE/Godot.
Writes only --out, outside --repo; Python 3 stdlib + GNU objdump. No repo imports.
Interpretations are reviewed static analysis, not proof of complete game behavior.
"""
from pathlib import Path
import argparse, hashlib, json, struct, subprocess, re

HERE = Path(__file__).resolve().parents[1]
EXE = '原版游戏/LP传奇单机版_重生.exe'
EXPECTED_FILES = {
    EXE: (2502656, '21dc753d3aa828fb29dc171e595857be234833edc43a1d80833540ae7e355b84'),
    '原版游戏/Data/Mon/5.lpRes': (1215784, '0f79fed5c0c255447f4097d7501afe7596c09694db76f59beb9e1ec029610d5b'),
    '原版游戏/Data/Mon/7.lpRes': (1315620, '4e2bea0144c11833495a7ada6dfa59871892727e59aec5860c48df65910ee766'),
}
# Endpoints are exclusive and aligned to instructions (tables are read separately).
RANGES = {
    'live_frame_appearance': (0x5c3f39, 0x5c3f7c),
    'live_resource_cache_miss': (0x5c4519, 0x5c45c3),
    'resource_wrapper': (0x631d9b, 0x631dcd),
    'corpse_frame': (0x5b6405, 0x5b6454),
    'corpse_resource_cache_miss': (0x5b648a, 0x5b64ee),
    'initialize_idle': (0x5a1cd2, 0x5a1d1e),
    'entry_clock': (0x5c849c, 0x5c8568),
    'slow_q_set': (0x5c8924, 0x5c895a),
    'slow_q_expiry': (0x5c89f7, 0x5c8a2c),
    'slow_q_other_status': (0x5c8a6e, 0x5c8a9a),
    'hp_death_priority': (0x5c917b, 0x5c91b3),
    'death_entry': (0x5c95f5, 0x5c9638),
    'dispatch': (0x5c9930, 0x5c9990),
    'pursuit_context': (0x5c9af1, 0x5c9afe),
    'pursuit_reentry_clock': (0x5c9f13, 0x5c9f3b),
    'pursuit_attack_entry': (0x5c9fb3, 0x5ca084),
    'idle_phase': (0x5ca506, 0x5ca53c),
    'wander_entry': (0x5ca5c7, 0x5ca692),
    'idle_special_gate': (0x5ca7dc, 0x5ca80f),
    'idle_frame': (0x5caea9, 0x5caed2),
    'walk_attack_frames': (0x5cafe5, 0x5cb0aa),
    'attack_strike_gate': (0x5cb0ff, 0x5cb13d),
    'attack_completion_hurt_death': (0x5cccdc, 0x5cce26),
    'death_terminal': (0x5ccf5a, 0x5cd03a),
    'direction_reservation': (0x5d27b0, 0x5d2899),
    'movement_tail': (0x5d2ffb, 0x5d3028),
    'resource_reader': (0x634700, 0x6347e7),
}
ANCHORS = {
    0x5c3f56: ('0fbf54d022', 'Live renderer reads signed entity +0x22 into nativeFrame local'),
    0x5c3f70: ('668b54c108', 'Live renderer reads entity appearance low WORD +8'),
    0x5c45be: ('e8add70600', 'Live loader calls resource wrapper with unchanged nativeFrame pointer'),
    0x631dc8: ('e833290000', 'Wrapper forwards nativeFrame pointer to634700'),
    0x5b644d: ('8d94d299000000', 'Corpse stored direction becomes nativeFrame153+9*d'),
    0x5b64e9: ('e882b80700', 'Corpse loader uses same resource wrapper'),
    0x5a1cd5: ('66c7461e0100', 'Initialize state 1'),
    0x5a1d05: ('c7462801000000', 'Initialize phase 1'),
    0x5a1d0c: ('66c1e10266034e28', 'Initial frame = direction*4 + phase'),
    0x5a1d1a: ('66894e22', 'Store initial native frame in entity +0x22'),
    0x5c84b5: ('66395e1e', 'Check state zero before clock increment'),
    0x5c8547: ('0f84ed4a0000', 'State zero jumps to return path'),
    0x5c854d: ('8b7e2447897e24', 'Increment signed 32-bit entity clock +0x24 once per active update'),
    0x5c894a: ('c7853cffffff01000000', 'q = 1 when +0xb2 status active'),
    0x5c8a21: ('899d3cffffff', 'q reset to zero when +0xb2 expires; ebx remains zero in this section'),
    0x5c917b: ('8b46783bc30f8faa070000', 'HP > 0 bypasses death initialization'),
    0x5c9186: ('66817e1e91000f849e070000', 'Already in death does not reinitialize'),
    0x5c962a: ('897e24897e2866c7461e9100', 'Death sets clock=0 phase=0 state=145 before same-call dispatch'),
    0x5c9971: ('0fbf461e483d90000000', 'State dispatcher indexes state-1'),
    0x5c9983: ('8a90e0d05c00ff2495c8d05c00', 'Two-level jump table'),
    0x5ca010: ('663946206689461e', 'Pursuit checks previous_state=33 and stores current state=33'),
    0x5ca01e: ('897e24c7462800000000', 'New pursuit movement clock=-1 phase=0; edi=-1 established in context'),
    0x5ca069: ('66c7461e5100897e24c7462800000000', 'Attack entry state81 clock=-1 phase0; frame held'),
    0x5ca509: ('b90c00000099f7f9', 'Idle phase gate: clock modulo 12'),
    0x5ca519: ('8b4e28418bc1894e2883f805', 'Idle increments phase then compares to 5'),
    0x5ca52f: ('c7462801000000', 'Idle wraps to phase1'),
    0x5ca5d6: ('c74624ffffffff', 'Wander entry clock=-1'),
    0x5ca5de: ('c7462801000000', 'Wander entry phase1'),
    0x5ca687: ('66c7461e2100e94a010000', 'Successful wander sets state33 then executes idle frame tail'),
    0x5caea9: ('668b461a66c1e0026603462866894622', 'Idle stored frame=4*direction+phase'),
    0x5caff2: ('66c746202100', 'Walk updates previous_state to33'),
    0x5cb002: ('e8b9780000', 'Movement step before frame gate; may change state to idle'),
    0x5cb00a: ('83c3040fbfcb99f7f9', 'Walk frame gate uses q+4'),
    0x5cb01b: ('837e28057c03897e28', 'Walk resets phase>=5 to0 before increment'),
    0x5cb02c: ('42895628', 'Walk preincrements phase'),
    0x5cb030: ('668b561a666bd2069b6603562883c22166895622', 'Walk stored frame=33+6*direction+new phase'),
    0x5cb04f: ('66c74620510083c004', 'Attack previous_state81 and q+4 frame interval'),
    0x5cb06d: ('8b5e288d1440d1e26603562883c251', 'Attack computes frame with old phase'),
    0x5cb07c: ('438bcb6689562283f901895e28', 'Attack stores frame, then commits phase+1'),
    0x5cb104: ('83f9050f85d11b0000', 'Main strike dispatch at new phase5 / old phase4'),
    0x5cccde: ('837e28060f8c52030000', 'Attack completion after new phase>=6'),
    0x5cccf8: ('894624894e4c897e2866894e1e6689562e', 'Completion writes clock-1, aggro1, phase0, idle1, cooldown'),
    0x5ccd56: ('b90500000099f7f9', 'Hurt clock modulo5'),
    0x5ccd66: ('668b561a8b4e2866d1e266035628', 'Hurt uses 2*direction + old phase'),
    0x5ccd79: ('81c281000000', 'Hurt frame base129'),
    0x5ccdcc: ('c74624ffffffff897e2866895e1e', 'Hurt completion clock-1 phase0 idle1'),
    0x5ccde8: ('81e203000080', 'Signed modulo4 death clock gate'),
    0x5ccdfb: ('668b461a8b4e28666bc00966034628', 'Death uses 9*direction + old phase'),
    0x5cce0f: ('05910000004166894622', 'Death base145 and post-incremented phase'),
    0x5ccf5a: ('837e28090f8c9c000000', 'Terminal after nine emitted frames'),
    0x5ccf68: ('c7462808000000', 'Clamp terminal phase to8'),
    0x5ccf8b: ('893cc8', 'Clear occupancy kind'),
    0x5ccfae: ('897cc804', 'Clear occupancy entity id'),
    0x5ccfd2: ('8b56088954c804', 'Store appearance in corpse map second word'),
    0x5ccffd: ('890cd0', 'Store direction in corpse map first word'),
    0x5d27c2: ('ff248d9c285d00', 'Direction table base'),
    0x63473b: ('8d0cc50d000000', 'Resource index seek = native frame*8+13, no frame subtraction'),
}

def require(ok, message):
    if not ok: raise ValueError(message)
def sha(b): return hashlib.sha256(b).hexdigest()
def jbytes(v): return (json.dumps(v, ensure_ascii=False, indent=2)+'\n').encode()
def no_symlinks(path):
    p=Path(path).absolute()
    for x in (p,*p.parents): require(not x.is_symlink(), f'Refuse symlink path component: {x}')
    return p.resolve()
def put(out, relative, value):
    target=out/relative; no_symlinks(target)
    require(out in target.resolve().parents, 'Output escaped requested directory')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(value if isinstance(value,bytes) else jbytes(value))

def pe_map(b):
    p=struct.unpack_from('<I',b,0x3c)[0]
    require(b[p:p+4]==b'PE\0\0','Not PE')
    machine,n=struct.unpack_from('<HH',b,p+4); opt=p+24
    require(machine==0x14c and struct.unpack_from('<H',b,opt)[0]==0x10b,'Not PE32 i386')
    base=struct.unpack_from('<I',b,opt+28)[0]
    start=opt+struct.unpack_from('<H',b,p+20)[0]; sections=[]
    for i in range(n):
        name,vs,rva,rs,off=struct.unpack_from('<8sIIII',b,start+i*40)
        sections.append(dict(name=name.rstrip(b'\0').decode(),virtual_size=vs,rva=rva,raw_size=rs,raw_offset=off))
    def offset(va):
        for s in sections:
            if s['rva']<=va-base<s['rva']+s['raw_size']:return s['raw_offset']+va-base-s['rva']
        raise ValueError(f'Unmapped VA {va:x}')
    return dict(machine='i386',image_base=hex(base),sections=sections),offset

def signed16(v): return v-65536 if v&0x8000 else v

def pack(b, appearance):
    k=b[3]^2;n=struct.unpack_from('<H',b,10)[0]^k
    require(n==217,'Unexpected frame count')
    rows=[]
    for i in range(n):
        off=12+8*i; p=(struct.unpack_from('<I',b,off)[0]^k)-1
        size=struct.unpack_from('<I',b,off+4)[0]^k
        require(p>=12+8*n and p+4+size<=len(b),'Invalid resource range')
        bmp=b[p+4:p+4+size];require(bmp[:2]==b'BM','Not BMP')
        require(struct.unpack_from('<I',bmp,2)[0]==size,'BMP declared length differs')
        width,height=struct.unpack_from('<ii',bmp,18)
        require(width>0 and height!=0,'Invalid dimensions')
        prefix=[signed16(struct.unpack_from('<H',b,p+x)[0]^k) for x in (0,2)]
        rows.append(dict(native_frame=i,table_record_zero_based=i,table_file_offset=off,
            vb_seek_position=off+1,prefix_file_offset=p,image_file_offset=p+4,image_bytes=size,
            prefix_signed16=prefix,width=width,height=height,
            bit_depth=struct.unpack_from('<H',bmp,28)[0],encoded_record_hex=b[off:off+8].hex(),
            encoded_prefix_hex=b[p:p+4].hex(),image_sha256=sha(bmp)))
    require(rows[0]['image_sha256']==rows[1]['image_sha256'],'Frame0 image no longer duplicates1')
    require(rows[0]['prefix_signed16']==[216,0],'Unexpected record0 prefix')
    return dict(appearance=appearance,source_path=f'原版游戏/Data/Mon/{appearance}.lpRes',
        source_sha256=sha(b),xor_key=k,record_count=n,
        native_layout_range=[1,216],all_records_have_valid_bmp_headers=True,
        record_zero=dict(image_bytes_equal_record_one=True,prefix=[216,0],
            ordinary_registration=False,semantic_role='Reserved/metadata-like prefix; exact producer intent not proven. Do not use as normal frame1 or subtract1.'),
        records=rows)


def contract():
    dirs=['N','NE','E','SE','S','SW','W','NW'];steps=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]]
    clips={}
    for name,state,stride,count,phase_start,base in [('idle',1,4,4,1,0),('walk',33,6,6,0,33),('attack',81,6,6,0,81),('hurt',129,2,2,0,129),('death',145,9,9,0,145)]:
        clips[name]=dict(state_code=state,direction_stride=stride,allocated_frames_per_direction=count,
            native_frames_by_direction={d:list(range(base+stride*i+phase_start,base+stride*i+phase_start+count)) for i,d in enumerate(dirs)})
    clips['idle'].update(formula='stored_frame = 4*d + p',clock_period_ticks=12,
        phase_update='if clock % 12 == 0: p += 1; if p >= 5: p = 1',
        emission='Write frame on every reached ordinary idle tail, even if phase gate not due.',
        stable_phases=[1,2,3,4],entry='Initializer sets state1,p1,frame4*d+1. Completion of attack/hurt sets clock-1,p0; next eligible idle call increments clock to0 then p to1.',
        evidence=['initialize_idle','idle_phase','idle_frame','idle_special_gate'])
    clips['walk'].update(formula='stored_frame = 33 + 6*d + new_p',clock_period_ticks='4+q',
        phase_update='On frame gate: if p >= 5: p = 0; p += 1; emit new p.',
        stable_emitted_phases=[1,2,3,4,5],allocated_but_not_emitted_by_this_walk_loop_phase=0,
        warning='Six allocated slots per direction do NOT imply a six-frame cyclic walk. Do not use modulo6.',
        stored_frame_when_not_due='unchanged',movement_gate='clock % (q+1) == 0 calls 0x5d28c0 before frame gate; movement may set state1, but this invocation continues the walk-frame code.',
        previous_state_write=33,evidence=['walk_attack_frames','movement_tail'])
    clips['attack'].update(formula='stored_frame = 81 + 6*d + old_p',clock_period_ticks='4+q',
        emitted_phases=[0,1,2,3,4,5],phase_update='Emit old p, then p += 1.',
        main_strike_dispatch_old_phase=4,main_strike_dispatch_new_phase=5,
        attack_kind_5_extra_effect_old_phase=0,
        completion='On emitted old_p5: preserve final attack frame, set state1,clock-1,p0; copy +0x30 to cooldown +0x2e and set aggro clock +0x4c to1.',
        stored_frame_when_not_due='unchanged',previous_state_write=81,
        evidence=['walk_attack_frames','attack_strike_gate','attack_completion_hurt_death'])
    clips['hurt'].update(formula='stored_frame = 129 + 2*d + old_p',clock_period_ticks=5,
        emitted_phases=[0,1],phase_update='Emit old p then p += 1; if p >=2 set state1,clock-1,p0 and hold final hurt frame.',
        relative_clock_values_if_entry_clock_zero=[5,10],
        entry_clock_scope='The [5,10] schedule is conditional on clock0,p0 entry; external damage-entry sites are not exhaustively recovered in v1.',
        evidence=['attack_completion_hurt_death'])
    clips['death'].update(formula='stored_frame = 145 + 9*d + old_p',clock_period_ticks=4,
        emitted_phases=list(range(9)),death_transition='After active clock increment, HP<=0 and state!=145 enters death (ordinary non-revival branch): state145,clock0,p0. Death frame0 is emitted in that same invocation.',
        emission_clocks=[0,4,8,12,16,20,24,28,32],
        terminal='After phase8 emission, p increments to9 then clamps to8; both occupancy words at 0x63ed6c are cleared; corpse map0x63ed7c stores direction and appearance. Entity state is not set to0 here.',
        corpse_frame_formula='153 + 9*d',
        time_to_terminal_seconds=None,automatic_delete_seconds=None,
        warning='No 1.2-second removal is established by this path; corpse replacement/clearing elsewhere is outside this animation slice.',
        evidence=['hp_death_priority','death_entry','dispatch','attack_completion_hurt_death','death_terminal'])
    return dict(schema='a01-ordinary-animation-contract-v1',status='static_source_contract_not_runtime_validation',
        source_exe_sha256=EXPECTED_FILES[EXE][1],binding_dependency=dict(artifact='a01-source-contract-v1/A01_SOURCE_CONTRACT.json',bytes=4467,sha256='d4545b9490aefaf2946176beda4d271f98916f4f367c81e3b411dcac02811c7f',note='A01 identity bindings are independently completed in the preceding artifact; no new lookup reconstruction here.'),scope=dict(appearances=[5,7],
            a01_ordinary_spawn_count_from_separately_pinned_binding=45,
            excluded=['appearance888 special initialization','complete AI/target selection','damage calculation/drop logic','all revival and named-special branches','wall-clock calibration','Godot implementation/runtime verification']),
        native_indexing=dict(table_index_equals_native_frame=True,subtract_one=False,
            vb_seek_formula='native_frame*8+13',zero_based_file_offset_formula='native_frame*8+12',
            pointer_field_conversion='Decoded image-record pointer is VB 1-based, so subtract1 from THAT pointer only; not from frame id.',
            allocated_native_frame_range=[1,216],record_count=217,
            record_zero='Valid duplicate image bytes of frame1, but decoded prefix=[216,0], not frame1 registration; keep separate.'),
        render_chain=dict(live='entity+0x22 -> local nativeFrame -> wrapper0x631d70 -> reader0x634700, unchanged',appearance='entity+8 low signed WORD -> decimal filename + .lpRes under Mon root',corpse='corpse map0x63ed7c direction/appearance -> frame153+9*d -> same wrapper and reader',cache_key='appearance + 257*nativeFrame',evidence=['live_frame_appearance','live_resource_cache_miss','resource_wrapper','resource_reader','corpse_frame','corpse_resource_cache_miss']),
        fields={'appearance':{'offset':'0x08','storage':'i32','renderer_read':'low i16'},
            'direction':{'offset':'0x1a','storage':'i16'},'state':{'offset':'0x1e','storage':'i16'},
            'previous_state':{'offset':'0x20','storage':'i16'},'stored_frame':{'offset':'0x22','storage':'i16'},
            'clock':{'offset':'0x24','storage':'i32'},'phase':{'offset':'0x28','storage':'i32'},
            'hp':{'offset':'0x78','storage':'i32'}},
        directions=[dict(code=i,name=d,cell_delta=steps[i]) for i,d in enumerate(dirs)],
        update_order=['If state0: return before clock increment.','Increment clock once for active entry.',
            'Process statuses and HP prelude; some conditions can return before animation dispatch.',
            'Ordinary death transition takes priority over state dispatch; sets clock0,p0.',
            'Dispatch state1,33,81,129,145 through original jump tables.',
            'Store native frame only at the respective state-specific write sites; hold on other paths.'],
        timing=dict(unit='eligible calls to original update0x5c8470; clock increments before state work',
            original_clock_hz=None,seconds_claims_allowed=False,
            note='Do not import current reconstruction 50Hz as original timing. Early returns/status effects can advance clock without emitting a frame.',
            q=dict(values=[0,1],local='ebp-0xc4',default=0,
                rule='q1 while entity+0xb2 is active after its decrement; reset0 on expiry. Alternate +0xae branch retains/resets0.',
                affected=['walk frame period4+q','attack frame period4+q','walk movement period1+q'])),
        transitions=dict(pursuit_walk=dict(state=33,new_previous_state_mismatch=dict(clock=-1,phase=0,frame='held'),
                previous_state_already_33='No clock/phase reset; held frame.',next_eligible_frame_gate='Starting clock-1,p0: next active call clock0 emits walk phase1 if no preemption.'),
            wander_walk=dict(state=33,clock=-1,phase=1,frame='Same call falls through idle tail and emits4*d+1 using possibly changed direction.',
                next_eligible_frame_gate='Next active call clock0 emits walk phase2 if no preemption.'),
            attack=dict(state=81,clock=-1,phase=0,frame='held until next frame gate; normally next call clock0 emits phase0.')),
        clips=clips,
        integration_cautions=['Keep stored_frame separate from state and phase; transitions do not generally rewrite the visible frame immediately.',
            'A source clip layout is not by itself a playback loop; walk is the concrete counterexample.',
            'Do not generate a frame from state+direction+phase universally: idle preincrements, attack/death use old phase, and entry paths differ.',
            'Map movement can change state within a walk call before the walk frame write; full movement/AI integration remains separate.',
            'Source frames/offsets are not texture-atlas indices or zero-based clip-local phase indices.'])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,default=HERE);a=ap.parse_args()
    repo=no_symlinks(a.repo);out=no_symlinks(a.out)
    require(repo!=out and repo not in out.parents and out not in repo.parents,'Output must be outside and not an ancestor of source repo')
    source=[];data={}
    for path,(size,digest) in EXPECTED_FILES.items():
        b=(repo/path).read_bytes();require(len(b)==size and sha(b)==digest,f'Source pin mismatch: {path}')
        data[path]=b;source.append(dict(path=path,bytes=size,sha256=digest))
    exe=data[EXE];pe,offset=pe_map(exe)
    require(pe['image_base']=='0x400000','Unexpected image base')
    pins=dict(schema='a01-animation-source-pins-v1',observed_repository_commit='749c7304c518308013a64a3915207835a261127e',
        commit_policy='Provenance only. Replays accept identical pinned source bytes at another backup commit.',files=source)
    anchors=[]
    for va,(h,note) in ANCHORS.items():
        expected=bytes.fromhex(h);off=offset(va)
        require(exe[off:off+len(expected)]==expected,f'Instruction mismatch at {hex(va)}')
        anchors.append(dict(va=hex(va),file_offset=off,bytes_hex=h,interpretation=note))
    ranges=[]
    for name,(lo,hi) in RANGES.items():
        assembly=subprocess.check_output(['objdump','-d','-Mintel','--insn-width=16',f'--start-address={lo}',f'--stop-address={hi}',str(repo/EXE)],text=True).replace(str(repo/EXE),EXE)
        put(out,f'evidence/{name}.asm.txt',assembly.encode())
        code=exe[offset(lo):offset(lo)+hi-lo]
        ranges.append(dict(name=name,start_va=hex(lo),end_va_exclusive=hex(hi),file_offset=offset(lo),bytes=len(code),sha256=sha(code)))
    imports=subprocess.check_output(['objdump','-p',str(repo/EXE)],text=True)
    relevant_imports={}
    for rva,name in [(0x11a8,'__vbaFileSeek'),(0x1104,'__vbaGet3')]:
        line=next((x.strip() for x in imports.splitlines() if f'{rva:08x}' in x and name in x),None)
        require(line is not None,f'Import mismatch {name}');relevant_imports[hex(0x400000+rva)]=line
    jump_bytes=exe[offset(0x5cd0e0):offset(0x5cd0e0)+145]
    jumps={str(i+1):hex(struct.unpack_from('<I',exe,offset(0x5cd0c8)+jump_bytes[i]*4)[0]) for i in range(145)}
    nondefault={s:v for s,v in jumps.items() if v!='0x5cd03a'}
    require(nondefault=={'1':'0x5c9990','33':'0x5cafe5','81':'0x5cb049','129':'0x5ccd53','145':'0x5ccde5'},'Unexpected state jump table')
    direction_targets=struct.unpack_from('<8I',exe,offset(0x5d289c))
    require(direction_targets==(0x5d27c9,0x5d27fa,0x5d2802,0x5d2808,0x5d2826,0x5d2857,0x5d285f,0x5d2865),'Direction jump table mismatch')
    evidence=dict(schema='a01-animation-exe-evidence-v1',pe=pe,source_sha256=sha(exe),anchors=anchors,ranges=ranges,
        imports=relevant_imports,state_dispatch=dict(index='state-1',selector_va='0x5cd0e0',target_va='0x5cd0c8',nondefault=nondefault,default='0x5cd03a'),
        direction_dispatch=dict(table_va='0x5d289c',targets=[hex(x) for x in direction_targets]),
        evidence_limit='Pins prove source and exact instructions. Semantics are static reviewed reconstructions; no native execution or complete control-flow proof.')
    packs=[pack(data[f'原版游戏/Data/Mon/{n}.lpRes'],n) for n in [5,7]]
    c=contract()
    put(out,'SOURCE_PINS.json',pins);put(out,'A01_ANIMATION_CONTRACT.json',c)
    put(out,'SOURCE_FRAME_INDEX.json',dict(schema='a01-source-frame-index-v1',pixel_decode_performed=False,packs=packs))
    put(out,'evidence/EXE_EVIDENCE.json',evidence)
    put(out,'.gdignore',b'')
    put(out,'local/VALIDATION.json',dict(status='static_checks_passed',source_files=len(source),instruction_anchors=len(anchors),disassembly_ranges=len(ranges),bmp_records=sum(len(p['records']) for p in packs),native_exe_run=False,godot_run=False,pixels_decoded=False,tests_do_not_prove_gameplay=True))
    print(json.dumps(dict(out=str(out),status='static_contract_ready',anchors=len(anchors),frames=sum(len(p['records']) for p in packs))))

if __name__=='__main__':main()
