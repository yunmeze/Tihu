"""Regenerate derived Godot JSON from archived final NPZ meshes; no engine invoked."""
from pathlib import Path
import json,numpy as np
O=Path(__file__).resolve().parent;R=O.parent
frames=[]
for phase in range(57,63):
 folder=R/('south-walk-arap-cpu-v1' if phase==59 else f'south-walk-arap{phase}-cpu-v1')
 kind='collision' if phase in (57,59,61) else 'orientation'
 mesh=np.load(folder/f'render_{kind}_safe{phase}.npz')
 frames.append({'phase':phase,'texture':str(R/f'south-walk-mesh-correction-v1/raw/{phase}.png'),'vertices':mesh['vertices'].tolist(),'uv':mesh['uv'].tolist(),'triangles':mesh['triangles'].tolist(),'output':str(O/f'output/mesh-{phase}.png')})
(O/'project/mesh.json').write_text(json.dumps(frames,separators=(',',':')))
