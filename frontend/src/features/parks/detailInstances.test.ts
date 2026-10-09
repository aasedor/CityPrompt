import { describe, expect, it, vi } from "vitest";
import {
  BoxGeometry,
  Group,
  Mesh,
  MeshStandardMaterial,
  Matrix4,
  Vector3,
} from "three";
import { WGS84_ELLIPSOID } from "3d-tiles-renderer";
import {
  direct3DProposalUserData,
  getDirect3DProposalRole,
  getDirect3DInstanceDescriptor,
  isExcludedFromDirect3DCapture,
  requireDirect3DInstanceDescriptor,
} from "@/components/viewer/globe/direct3dCapture";
import {
  buildDetailInstances,
  detailPlacementMatrix,
  disposeDetailInstances,
} from "./detailInstances";

describe("batched project details", () => {
  it("keeps detail pixels in captures without claiming a zone-owned landscape instance", () => {
    const source = new Mesh(new BoxGeometry(), new MeshStandardMaterial());
    const details = buildDetailInstances(source, [new Matrix4(), new Matrix4().makeTranslation(3, 0, 0)]);
    const parent = new Group();
    parent.userData = direct3DProposalUserData("landscape");
    parent.add(details);
    const mesh = details.children[0];
    expect(isExcludedFromDirect3DCapture(mesh)).toBe(false);
    expect(getDirect3DProposalRole(mesh)).toBeNull();
    expect(getDirect3DInstanceDescriptor(mesh)).toBeNull();
    expect(() => requireDirect3DInstanceDescriptor(getDirect3DProposalRole(mesh), getDirect3DInstanceDescriptor(mesh))).not.toThrow();
    expect((mesh as import("three").InstancedMesh).count).toBe(2);
    disposeDetailInstances(details);
    source.geometry.dispose();
    source.material.dispose();
  });
  it("releases instance buffers without disposing shared geometry and materials", () => {
    const source = new Mesh(new BoxGeometry(), new MeshStandardMaterial());
    const geometry = vi.spyOn(source.geometry, "dispose");
    const material = vi.spyOn(source.material, "dispose");
    const group = buildDetailInstances(source, [new Matrix4()]);
    const instance = vi.spyOn(
      group.children[0] as import("three").InstancedMesh,
      "dispose",
    );
    disposeDetailInstances(group);
    expect(instance).toHaveBeenCalledOnce();
    expect(geometry).not.toHaveBeenCalled();
    expect(material).not.toHaveBeenCalled();
  });
  it("renders 100 copies with one draw object per source mesh and preserves source transforms", () => {
    const source = new Group();
    const mesh = new Mesh(new BoxGeometry(2, 1, 1), new MeshStandardMaterial());
    mesh.position.y = 0.5;
    source.add(mesh);
    const placements = Array.from({ length: 100 }, (_, i) =>
      new Matrix4().makeTranslation(i * 3, 0, 0),
    );
    const result = buildDetailInstances(source, placements);
    expect(result.children).toHaveLength(1);
    const batch = result.children[0] as import("three").InstancedMesh;
    expect(batch.count).toBe(100);
    expect(batch.geometry).toBe(mesh.geometry);
    expect(batch.material).toBe(mesh.material);
    const matrix = new Matrix4();
    batch.getMatrixAt(99, matrix);
    expect(new Vector3().setFromMatrixPosition(matrix).toArray()).toEqual([
      297, 0.5, 0,
    ]);
    const hits: unknown[] = [];
    batch.raycast({} as never, hits as never);
    expect(hits).toEqual([]);
    expect(batch.boundingSphere!.radius).toBeGreaterThan(140);
    expect(mesh.position.y).toBe(0.5);
  });
  it("matches individual ENU placement including elevation, rotation and ground anchor", () => {
    const origin = WGS84_ELLIPSOID.getEastNorthUpFrame(
      (51 * Math.PI) / 180,
      (-114 * Math.PI) / 180,
      1000,
      new Matrix4(),
    );
    const item = { lat: 51.0001, lng: -114.0002, height: 1003, angle: 30 };
    const actual = detailPlacementMatrix(
      item,
      origin.clone().invert(),
      [1, -2, 3],
    );
    const expected = WGS84_ELLIPSOID.getEastNorthUpFrame(
      (item.lat * Math.PI) / 180,
      (item.lng * Math.PI) / 180,
      item.height,
      new Matrix4(),
    )
      .multiply(new Matrix4().makeTranslation(0, 0, 0.084))
      .multiply(new Matrix4().makeRotationZ(Math.PI / 6))
      .multiply(new Matrix4().makeRotationX(Math.PI / 2))
      .multiply(new Matrix4().makeTranslation(1, -2, 3));
    const restored = origin.clone().multiply(actual);
    restored.elements.forEach((n, i) =>
      expect(n).toBeCloseTo(expected.elements[i], 7),
    );
  });
});
