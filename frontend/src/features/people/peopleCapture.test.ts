import { describe, expect, it, vi } from 'vitest';
import { Group } from 'three';
import { beginPeopleCapture, PEOPLE_CAPTURE_KEY, renderPeopleCaptureFrame } from './peopleCapture';

describe('people capture scope', () => {
  it('poses visible authored actors at absolute time and restores even after a failed pass', () => {
    const scene = new Group(), actor = new Group(), hidden = new Group();
    const active = { pose: vi.fn(), restore: vi.fn() };
    const inactive = { pose: vi.fn(), restore: vi.fn() };
    actor.userData[PEOPLE_CAPTURE_KEY] = active;
    hidden.userData[PEOPLE_CAPTURE_KEY] = inactive; hidden.visible = false;
    scene.add(actor, hidden);
    const capture = beginPeopleCapture(scene, true);
    expect(capture.count).toBe(1);
    try { capture.pose(2); capture.pose(0); throw new Error('pass failed'); }
    catch { /* normal capture finally still restores */ }
    finally { capture.restore(); capture.restore(); }
    expect(active.pose.mock.calls).toEqual([[2], [0]]);
    expect(active.restore).toHaveBeenCalledOnce();
    expect(inactive.pose).not.toHaveBeenCalled();
  });
  it('keeps normal editing still and rejects invalid capture time before touching actors', () => {
    const scene = new Group(); const pose = vi.fn();
    scene.userData[PEOPLE_CAPTURE_KEY] = { pose, restore: vi.fn() };
    const disabled = beginPeopleCapture(scene, false);
    disabled.pose(2); expect(disabled.count).toBe(0); expect(pose).not.toHaveBeenCalled();
    expect(() => beginPeopleCapture(scene, true).pose(NaN)).toThrow(/time/);
  });
  it('resolves replacement rigs by stable detail ID and rejects actual membership changes', () => {
    const scene = new Group(), first = new Group(), replacement = new Group();
    first.userData.projectDetailId = replacement.userData.projectDetailId = 'saved-person';
    const a = { pose: vi.fn(), restore: vi.fn() }, b = { pose: vi.fn(), restore: vi.fn() };
    first.userData[PEOPLE_CAPTURE_KEY] = a; replacement.userData[PEOPLE_CAPTURE_KEY] = b;
    scene.add(first); const capture = beginPeopleCapture(scene, true);
    scene.remove(first); scene.add(replacement); capture.pose(3);
    expect(a.pose).not.toHaveBeenCalled(); expect(b.pose).toHaveBeenCalledWith(3);
    scene.remove(replacement);
    expect(() => capture.pose(3)).toThrow(/changed during capture/);
    capture.restore(); expect(a.restore).toHaveBeenCalledOnce();
  });
  it('reapplies pose after an awaited terrain update before the encoded draw', async () => {
    const scene = new Group(), first = new Group(), replacement = new Group();
    first.userData.projectDetailId = replacement.userData.projectDetailId = 'person';
    let renderedTime = -1, cameraTime = -1;
    first.userData[PEOPLE_CAPTURE_KEY] = { pose: vi.fn(), restore: vi.fn() };
    replacement.userData[PEOPLE_CAPTURE_KEY] = { pose: (time: number) => { renderedTime = time; }, restore: vi.fn() };
    scene.add(first); const scope = beginPeopleCapture(scene, true);
    await renderPeopleCaptureFrame(scope, 3.5, () => { cameraTime = renderedTime; },
      async () => { scene.remove(first); scene.add(replacement); },
      () => { expect(renderedTime).toBe(3.5); expect(cameraTime).toBe(3.5); });
  });
});
