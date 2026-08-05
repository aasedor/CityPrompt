export type SharedParkEquipmentId =
  | 'basketball_hoop_regulation'
  | 'picnic_table_accessible'
  | 'dual_stream_bin'
  | 'bike_rack_three_stall'
  | 'drinking_fountain_accessible';

export interface SharedParkEquipmentAsset {
  id: SharedParkEquipmentId;
  url: string;
  targetHeightM: number;
  footprintM: { width: number; depth: number };
  clearanceM: number;
  placementAnchor: 'post_base' | 'assembly_center';
  maxTriangles: number;
}

const ROOT = '/park-kits/shared-park-equipment-v1';

/** Reviewed, metric park objects shared across archetype families. Program
 * logic owns placement; this catalog owns geometry, scale, and clearance. */
export const SHARED_PARK_EQUIPMENT: Record<SharedParkEquipmentId, SharedParkEquipmentAsset> = {
  basketball_hoop_regulation: {
    id: 'basketball_hoop_regulation',
    url: `${ROOT}/basketball-hoop-regulation.glb`,
    targetHeightM: 3.95,
    footprintM: { width: 2.037, depth: 1.82 },
    clearanceM: 2,
    placementAnchor: 'post_base',
    maxTriangles: 2000,
  },
  picnic_table_accessible: {
    id: 'picnic_table_accessible',
    url: `${ROOT}/picnic-table-accessible.glb`,
    targetHeightM: 0.78,
    footprintM: { width: 2.76, depth: 1.73 },
    clearanceM: 0.9,
    placementAnchor: 'assembly_center',
    maxTriangles: 3500,
  },
  dual_stream_bin: {
    id: 'dual_stream_bin',
    url: `${ROOT}/dual-stream-bin.glb`,
    targetHeightM: 1.08,
    footprintM: { width: 0.84, depth: 0.537 },
    clearanceM: 0.55,
    placementAnchor: 'assembly_center',
    maxTriangles: 1000,
  },
  bike_rack_three_stall: {
    id: 'bike_rack_three_stall',
    url: `${ROOT}/bike-rack-three-stall.glb`,
    targetHeightM: 0.861,
    footprintM: { width: 1.946, depth: 0.15 },
    clearanceM: 1.25,
    placementAnchor: 'assembly_center',
    maxTriangles: 1500,
  },
  drinking_fountain_accessible: {
    id: 'drinking_fountain_accessible',
    url: `${ROOT}/drinking-fountain-accessible.glb`,
    targetHeightM: 1.04,
    footprintM: { width: 0.925, depth: 0.68 },
    clearanceM: 0.9,
    placementAnchor: 'assembly_center',
    maxTriangles: 1000,
  },
};
