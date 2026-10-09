import { findSpellingIssues } from './spellingEngine';
self.onmessage = (event: MessageEvent<string>) => {
  self.postMessage(findSpellingIssues(event.data));
};
