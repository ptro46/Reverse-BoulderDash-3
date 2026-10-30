#!/usr/bin/env python3
"""Render an app icon from the extracted CPC player/diamond, nearest pixels."""
from pathlib import Path
from PIL import Image, ImageDraw
import struct
r=Path(__file__).resolve().parents[1]
a=Image.open(r/'assets/sprites.png').convert('RGB')
im=Image.new('RGB',(1024,1024),(9,23,29));d=ImageDraw.Draw(im)
d.rounded_rectangle((48,48,976,976),radius=180,fill=(22,43,57),outline=(0,210,255),width=20)
player=a.crop((64*16,0,65*16,16)).resize((576,576),Image.Resampling.NEAREST)
im.paste(player,(224,224))
diamond=a.crop((20*16,16,21*16,32)).resize((192,192),Image.Resampling.NEAREST)
im.paste(diamond,(704,704))
im.save(r/'assets/icon.png')
# PNG-backed icns slots; no macOS-only tools needed for source generation.
chunks=[]
for code,size in [(b'icp4',16),(b'icp5',32),(b'icp6',64),(b'ic07',128),(b'ic08',256),(b'ic09',512),(b'ic10',1024)]:
    import io
    out=io.BytesIO();im.resize((size,size),Image.Resampling.LANCZOS).save(out,format='PNG');b=out.getvalue()
    chunks.append(code+struct.pack('>I',len(b)+8)+b)
b=b''.join(chunks);(r/'assets/BoulderDashIII.icns').write_bytes(b'icns'+struct.pack('>I',len(b)+8)+b)
