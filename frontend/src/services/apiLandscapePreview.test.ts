import type { InternalAxiosRequestConfig } from "axios";
import { afterEach, expect, it, vi } from "vitest";
import { api } from "./api";
const originalAdapter = api.defaults.adapter;
afterEach(() => {
  api.defaults.adapter = originalAdapter;
  localStorage.clear();
});
it("returns signed landscape previews unchanged while still decorating ordinary assets", async () => {
  const project = "7e1e9037-b98c-4d18-8502-839160315869";
  const path = `/api/v1/files/projects/${project}/landscape/1234.png`;
  const signed = {
    preview: { project_id: project, recipe: { surface_image_url: path } },
    signature: "signed",
  };
  localStorage.setItem(
    "access_token",
    `header.${btoa(JSON.stringify({ sub: "student", type: "access" }))}.signature`,
  );
  const adapter = vi.fn(async (config: InternalAxiosRequestConfig) => ({
    data: config.url?.endsWith("asset-ticket")
      ? { asset_ticket: "temporary", expires_in: 900 }
      : structuredClone(signed),
    status: 200,
    statusText: "OK",
    headers: {},
    config,
  }));
  api.defaults.adapter = adapter;
  expect(
    (await api.post("/api/v1/site-landscape/boundary/preview", {})).data,
  ).toEqual(signed);
  expect(adapter).toHaveBeenCalledTimes(1);
  const decorated = (
    await api.get(`/api/v1/projects/${project}/ordinary-asset`)
  ).data;
  expect(decorated.preview.recipe.surface_image_url).toContain(
    "asset_ticket=temporary",
  );
});
