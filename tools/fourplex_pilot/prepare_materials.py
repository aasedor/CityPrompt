"""Crop the reference-conditioned four-role atlas and derive bounded PBR maps.

Run: python tools/fourplex_pilot/prepare_materials.py ATLAS.png OUTPUT_DIR
All outputs are candidate evidence; keep them in ignored/external artifacts.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


source=Path(sys.argv[1]).resolve()
target=Path(sys.argv[2]).resolve()
target.mkdir(parents=True,exist_ok=True)
atlas=Image.open(source).convert("RGB")
w,h=atlas.size
roles={
    "dark_siding":(0,0,w//2,h//2),
    "white_lap":(w//2,0,w,h//2),
    "charcoal_brick":(0,h//2,w//2,h),
    "roof_shingle":(w//2,h//2,w,h),
}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

records={}
for role,box in roles.items():
    image=atlas.crop(box).resize((1024,1024),Image.Resampling.LANCZOS)
    pixels=np.array(image).astype(np.float32)
    # Make the bounded source specimen tile cleanly, without changing its centre.
    edge=20
    for i in range(edge):
        t=(edge-i)/edge*.5
        blend=(pixels[:,i].copy()+pixels[:,-edge+i].copy())/2
        pixels[:,i]=(1-t)*pixels[:,i]+t*blend
        pixels[:,-edge+i]=(1-t)*pixels[:,-edge+i]+t*blend
        blend=(pixels[i].copy()+pixels[-edge+i].copy())/2
        pixels[i]=(1-t)*pixels[i]+t*blend
        pixels[-edge+i]=(1-t)*pixels[-edge+i]+t*blend
    albedo=Image.fromarray(np.clip(pixels,0,255).astype(np.uint8),"RGB")
    albedo_path=target/f"{role}-albedo.png";albedo.save(albedo_path,optimize=True)
    gray=np.asarray(albedo.convert("L").filter(ImageFilter.GaussianBlur(1.2)),dtype=np.float32)/255
    gy,gx=np.gradient(gray)
    strength={"dark_siding":2.8,"white_lap":3.4,"charcoal_brick":3.0,"roof_shingle":1.8}[role]
    nx=-gx*strength;ny=-gy*strength;nz=np.ones_like(nx)
    norm=np.sqrt(nx*nx+ny*ny+nz*nz)
    normal=np.stack(((nx/norm*.5+.5)*255,(ny/norm*.5+.5)*255,(nz/norm*.5+.5)*255),axis=-1)
    normal_path=target/f"{role}-normal.png"
    Image.fromarray(np.clip(normal,0,255).astype(np.uint8),"RGB").save(normal_path,optimize=True)
    rough_base={"dark_siding":.82,"white_lap":.78,"charcoal_brick":.91,"roof_shingle":.94}[role]
    rough=np.clip((rough_base+(gray-gray.mean())*.085)*255,0,255).astype(np.uint8)
    rough_path=target/f"{role}-roughness.png"
    Image.fromarray(rough,"L").save(rough_path,optimize=True)
    ao=np.clip((.92+(gray-gray.mean())*.15)*255,0,255).astype(np.uint8)
    ao_path=target/f"{role}-ao.png"
    Image.fromarray(ao,"L").save(ao_path,optimize=True)
    records[role]={name:{"path":str(path),"bytes":path.stat().st_size,"sha256":sha(path)} for name,path in
                   (("albedo",albedo_path),("normal",normal_path),("roughness",rough_path),("ao",ao_path))}

(target/"manifest.json").write_text(json.dumps({"schema":"cityprompt.fourplex.materials@1",
    "source_atlas":{"path":str(source),"bytes":source.stat().st_size,"sha256":sha(source)},
    "method":"RLASM v6.1 source-photo-conditioned specimen atlas; orthographic role crops with deterministic edge feather and PBR derivatives",
    "roles":records},indent=2)+"\n",encoding="utf-8")
print(target/"manifest.json")
