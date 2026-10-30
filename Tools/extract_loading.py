#!/usr/bin/env python3
"""Decode DASHIII.ECR's own two-run RLE (Z80 routine at file offset 0).
Palette comes from firmware BC32 calls in DASHIII.PAR, not from gameplay.
"""
from pathlib import Path
import json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'Extracted/DASHIII.ECR').read_bytes()
# The original decoder sets IX=entry+0x39, then reads two run values
# at IX+1 and IX+2. IX starts six bytes before its stream because it
# pops the return address after the two firmware calls (entry+6).
pos=0x3f
screen=bytearray()
while len(screen)<16384:
    control,a,b=src[pos:pos+3];pos+=3
    screen.extend(bytes([a])*((control>>4)+1))
    screen.extend(bytes([b])*((control&15)+1))
assert len(screen)>=16384
screen=screen[:16384]
(ROOT/'assets/loading-screen.bin').write_bytes(screen)
# CPC firmware ink order: RGB levels 0,128,255.
fw=[(0,0,0),(0,0,128),(0,0,255),(128,0,0),(128,0,128),(128,0,255),
    (255,0,0),(255,0,128),(255,0,255),(0,128,0),(0,128,128),(0,128,255),
    (128,128,0),(128,128,128),(128,128,255),(255,128,0),(255,128,128),(255,128,255),
    (0,255,0),(0,255,128),(0,255,255),(128,255,0),(128,255,128),(128,255,255),
    (255,255,0),(255,255,128),(255,255,255)]
par=(ROOT/'Extracted/DASHIII.PAR').read_bytes();inks=[0]*16
# First ink is set using XOR A, subsequent ones use LD A,n.
inks[0]=par[9]
for i in range(len(par)-9):
    if par[i]==0x3e and par[i+2]==1 and par[i+5:i+8]==b'\xcd\x32\xbc':
        inks[par[i+1]]=par[i+3]
im=Image.new('RGB',(640,400))
for y in range(200):
    for x in range(80):
        v=screen[(y%8)*2048+(y//8)*80+x]
        # MODE 0 selected by XOR A / CALL BC1C in DASHIII.PAR.
        cols=[((v>>7)&1)|((v>>2)&2)|((v>>3)&4)|((v<<2)&8),
              ((v>>6)&1)|((v>>1)&2)|((v>>2)&4)|((v<<3)&8)]
        for q,col in enumerate(cols):
            for xx in range(4):
                for yy in range(2):im.putpixel((x*8+q*4+xx,y*2+yy),fw[inks[col]])
im.save(ROOT/'assets/loading.png')
(ROOT/'assets/loading-palette.json').write_text(json.dumps({'firmwareInks':inks,'source':'DASHIII.PAR','mode':0,'rleOffset':63,'consumedBytes':pos},indent=2)+'\n')
print(f'Loading screen: {pos} of {len(src)} bytes consumed, inks {inks[:7]}')
