#!/usr/bin/env python3
"""Validate the extracted disk, all 100 caves and reconstructed audio."""
import hashlib, json, struct, wave
import z80
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
a=ROOT/'assets'
manifest=json.loads((ROOT/'Extracted/manifest.json').read_text())
assert hashlib.sha256((ROOT/manifest['source']).read_bytes()).hexdigest()==manifest['sha256']
for f in manifest['files']:
 b=(ROOT/'Extracted'/f['name']).read_bytes()
 assert len(b)==f['length']
 assert hashlib.sha256(b).hexdigest()==f['sha256']
caves=json.loads((a/'caves.json').read_text());maps=(a/'caves.bin').read_bytes()
assert len(caves)==100 and len(maps)==88000
for i,c in enumerate(caves):
 m=maps[i*880:(i+1)*880]
 assert m.count(37)==1 and m.count(4)==1
 assert set(m[:40]+m[-40:]+m[::40]+m[39::40]) <= {7,4,37}, (i, "unexpected open boundary")
 assert c['required']>0 and c['time']>0
# Independently execute DASHIII.ECR's original Z80 decoder, stubbing only
# firmware screen calls, and compare every decoded VRAM byte.
cpu=z80.Z80Machine()
cpu.set_memory_block(0x4500,(ROOT/'Extracted/DASHIII.ECR').read_bytes())
cpu.sp=0x8000;cpu.memory[0x8000]=0xf0;cpu.memory[0x8001]=0xff;cpu.pc=0x4500
for addr in [0xbc11,0xbc0e,0xfff0]:cpu.set_breakpoint(addr)
for _ in range(30):
 cpu.ticks_to_stop=1000000;cpu.run()
 if cpu.pc==0xfff0:break
 if cpu.pc in [0xbc11,0xbc0e]:
  cpu.pc=cpu.memory[cpu.sp]+256*cpu.memory[cpu.sp+1];cpu.sp+=2
else:raise AssertionError('Original loading decoder did not return')
assert bytes(cpu.memory[0xc000:])==(a/'loading-screen.bin').read_bytes()
assert len(list(a.glob('*.wav')))==7
for p in a.glob('*.wav'):
 with wave.open(str(p)) as w:
  assert w.getframerate()==44100 and w.getnchannels()==1 and w.getsampwidth()==2
  frames=w.readframes(w.getnframes());values=struct.unpack('<'+'h'*(len(frames)//2),frames)
  assert max(values)>0 and min(values)<0,p.name
provenance={'sourceSha256':manifest['sha256'],'runtime':'native Rust, no emulator','loadingScreen':{'source':'DASHIII.ECR','paletteSource':'DASHIII.PAR','mode':0,'decoder':'RLE offset 0x3f; two runs per triple; 16384 VRAM bytes'},'maps':{'address':'0xb0e0','width':40,'height':22,'count':100,'decoderRoutines':['0x13d1','0x11e2','0x173d','0x16af']},'graphics':{'bank':'0x2c00..0x5daf','tileLookup':'0x5df0','playerIdle':'0x58f0','playerRight':'0x59b0','playerLeft':'0x5bb0','palettes':'original routine 0x2995'},'audio':{'musicRoutine':'0x183d','noteSequence':'0x6979','periodTable':'0x6a79','ayRegisterWriter':'0x1818','deathParameters':'0x043c','sampleRate':44100,'synthesis':'offline square-wave tone and 17-bit noise; analogue filter and envelope not emulated'},'assets':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(a.iterdir()) if p.is_file() and p.name!='manifest.json'}}
(a/'manifest.json').write_text(json.dumps(provenance,indent=2)+'\n')
print('PASS: disk hashes, 4 original files, 100 caves, boundaries, entrances/exits, original Z80 loading decoder match, 7 non-silent WAV files')
