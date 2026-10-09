import type { SpellingIssue } from './spellingTypes';

/** Load the dictionary only on demand and keep suggestion work off the 3D/UI thread. */
export function checkPromptSpelling(text: string): Promise<SpellingIssue[]> {
  return new Promise((resolve, reject) => {
    const worker = new Worker(new URL('./spelling.worker.ts', import.meta.url), { type: 'module' });
    const finish = () => { clearTimeout(timeout); worker.terminate(); };
    const timeout = setTimeout(() => { finish(); reject(new Error('Spelling check timed out')); }, 30000);
    worker.onmessage = (event: MessageEvent<SpellingIssue[]>) => { finish(); resolve(event.data); };
    worker.onerror = () => { finish(); reject(new Error('Spelling dictionary unavailable')); };
    worker.postMessage(text);
  });
}
