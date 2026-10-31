import { CanceledError, type InternalAxiosRequestConfig } from 'axios';
import { afterEach, expect, it, vi } from 'vitest';
import api, { rendersApi } from './api';

const originalAdapter = api.defaults.adapter;
afterEach(() => { api.defaults.adapter = originalAdapter; localStorage.clear(); });

function delayedTicket(project: string, fileScope = false) {
  localStorage.setItem('access_token', `header.${btoa(JSON.stringify({sub:project,type:'access',ver:0}))}.signature`);
  const tickets: Array<{config:InternalAxiosRequestConfig; complete:()=>void}> = [];
  api.defaults.adapter = async config => {
    const response = (data:unknown) => ({data,status:200,statusText:'OK',headers:{},config});
    if (/(?:asset-ticket|read-ticket)$/.test(config.url || '')) return new Promise((resolve,reject) => {
      tickets.push({config,complete:()=>resolve(response({asset_ticket:'scoped-ticket',file_ticket:'scoped-file',expires_in:900}))});
      config.signal?.addEventListener?.('abort',()=>reject(new CanceledError('Ticket canceled')),{once:true});
    });
    return response([{id:'saved',image_url:fileScope ? `/api/v1/files/library/${project}/a.png` : `/api/v1/files/projects/${project}/renders/a.png`}]);
  };
  return tickets;
}

it('passes render-list cancellation to the HTTP request', async () => {
  const controller = new AbortController();
  let observedSignal: unknown;
  api.defaults.adapter = async config => {
    observedSignal = config.signal;
    return { data: [], status: 200, statusText: 'OK', headers: {}, config };
  };
  await rendersApi.list('project-0', controller.signal);
  expect(observedSignal).toBe(controller.signal);
});

it.each(['project', 'file'])('cancels render-list preparation while the HTTP %s ticket is delayed', async kind => {
  const project='beffaece-e33d-49ca-9f45-92b76d150001';
  const tickets=delayedTicket(project,kind === 'file'),controller=new AbortController();
  let state='pending';
  const result=rendersApi.list(project,controller.signal).then(()=>{state='resolved';},()=>{state='canceled';});
  try {
    await vi.waitFor(()=>expect(tickets).toHaveLength(1));
    controller.abort();
    await vi.waitFor(()=>expect(state).toBe('canceled'));
    expect(tickets[0].config.signal?.aborted).toBe(true);
  } finally {
    tickets.forEach(ticket=>ticket.complete());
    await result;
  }
});

it('keeps a shared HTTP ticket alive for another list consumer and recovers after all consumers cancel', async () => {
  const project='beffaece-e33d-49ca-9f45-92b76d150002',tickets=delayedTicket(project);
  const firstController=new AbortController(),secondController=new AbortController();
  let firstState='pending';
  const first=rendersApi.list(project,firstController.signal).then(()=>{firstState='resolved';},()=>{firstState='canceled';});
  const second=rendersApi.list(project,secondController.signal).catch(error=>error);
  try {
    await vi.waitFor(()=>expect(tickets).toHaveLength(1));
    firstController.abort();
    await vi.waitFor(()=>expect(firstState).toBe('canceled'));
    expect(tickets[0].config.signal?.aborted).toBe(false);
    secondController.abort();
    await vi.waitFor(()=>expect(tickets[0].config.signal?.aborted).toBe(true));
    await second;
    const recovery=rendersApi.list(project);
    await vi.waitFor(()=>expect(tickets).toHaveLength(2));
    tickets[1].complete();
    expect((await recovery)[0].image_url).toContain('asset_ticket=scoped-ticket');
  } finally {
    tickets.forEach(ticket=>ticket.complete());
    await Promise.all([first,second]);
  }
});

it('returns a prepared render to the surviving consumer of a shared HTTP ticket', async () => {
  const project='beffaece-e33d-49ca-9f45-92b76d150003',tickets=delayedTicket(project);
  const controller=new AbortController();
  let firstState='pending';
  const first=rendersApi.list(project,controller.signal).then(()=>{firstState='resolved';},()=>{firstState='canceled';});
  const surviving=rendersApi.list(project);
  try {
    await vi.waitFor(()=>expect(tickets).toHaveLength(1));
    controller.abort();
    await vi.waitFor(()=>expect(firstState).toBe('canceled'));
    expect(tickets[0].config.signal?.aborted).toBe(false);
    tickets[0].complete();
    expect((await surviving)[0].image_url).toContain('asset_ticket=scoped-ticket');
    expect(tickets).toHaveLength(1);
  } finally {
    tickets.forEach(ticket=>ticket.complete());
    await Promise.all([first,surviving]);
  }
});
