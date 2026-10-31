import { describe, expect, it, vi } from 'vitest';
import { assetAccountIdentity, createAssetAccess } from './assetAccess';

function token(subject: string, version = 1, type = 'access') {
  return `header.${btoa(JSON.stringify({ sub: subject, type, exp: version })).replace(/=/g, '')}.signature-${version}`;
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

function setup() {
  const projectTicket = vi.fn().mockResolvedValue({ asset_ticket: 'project-read', expires_in: 900 });
  const fileTicket = vi.fn().mockResolvedValue({ file_ticket: 'one-file', expires_in: 900 });
  let session: string | null = token('account-a');
  const access = createAssetAccess({ baseUrl: '', origin: () => 'https://cityprompt.ca', session: () => assetAccountIdentity(session), projectTicket, fileTicket });
  return { access, projectTicket, fileTicket, getToken: () => session!,
    setToken: (next: string | null) => { session = next; },
    logout: () => { session = null; access.clear(); },
  };
}
describe('scoped media downloads', () => {
  it('rejects a canceled consumer without aborting another consumer of the shared ticket', async () => {
    const { access, projectTicket } = setup();
    const response = deferred<{ asset_ticket: string; expires_in: number }>();
    let ticketSignal: AbortSignal | undefined;
    projectTicket.mockImplementation((_id: string, signal?: AbortSignal) => {
      ticketSignal = signal;
      return response.promise;
    });
    const firstController = new AbortController();
    const data = { image_url: '/api/v1/files/projects/shared/renders/a.png' };
    let firstState = 'pending';
    const first = access.prepare(data, undefined, firstController.signal).then(
      () => { firstState = 'resolved'; }, error => { firstState = error.name; },
    );
    const second = access.prepare(data);
    try {
      firstController.abort();
      await vi.waitFor(() => expect(firstState).toBe('AbortError'));
      expect(projectTicket).toHaveBeenCalledOnce();
      expect(ticketSignal?.aborted).toBe(false);
    } finally {
      response.resolve({ asset_ticket: 'shared-ticket', expires_in: 900 });
      await first;
    }
    expect((await second).image_url).toContain('asset_ticket=shared-ticket');
  });

  it('cancels an abandoned ticket and keeps its late completion from replacing or deleting a new request', async () => {
    const { access, projectTicket } = setup();
    const old = deferred<{ asset_ticket: string; expires_in: number }>();
    const current = deferred<{ asset_ticket: string; expires_in: number }>();
    const signals: Array<AbortSignal | undefined> = [];
    projectTicket.mockImplementationOnce((_id: string, signal?: AbortSignal) => { signals.push(signal); return old.promise; })
      .mockImplementationOnce((_id: string, signal?: AbortSignal) => { signals.push(signal); return current.promise; });
    const data = { image_url: '/api/v1/files/projects/shared/renders/a.png' };
    const controllers = [new AbortController(), new AbortController()];
    const abandoned = controllers.map(controller => access.prepare(data, undefined, controller.signal).catch(error => error));
    try {
      controllers.forEach(controller => controller.abort());
      expect(signals[0]?.aborted).toBe(true);
      const replacement = access.prepare(data);
      expect(projectTicket).toHaveBeenCalledTimes(2);
      old.resolve({ asset_ticket: 'abandoned-ticket', expires_in: 900 });
      await Promise.all(abandoned);
      expect(access.resolve(data.image_url)).not.toContain('abandoned-ticket');
      const sameReplacement = access.prepare(data);
      expect(projectTicket).toHaveBeenCalledTimes(2);
      current.resolve({ asset_ticket: 'current-ticket', expires_in: 900 });
      expect((await replacement).image_url).toContain('asset_ticket=current-ticket');
      expect((await sameReplacement).image_url).toContain('asset_ticket=current-ticket');
    } finally {
      old.resolve({ asset_ticket: 'abandoned-ticket', expires_in: 900 });
      current.resolve({ asset_ticket: 'current-ticket', expires_in: 900 });
      await Promise.all(abandoned);
    }
  });

  it('aborts project and file tickets and never starts the remaining queued scopes', async () => {
    const { access, projectTicket, fileTicket } = setup();
    const response = deferred<{ asset_ticket: string; file_ticket: string; expires_in: number }>();
    const signals: Array<AbortSignal | undefined> = [];
    const request = (_path: string, signal?: AbortSignal) => { signals.push(signal); return response.promise; };
    projectTicket.mockImplementation(request); fileTicket.mockImplementation(request);
    const controller = new AbortController();
    let state = 'pending';
    const pending = access.prepare(Array.from({length:12}, (_, index) => ({image_url:index % 2
      ? `/api/v1/files/library/${index}.glb` : `/api/v1/files/projects/${index}/renders/a.png`,
    })), undefined, controller.signal).then(() => { state = 'resolved'; }, error => { state = error.name; });
    try {
      expect(signals).toHaveLength(6);
      controller.abort();
      await vi.waitFor(() => expect(state).toBe('AbortError'));
      expect(signals.every(signal => signal?.aborted)).toBe(true);
    } finally {
      response.resolve({ asset_ticket:'project', file_ticket:'file', expires_in:900 });
      await pending;
    }
    expect(signals).toHaveLength(6);
    await access.refresh();
    expect(signals).toHaveLength(6);
  });

  it('does not start ticket requests for an already canceled preparation', async () => {
    const { access, projectTicket } = setup();
    const controller = new AbortController();
    controller.abort();
    await expect(access.prepare({image_url:'/api/v1/files/projects/p/renders/a.png'}, undefined, controller.signal))
      .rejects.toMatchObject({name:'AbortError'});
    expect(projectTicket).not.toHaveBeenCalled();
  });

  it('discards private tickets and keeps public media usable when session storage becomes inaccessible', async () => {
    const session = vi.fn<() => string | null>().mockReturnValue('account-a');
    const projectTicket = vi.fn().mockResolvedValue({ asset_ticket: 'private-ticket', expires_in: 900 });
    const access = createAssetAccess({ baseUrl: '', origin: () => 'https://cityprompt.ca', session,
      projectTicket, fileTicket: vi.fn() });
    const url = '/api/v1/files/projects/p/renders/a.png';
    const saved = await access.prepare({ image_url: url });
    expect(saved.image_url).toContain('asset_ticket=private-ticket');
    const listener = vi.fn();
    access.subscribe(listener);
    session.mockImplementation(() => { throw new DOMException('Blocked', 'SecurityError'); });
    await expect(access.refresh()).resolves.toBeUndefined();
    expect(listener).toHaveBeenCalledOnce();
    expect(access.resolve(saved.image_url)).toBe(url);
    expect(access.resolve(url, { shareToken: 'public-share' })).toContain('share_token=public-share');
    expect(await access.prepare({ image_url: url })).toEqual({ image_url: url });
    expect(projectTicket).toHaveBeenCalledOnce();
    session.mockReturnValue('account-a');
    projectTicket.mockResolvedValue({ asset_ticket: 'fresh-ticket', expires_in: 900 });
    const recovered = await access.prepare({ image_url: url });
    expect(recovered.image_url).toContain('asset_ticket=fresh-ticket');
    expect(recovered.image_url).not.toContain('private-ticket');
    expect(projectTicket).toHaveBeenCalledTimes(2);
  });
  it('prepares one ticket for multiple project assets without putting the login token in URLs', async () => {
    const { access, projectTicket, getToken } = setup();
    const result = await access.prepare({ images: ['/api/v1/files/projects/p/renders/a.png', '/api/v1/files/projects/p/renders/b.png'] });
    expect(projectTicket).toHaveBeenCalledTimes(1);
    expect(result.images.every((url) => url.includes('asset_ticket=project-read'))).toBe(true);
    expect(JSON.stringify(result)).not.toContain(getToken());
  });
  it('does not send credentials to third-party URLs that resemble the file API', async () => {
    const { access, projectTicket, fileTicket } = setup();
    const remote = 'https://outside.example/api/v1/files/projects/p/secret.png';
    expect(await access.prepare({ image_url: remote })).toEqual({ image_url: remote });
    expect(access.resolve(remote, { shareToken: 'public-secret' })).toBe(remote);
    expect(projectTicket).not.toHaveBeenCalled(); expect(fileTicket).not.toHaveBeenCalled();
  });
  it('uses exact-file tickets for a private library and public tokens for shared presentations', async () => {
    const { access, fileTicket, projectTicket } = setup();
    expect((await access.prepare({ model_url: '/api/v1/files/library/a/model.glb' })).model_url).toContain('file_ticket=one-file');
    expect(fileTicket).toHaveBeenCalledWith('library/a/model.glb', expect.any(AbortSignal));
    const shared = await access.prepare({ image_url: '/api/v1/files/projects/p/renders/a.png' }, { projectId: 'p', shareToken: 'panel' });
    expect(shared.image_url).toContain('share_token=panel');
    expect(projectTicket).not.toHaveBeenCalled();
  });
  it('clears private ticket caches when the account changes', async () => {
    const { access, logout } = setup();
    await access.prepare({ image_url: '/api/v1/files/projects/p/renders/a.png' });
    logout();
    expect(access.resolve('/api/v1/files/projects/p/renders/a.png')).not.toContain('asset_ticket');
  });
  it('requests the decoded exact storage key for filenames with spaces', async () => {
    const { access, fileTicket } = setup();
    const data = await access.prepare({ model_url: '/api/v1/files/library/a/My%20house.glb' });
    expect(fileTicket).toHaveBeenCalledWith('library/a/My house.glb', expect.any(AbortSignal));
    expect(data.model_url).toContain('My%20house.glb?file_ticket=one-file');
  });
  it('renews existing gallery URLs after a long session and notifies their consumers', async () => {
    vi.useFakeTimers();
    try {
      const { access, projectTicket } = setup();
      const image = (await access.prepare({ image_url: '/api/v1/files/projects/p/renders/a.png' })).image_url;
      const listener = vi.fn(); const unsubscribe = access.subscribe(listener);
      vi.advanceTimersByTime(16 * 60_000);
      expect(access.resolve(image)).not.toContain('asset_ticket');
      projectTicket.mockResolvedValueOnce({ asset_ticket: 'renewed-ticket', expires_in: 900 });
      await access.refresh();
      expect(access.resolve(image)).toContain('asset_ticket=renewed-ticket');
      expect(projectTicket).toHaveBeenCalledTimes(2); expect(listener).toHaveBeenCalledTimes(1);
      unsubscribe();
    } finally { vi.useRealTimers(); }
  });

  it('keeps renewal targets and object ownership after same-account token rotation and a sleeping tab', async () => {
    vi.useFakeTimers();
    try {
      const { access, projectTicket, fileTicket, setToken } = setup();
      const data = await access.prepare({ id: 'building-a', project_id: 'project-a',
        model_url: '/api/v1/buildings/building-a/model/file',
        video_url: '/api/v1/files/projects/project-a/videos/video.mp4',
        private_image: '/api/v1/files/render-audit/a/output.png',
      });
      const listener = vi.fn(); access.subscribe(listener);
      setToken(token('account-a', 2));
      // No resolve/prepare occurs before this focus/visibility renewal. The
      // existing gallery still holds its old decorated URLs after sleeping.
      vi.advanceTimersByTime(16 * 60_000);
      projectTicket.mockResolvedValueOnce({ asset_ticket: 'renewed-project', expires_in: 900 });
      fileTicket.mockResolvedValueOnce({ file_ticket: 'renewed-file', expires_in: 900 });
      await access.refresh();
      expect(projectTicket).toHaveBeenCalledTimes(2);
      expect(fileTicket).toHaveBeenCalledTimes(2);
      expect(access.resolve(data.video_url)).toContain('asset_ticket=renewed-project');
      expect(access.resolve(data.model_url)).toContain('asset_ticket=renewed-project');
      expect(access.resolve(data.private_image)).toContain('file_ticket=renewed-file');
      expect(listener).toHaveBeenCalledTimes(2);
    } finally { vi.useRealTimers(); }
  });

  it('does not discard a same-account ticket response when auth refresh rotates the login token in flight', async () => {
    const { access, projectTicket, setToken } = setup();
    const response = deferred<{ asset_ticket: string; expires_in: number }>();
    projectTicket.mockReturnValueOnce(response.promise);
    const pending = access.prepare({ image_url: '/api/v1/files/projects/p/renders/a.png' });
    setToken(token('account-a', 2));
    response.resolve({ asset_ticket: 'same-account-result', expires_in: 900 });
    expect((await pending).image_url).toContain('asset_ticket=same-account-result');
  });

  it('drops credentials and renewal targets on logout, including immediate login to the same account', async () => {
    const { access, projectTicket, setToken, logout } = setup();
    const previous = await access.prepare({ id: 'building-a', project_id: 'p', model_url: '/api/v1/buildings/building-a/model/file' });
    const listener = vi.fn(); access.subscribe(listener);
    logout();
    expect(listener).toHaveBeenCalledOnce();
    setToken(token('account-a', 3));
    await access.refresh();
    expect(projectTicket).toHaveBeenCalledTimes(1);
    expect(access.resolve(previous.model_url)).not.toContain('asset_ticket');
  });

  it('clears old targets when a different account becomes active while the tab is hidden', async () => {
    const { access, projectTicket, setToken } = setup();
    const old = await access.prepare({ image_url: '/api/v1/files/projects/p/renders/a.png' });
    setToken(token('account-b'));
    await access.refresh();
    expect(projectTicket).toHaveBeenCalledTimes(1);
    expect(access.resolve(old.image_url)).not.toContain('asset_ticket');
    // Unknown object URLs must not retain a private ticket from old query data.
    expect(access.resolve('/api/v1/buildings/unknown/model/file?asset_ticket=account-a-ticket')).not.toContain('asset_ticket');
  });

  it('ignores old-account completion without deleting the new account pending request for the same key', async () => {
    const { access, projectTicket, setToken } = setup();
    const a = deferred<{ asset_ticket: string; expires_in: number }>();
    const b = deferred<{ asset_ticket: string; expires_in: number }>();
    projectTicket.mockReturnValueOnce(a.promise).mockReturnValueOnce(b.promise);
    const path = '/api/v1/files/projects/shared/renders/a.png';
    const first = access.prepare({ image_url: path });
    setToken(token('account-b'));
    const second = access.prepare({ image_url: path });
    a.resolve({ asset_ticket: 'old-account-ticket', expires_in: 900 });
    expect((await first).image_url).not.toContain('old-account-ticket');
    const third = access.prepare({ image_url: path });
    expect(projectTicket).toHaveBeenCalledTimes(2);
    b.resolve({ asset_ticket: 'new-account-ticket', expires_in: 900 });
    expect((await second).image_url).toContain('asset_ticket=new-account-ticket');
    expect((await third).image_url).toContain('asset_ticket=new-account-ticket');
  });

  it('an old-account renewal failure cannot remove the new account completed ticket', async () => {
    vi.useFakeTimers();
    try {
      const { access, projectTicket, setToken } = setup();
      const path = '/api/v1/files/projects/shared/renders/a.png';
      await access.prepare({ image_url: path });
      const oldRenewal = deferred<{ asset_ticket: string; expires_in: number }>();
      projectTicket.mockReturnValueOnce(oldRenewal.promise);
      vi.advanceTimersByTime(16 * 60_000);
      const oldRefresh = access.refresh();
      setToken(token('account-b'));
      projectTicket.mockResolvedValueOnce({ asset_ticket: 'new-account-ticket', expires_in: 900 });
      await access.prepare({ image_url: path });
      oldRenewal.reject(new Error('Old request failed'));
      await oldRefresh;
      expect(access.resolve(path)).toContain('asset_ticket=new-account-ticket');
    } finally { vi.useRealTimers(); }
  });

  it('treats the decoded access subject only as a cache identity and rejects other token forms', () => {
    expect(assetAccountIdentity(token('account-a', 1))).toBe(assetAccountIdentity(token('account-a', 2)));
    expect(assetAccountIdentity(token('account-a'))).not.toBe(assetAccountIdentity(token('account-b')));
    for (const value of [null, '', 'not-a-jwt', 'a.%%%.b', token('', 1), token('account-a', 1, 'refresh'), token('account-a', 1, 'file_asset')]) {
      expect(assetAccountIdentity(value)).toBeNull();
    }
  });
});
