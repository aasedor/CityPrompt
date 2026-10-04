import { Component, Suspense, useEffect, useMemo, type ReactNode } from 'react';
import { useGLTF } from '@react-three/drei';
import { EastNorthUpFrame } from '3d-tiles-renderer/r3f';
import type { SiteZone } from '@/types';
import { computeCentroid } from '../mapEngine/geoUtils';
import { centreNativeClayClone } from '@/features/legoAssembly/nativeClayPlacement';
import { rectangleDimensions } from '@/features/pickPlace/geometry';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import { resolveZoneTerrainHeight } from './globeTerrainUtils';
import { direct3DInstanceUserData, direct3DZoneInstanceDescriptor } from './direct3dCapture';
import { mountBuildingWalking, readBuildingWalking } from '@/features/legoAssembly/buildingWalking';
import * as THREE from 'three';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { useSharedSiteGround, useSharedSiteGroundVerification } from './SharedSiteGroundProvider';
import { preparedEntranceGround } from './preparedEntranceGround';
import { reviewBuildingFootprints, reviewBuildingGroundContact } from './reviewBuildingGround';
import { BuildingFoundationSurface } from './BuildingFoundationSurface';
import { retainResourceForDeferredDisposal } from './strictModeResourceDisposal';
import { prepareReviewBuildingGlass } from './reviewBuildingGlass';

type GroundReporter = (buildingId: string, rendererId: string, reason: string | null) => void;

function PendingGroundIssue({ zone, reason, report }: { zone: SiteZone; reason: string; report?: GroundReporter }) {
  const buildingId = zone.building_id || zone.id;
  const rendererId = `review:${zone.id}`;
  useEffect(() => {
    report?.(buildingId, rendererId, reason);
    return () => report?.(buildingId, rendererId, null);
  }, [buildingId, rendererId, reason, report]);
  return null;
}

/** Isolated local-review GLB. A bad candidate leaves a visible fallback and
 * never takes down the project view or another building. */
class ReviewBoundary extends Component<{ children: ReactNode; fallback: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? this.props.fallback : this.props.children; }
}

function BuildingGLB({ url, zone, zones, terrainHeight, onGroundingIssue }: {
  url: string; zone: SiteZone; zones: SiteZone[]; terrainHeight: number; onGroundingIssue?: GroundReporter;
}) {
  const { scene } = useGLTF(url);
  const preparedModel = useMemo(() => prepareReviewBuildingGlass(scene), [scene]);
  const model = useMemo(() => centreNativeClayClone(preparedModel.clone), [preparedModel]);
  useEffect(() => retainResourceForDeferredDisposal(preparedModel,
    value => value.ownedMaterials.forEach(material => material.dispose())), [preparedModel]);
  const [lng, lat] = computeCentroid(zone.coordinates);
  const yaw = rectangleDimensions(zone.coordinates).degrees * Math.PI / 180;
  const footprints = useMemo(() => reviewBuildingFootprints(scene, yaw), [scene, yaw]);
  const sharedGround = useSharedSiteGround();
  const verifiedGround = useSharedSiteGroundVerification();
  const boundary = getActiveSiteBoundary(zones);
  const preparedLevel = resolvePreparedSiteTerrainForZone(zone, zones, terrainHeight);
  const prepared = useMemo(() => preparedEntranceGround(boundary, preparedLevel), [boundary, preparedLevel]);
  const ground = sharedGround.status === 'inactive' && prepared ? prepared : verifiedGround;
  const displayGround = sharedGround.status === 'inactive' && prepared ? prepared : sharedGround;
  const contact = useMemo(() => reviewBuildingGroundContact(footprints, lng, lat, ground), [footprints, lng, lat, ground]);
  // Retain a coherent visible draft during tile refresh. Only the verification
  // contact above can authorize walking or clear a capture-blocking issue.
  const displayContact = useMemo(() => reviewBuildingGroundContact(footprints, lng, lat, displayGround),
    [footprints, lng, lat, displayGround]);
  const geometry = useMemo(() => {
    if (displayContact.status !== 'ready') return null;
    const result = new THREE.BufferGeometry();
    result.setAttribute('position', new THREE.Float32BufferAttribute(displayContact.positions, 3));
    result.setIndex(displayContact.indices);
    result.computeVertexNormals();
    result.computeBoundingSphere();
    return result;
  }, [displayContact]);
  useEffect(() => geometry ? retainResourceForDeferredDisposal(geometry, value => value.dispose()) : undefined, [geometry]);
  const buildingId = zone.building_id || zone.id;
  const rendererId = `review:${zone.id}`;
  const reason = contact.status === 'ready' ? null : contact.status === 'outside'
    ? 'incomplete_footprint_ground' : contact.reason ?? 'incomplete_footprint_ground';
  useEffect(() => {
    onGroundingIssue?.(buildingId, rendererId, reason);
    return () => onGroundingIssue?.(buildingId, rendererId, null);
  }, [buildingId, rendererId, reason, onGroundingIssue]);
  useEffect(() => {
    const source = model.children[0];
    if (contact.status !== 'ready' || !source) return;
    const walking = readBuildingWalking(source);
    if (walking) return mountBuildingWalking(rendererId, zone, source, walking);
  }, [model, zone, contact, rendererId]);
  const storedTerrain = Number(zone.properties?.terrain_elevation_m);
  const height = displayContact.status === 'ready' ? displayContact.anchorHeight : preparedLevel
    ?? resolveZoneTerrainHeight(null, Number.isFinite(storedTerrain) ? storedTerrain : null, terrainHeight);
  const userData = { reviewBuildingStatus: contact.status === 'ready' ? 'ready' : 'ground-unresolved',
    reviewBuildingGroundReason: reason, reviewBuildingGroundRevision: ground.revision,
    ...direct3DInstanceUserData(direct3DZoneInstanceDescriptor(zone.id, 'building',
      zone.building_id ? { building_id: zone.building_id } : {})) };
  return <EastNorthUpFrame lat={lat * Math.PI / 180} lon={lng * Math.PI / 180} height={height}>
    <group name={`review-building-${zone.id}`}>
      {geometry && <BuildingFoundationSurface geometry={geometry} renderOrder={150} userData={userData}/>}
      <group rotation={[0, 0, yaw]}>
        <group name="review-building-loaded" userData={userData}
          rotation={[Math.PI / 2, 0, 0]} dispose={null}><primitive object={model}/></group>
      </group>
    </group>
  </EastNorthUpFrame>;
}

export function GlobeReviewBuilding({ zone, zones, terrainHeight, onGroundingIssue }: {
  zone: SiteZone; zones: SiteZone[]; terrainHeight: number; onGroundingIssue?: GroundReporter;
}) {
  const url = String(zone.properties?.validation_native_url || '');
  const [lng, lat] = computeCentroid(zone.coordinates);
  const storedTerrain = Number(zone.properties?.terrain_elevation_m);
  const height = resolvePreparedSiteTerrainForZone(zone, zones, terrainHeight)
    ?? resolveZoneTerrainHeight(null, Number.isFinite(storedTerrain) ? storedTerrain : null, terrainHeight);
  if (!url || zone.coordinates.length < 4) return null;
  return <ReviewBoundary key={url} fallback={<>
    <PendingGroundIssue zone={zone} reason="review_model_unavailable" report={onGroundingIssue}/>
    <EastNorthUpFrame lat={lat * Math.PI / 180} lon={lng * Math.PI / 180} height={height}>
      <mesh name="review-building-error" userData={{ reviewBuildingStatus: 'error' }} position={[0, 0, 4]}>
        <boxGeometry args={[22, 14, 8]}/><meshBasicMaterial color="#e86a40" wireframe/>
      </mesh>
    </EastNorthUpFrame>
  </>}><Suspense fallback={<>
      <PendingGroundIssue zone={zone} reason="review_model_loading" report={onGroundingIssue}/>
      <EastNorthUpFrame lat={lat * Math.PI / 180} lon={lng * Math.PI / 180} height={height}>
        <mesh name="review-building-loading" userData={{ reviewBuildingStatus: 'loading' }} position={[0, 0, 4]}>
          <boxGeometry args={[22, 14, 8]}/><meshBasicMaterial color="#64748b" wireframe/>
        </mesh>
      </EastNorthUpFrame>
    </>}><BuildingGLB url={url} zone={zone} zones={zones} terrainHeight={terrainHeight}
      onGroundingIssue={onGroundingIssue}/></Suspense></ReviewBoundary>;
}
