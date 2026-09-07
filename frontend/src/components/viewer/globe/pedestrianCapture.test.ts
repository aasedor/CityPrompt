import { describe, expect, it } from 'vitest';
import { Group, Object3D } from 'three';
import { pedestrianCaptureUserData } from './pedestrianCapture';
import { direct3DProposalUserData, getDirect3DInstanceDescriptor, getDirect3DProposalRole } from './direct3dCapture';

describe('pedestrian capture ownership',()=>{
  it('keeps street semantics under a differently labelled parent and retains the source owner',()=>{
    const parent=new Group(),connection=new Group(),mesh=new Object3D();
    parent.userData=direct3DProposalUserData('park');
    connection.userData=pedestrianCaptureUserData('house');
    parent.add(connection);connection.add(mesh);
    expect(getDirect3DProposalRole(mesh)).toBe('street');
    expect(getDirect3DInstanceDescriptor(mesh)).toMatchObject({semantic_class:'street',zone_id:'house'});
  });
});
