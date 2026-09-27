"""Recover source-authored street markings/edging independently of rigid kits.

Run in Blender, one locked package per process. Original files are never edited.
Ground regions and kit poses remain from the reviewed recipe. Only the source
builder's small non-kit meshes are recorded for route-aligned reconstruction.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import bpy
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.output.exists():raise ValueError('Use a new extraction output')
    source=json.loads((args.source/'recipe.json').read_text())
    if source['kind'] not in ('cycle_avenue','green_alley','school_street'):
        raise ValueError('Outside the finite three-street initiative')
    kit=Path(source['kit_source']['path'])
    if digest(kit)!=source['kit_source']['sha256']:raise ValueError('Source kit changed')
    if digest(args.source/source['assembly']['path'])!=source['assembly']['sha256']:
        raise ValueError('Source assembly changed')
    # Import each package's preserved authoring version, never a newer sibling.
    sys.path.insert(0,str(args.source))
    builder=importlib.import_module('build_street_batch')
    S,F=builder.S,builder.F
    S.init(kit);F.init();S.paving=builder.patterned_paving(source['pattern'])
    rigid=set();original_kit=S.kit
    def placed(*a,**kw):
        objects=original_kit(*a,**kw);rigid.update(o.as_pointer() for o in objects);return objects
    S.kit=placed
    recipe=builder.validate(builder.recipe(source['kind']))
    builder.make(recipe)
    bpy.context.view_layer.update()
    groups={}
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH' or obj.as_pointer() in rigid:continue
        obj.data.calc_loop_triangles()
        for tri in obj.data.loop_triangles:
            mat=obj.data.materials[tri.material_index]
            group=groups.setdefault(mat.name,dict(material=mat.name,positions=[],indices=[]))
            first=len(group['positions'])//3
            for vi in tri.vertices:group['positions'].extend(round(float(v),7) for v in obj.matrix_world@obj.data.vertices[vi].co)
            group['indices'].extend([first,first+1,first+2])
    palette={name:list(mat.diffuse_color[:3]) for name,mat in S.MATS.items() if name!='kit'}
    for name in groups:palette[name]=list(bpy.data.materials[name].diffuse_color[:3])
    scripts={p.name:digest(p) for p in args.source.glob('*.py')}
    width,length=source['dimensions_m']
    program=dict(schemaVersion=1,adapter='classroom-source-street-v1',sourceFiles=scripts,
        surfaceRegions=source['surface_regions'],details=[],meshDetails=list(groups.values()),
        paving=source['pattern'],pavingModuleM=[.48,.24] if source['pattern']=='brick' else [1.2,.8],
        minLengthM=length,maxLengthM=480,preparedLevelOnly=True,baseLiftM=.025,palette=palette)
    output=dict(sourceRecipeSha256=digest(args.source/'recipe.json'),sourceAssemblySha256=source['assembly']['sha256'],
        program=program,detailTriangleCount=sum(len(g['indices'])//3 for g in groups.values()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2)+'\n')
    print('EXTRACTED_SOURCE_DETAILS',source['id'],output['detailTriangleCount'])


if __name__=='__main__':main()
