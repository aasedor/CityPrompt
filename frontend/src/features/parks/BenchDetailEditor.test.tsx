import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { SiteZone } from "@/types";
import { rectangleAt } from "@/features/pickPlace/geometry";
import { BenchDetailControls, BenchLayoutEditor } from "./BenchDetailEditor";
import { projectBenchContext, projectBenchFrame } from "./projectBenches";
const zone = {
  id: "park",
  project_id: "trial",
  color: "#769952",
  sort_order: 0,
  created_at: "2026-10-08",
  updated_at: "2026-10-08",
  name: "Trial park",
  zone_type: "green_space",
  coordinates: rectangleAt([-114, 51], 70, 55),
  properties: {
    green_space_archetype_id: "neighborhood_park",
    green_space_selected_variant_id: "neighborhood_park_v0",
    neighborhood_park_layout: "adaptive_rustic_v1",
  },
} as SiteZone;
describe("isolated bench editor", () => {
  it("draws paving beneath details, undoes removal and saves both in the same draft", async () => {
    const onSave = vi.fn().mockResolvedValue({});
    const context = projectBenchContext(projectBenchFrame([], []));
    const benches = [{ id: "bench", point: { x: 5, y: 5 }, yaw: 0 }];
    render(
      <BenchLayoutEditor
        context={context}
        initialBenches={benches}
        title="Paving trial"
        disabled={false}
        onSave={onSave}
        onClose={vi.fn()}
      />,
    );
    const plan = screen.getByRole("group", { name: "Detail layout plan" });
    Object.defineProperty(plan, "getScreenCTM", {
      value: () => ({ inverse: () => ({}) }),
    });
    vi.stubGlobal("PointerEvent", MouseEvent);
    vi.stubGlobal(
      "DOMPoint",
      class {
        constructor(
          public x: number,
          public y: number,
        ) {}
        matrixTransform() {
          return this;
        }
      },
    );
    try {
      fireEvent.click(screen.getByRole("button", { name: "Draw paved area" }));
      for (const [x, y] of [
        [0, 0],
        [20, 0],
        [20, -20],
        [0, -20],
      ])
        fireEvent.pointerDown(plan, { clientX: x, clientY: y });
      fireEvent.click(screen.getByRole("button", { name: "Finish paving" }));
      expect(
        screen.getByRole("button", { name: "Select paving 1" }),
      ).toBeInTheDocument();
      fireEvent.change(screen.getByLabelText("Paving material"), {
        target: { value: "brick" },
      });
      fireEvent.click(
        screen.getByRole("button", { name: "Remove paved area" }),
      );
      expect(
        screen.queryByRole("button", { name: "Select paving 1" }),
      ).not.toBeInTheDocument();
      fireEvent.click(screen.getByRole("button", { name: "Undo detail edit" }));
      fireEvent.click(screen.getByRole("button", { name: "Save details" }));
      await waitFor(() => expect(onSave).toHaveBeenCalledOnce());
      expect(onSave.mock.calls[0][0]).toEqual(benches);
      expect(onSave.mock.calls[0][1][0]).toMatchObject({
        material: "brick",
        coordinates: [
          [0, 0],
          [20, 0],
          [20, 20],
          [0, 20],
        ].map(([x, y]) => context.toWorld({ x, y })),
      });
    } finally {
      vi.unstubAllGlobals();
    }
  });
  it("keeps the moving detail selected when the destination hits another marker", () => {
    const context = projectBenchContext(projectBenchFrame([], []));
    render(
      <BenchLayoutEditor
        context={context}
        initialBenches={[
          { id: "one", point: { x: 10, y: 0 }, yaw: 0 },
          { id: "two", point: { x: 0, y: 0 }, yaw: 0 },
        ]}
        title="Move trial"
        disabled={false}
        onSave={vi.fn()}
        onClose={vi.fn()}
      />,
    );
    const first = screen.getByRole("button", { name: "Select bench 1" });
    const second = screen.getByRole("button", { name: "Select bench 2" });
    Object.defineProperty(
      screen.getByRole("group", { name: "Detail layout plan" }),
      "getScreenCTM",
      { value: () => null },
    );
    second.setPointerCapture = vi.fn();
    fireEvent.click(first);
    fireEvent.click(screen.getByRole("button", { name: "Move on plan" }));
    fireEvent.pointerDown(second);
    fireEvent.click(second);
    expect(first).toHaveAttribute("aria-pressed", "true");
    expect(second).toHaveAttribute("aria-pressed", "false");
    expect(
      screen.getByRole("button", { name: "Move on plan" }),
    ).toHaveAttribute("aria-pressed", "true");
  });
  it("searches the catalogue and adds, moves and saves a standalone picnic table", async () => {
    const onSave = vi.fn().mockResolvedValue({});
    render(
      <BenchLayoutEditor
        context={projectBenchContext(projectBenchFrame([], []))}
        initialBenches={[]}
        title="Furniture trial"
        disabled={false}
        onSave={onSave}
        onClose={vi.fn()}
      />,
    );
    fireEvent.change(screen.getByLabelText("Search detail catalogue"), {
      target: { value: "picnic" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Add object" }));
    fireEvent.click(screen.getByRole("button", { name: "Move object east" }));
    fireEvent.click(screen.getByRole("button", { name: "Save details" }));
    await waitFor(() => expect(onSave).toHaveBeenCalledOnce());
    expect(onSave.mock.calls[0][0][0].propVariant).toBe(
      "picnic-table-accessible",
    );
  });
  it("adds an oak tree, moves it, undoes removal and saves its model choice", async () => {
    const onSave = vi.fn().mockResolvedValue({});
    render(
      <BenchLayoutEditor
        context={projectBenchContext(projectBenchFrame([], []))}
        initialBenches={[]}
        title="Tree trial"
        disabled={false}
        onSave={onSave}
        onClose={vi.fn()}
      />,
    );
    fireEvent.change(screen.getByLabelText("Detail model"), {
      target: { value: "oak-2" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Add tree" }));
    fireEvent.click(screen.getByRole("button", { name: "Move tree east" }));
    fireEvent.click(screen.getByRole("button", { name: "Remove tree" }));
    expect(
      screen.queryByRole("button", { name: /^Select tree / }),
    ).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Undo detail edit" }));
    fireEvent.click(screen.getByRole("button", { name: "Save details" }));
    await waitFor(() => expect(onSave).toHaveBeenCalledOnce());
    expect(onSave.mock.calls[0][0][0].treeVariant).toBe("oak-2");
  });
  it("adds and moves an independent bench without any site or archetype and saves the draft", async () => {
    const onSave = vi.fn().mockResolvedValue({});
    const onClose = vi.fn();
    render(
      <BenchLayoutEditor
        context={projectBenchContext(projectBenchFrame([], []))}
        initialBenches={[]}
        title="Empty project"
        disabled={false}
        onSave={onSave}
        onClose={onClose}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Add bench" }));
    fireEvent.click(screen.getByRole("button", { name: "Move bench east" }));
    fireEvent.click(screen.getByRole("button", { name: "Remove bench" }));
    expect(
      screen.queryByRole("button", { name: /^Select bench / }),
    ).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Undo detail edit" }));
    fireEvent.click(screen.getByRole("button", { name: "Save details" }));
    await waitFor(() => expect(onClose).toHaveBeenCalledOnce());
    expect(onSave.mock.calls[0][0]).toHaveLength(1);
  });
  it("pauses scene editing, keeps focus after keyboard deletion and restores the scene on close", () => {
    const onEditingChange = vi.fn();
    const root = document.createElement("div");
    root.id = "root";
    document.body.append(root);
    render(
      <BenchDetailControls
        zone={zone}
        disabled={false}
        onSave={vi.fn()}
        onEditingChange={onEditingChange}
      />,
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Edit details · benches" }),
    );
    expect(onEditingChange).toHaveBeenLastCalledWith(true);
    expect(root).toHaveAttribute("inert");
    const before = screen.getAllByRole("button", {
      name: /^Select bench /,
    }).length;
    fireEvent.click(
      screen.getAllByRole("button", { name: /^Select bench / })[0],
    );
    fireEvent.keyDown(screen.getByRole("dialog"), { key: "Delete" });
    expect(
      screen.getAllByRole("button", { name: /^Select bench / }),
    ).toHaveLength(before - 1);
    expect(screen.getByRole("dialog")).toHaveFocus();
    fireEvent.keyDown(screen.getByRole("dialog"), { key: "z", ctrlKey: true });
    expect(
      screen.getAllByRole("button", { name: /^Select bench / }),
    ).toHaveLength(before);
    fireEvent.keyDown(screen.getByRole("dialog"), { key: "Escape" });
    expect(onEditingChange).toHaveBeenLastCalledWith(false);
    expect(root).not.toHaveAttribute("inert");
    root.remove();
  });
  it("exposes bench selection only inside the editor and keeps unsaved removal reversible", () => {
    const onSave = vi.fn();
    render(
      <BenchDetailControls zone={zone} disabled={false} onSave={onSave} />,
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    fireEvent.click(
      screen.getByRole("button", { name: "Edit details · benches" }),
    );
    const before = screen.getAllByRole("button", {
      name: /^Select bench /,
    }).length;
    fireEvent.click(
      screen.getAllByRole("button", { name: /^Select bench / })[0],
    );
    fireEvent.click(screen.getByRole("button", { name: "Remove bench" }));
    expect(
      screen.getAllByRole("button", { name: /^Select bench / }),
    ).toHaveLength(before - 1);
    fireEvent.click(screen.getByRole("button", { name: "Undo detail edit" }));
    expect(
      screen.getAllByRole("button", { name: /^Select bench / }),
    ).toHaveLength(before);
    fireEvent.click(
      screen.getByRole("button", { name: "Close detail editor" }),
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(onSave).not.toHaveBeenCalled();
  });
  it("adds, moves and saves benches through the existing zone save callback", async () => {
    const onSave = vi.fn().mockResolvedValue({});
    render(
      <BenchDetailControls zone={zone} disabled={false} onSave={onSave} />,
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Edit details · benches" }),
    );
    fireEvent.click(screen.getByRole("button", { name: "Add bench" }));
    fireEvent.click(screen.getByRole("button", { name: "Move bench east" }));
    fireEvent.click(screen.getByRole("button", { name: "Save details" }));
    await waitFor(() => expect(onSave).toHaveBeenCalledTimes(1));
    expect(
      onSave.mock.calls[0][0].bench_details.items.some((b: { id: string }) =>
        b.id.startsWith("bench-"),
      ),
    ).toBe(true);
  });
  it("retains the draft if saving fails", async () => {
    render(
      <BenchDetailControls
        zone={zone}
        disabled={false}
        onSave={vi.fn().mockRejectedValue(new Error("offline"))}
      />,
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Edit details · benches" }),
    );
    fireEvent.click(screen.getByRole("button", { name: "Add bench" }));
    fireEvent.click(screen.getByRole("button", { name: "Save details" }));
    expect(await screen.findByText(/Could not save/)).toBeInTheDocument();
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });
});
