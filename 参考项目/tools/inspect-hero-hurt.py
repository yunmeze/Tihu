"""Read the shipped executable; verify the enemy-hit gate and hurt clock."""
from pathlib import Path
from importlib import import_module
import hashlib, json

n = import_module('native-code').NativeCode()
root = Path(__file__).resolve().parent.parent
out = root / 'reports/hero-hurt-20261013'
out.mkdir(parents=True, exist_ok=True)
assert hashlib.sha256(n.data).hexdigest() == '21dc753d3aa828fb29dc171e595857be234833edc43a1d80833540ae7e355b84'
sections = [('landed-enemy-hit', 0x5d3b70, 0x5d4a46), ('clock-start', 0x618d0c, 0x618da1),
            ('freeze-clock', 0x619979, 0x619a4e), ('hurt-playback', 0x61e3a5, 0x61e4e5),
            ('action-reset', 0x61f250, 0x61f2e1)]
all_rows, evidence = {}, []
for name, lo, hi in sections:
    rows = n.disasm(lo, hi)
    all_rows.update({a: (m, o) for a, m, o in rows})
    file = out / (name + '.txt')
    file.write_text('\n'.join(f'{a:08x} {m:8} {o}' for a, m, o in rows), encoding='utf8')
    evidence.append({'file': file.relative_to(root).as_posix(), 'from': hex(lo), 'to': hex(hi),
                     'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
anchors = {
    0x5d4163: ('mov', 'ebx, 1'), 0x5d4723: ('mov', 'ebx, 1'),
    0x5d4460: ('cmp', 'word ptr [edx + ecx*4 + 0x1f7c], bx'),
    0x5d446e: ('jmp', '0x5d4a2a'),
    0x5d4a20: ('cmp', 'word ptr [edx + ecx*4 + 0x1f7c], bx'),
    0x5d4a2d: ('mov', 'dword ptr [ebp - 0x4c], 0xe1'),
    0x5d4a35: ('call', '0x61f250'),
    0x5d422e: ('jge', '0x5d4359'),  # MP absorbs magic damage, still reaches the gate.
    0x5d463e: ('jmp', '0x5d4a46'),  # Reflection bypasses the hurt gate.
    0x618d9e: ('inc', 'edi'),
    0x619a47: ('mov', 'dword ptr [ebp - 0x30], 1'),
    0x61e3ae: ('add', 'edx, 5'),
    0x61e4b6: ('cmp', 'ecx, 3'),
    0x61e4c8: ('call', '0x61f250'),
    0x61e4d9: ('add', 'dx, 0x4b'),
    0x61e4dd: ('lea', 'edx, [edx + edx*2]'),
    0x61f273: ('mov', 'dword ptr [ecx + eax*4 + 0x1f8c], 0'),
    0x61f2a1: ('mov', 'dword ptr [ecx + eax*4 + 0x1f84], 0'),
}
for address, expected in anchors.items():
    assert all_rows[address] == expected, (hex(address), all_rows.get(address))
report = {'passed': True, 'source': n.source.relative_to(root).as_posix(),
          'sourceSha256': hashlib.sha256(n.data).hexdigest(), 'anchors': len(anchors), 'evidence': evidence,
          'rules': {'eligibleAction': 'idle (native 1)', 'hurtAction': 225, 'frames': '225 + direction*3 + phase',
                    'normalClockTicks': [5, 10, 15, 20], 'frozenClockTicks': [6, 12, 18, 24],
                    'lastClockStep': 'return to idle', 'initialDelay': 'retain previously drawn frame until first step',
                    'ringAbsorptionStillReacts': True, 'reflectionSkipsReaction': True,
                    'damageOverTime': 'poison/burn decrement HP in the hero update, outside the enemy-hit gate'},
          'boundaries': ['Actor-local web animation; exiting hurt redraws idle immediately.',
                         'Existing sound/shield feedback remains at the web hit time; native sound is phase 1 and shield is phase 0.',
                         'Existing damage/reflection calculation is unchanged; this verifies the reaction gate, not full damage parity.',
                         'Existing paralysis pauses the web actor clock; native modulo phase across status transitions is not claimed.'],
          'fullNativeCombatEquivalent': False}
(out / 'native-evidence.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
print({'passed': True, 'anchors': len(anchors), 'sections': len(sections)})
