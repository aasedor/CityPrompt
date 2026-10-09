import nspell from 'nspell';
// The package entry uses node:fs. Import its data as Vite assets for browser use.
import aff from '../../../node_modules/dictionary-en-ca/index.aff?raw';
import dic from '../../../node_modules/dictionary-en-ca/index.dic?raw';
import type { SpellingIssue } from './spellingTypes';

const spelling = nspell(aff, dic);
for (const word of ['Calgary', 'Kensington', 'streetscape', 'CityPrompt', 'placemaking']) spelling.add(word);

export function findSpellingIssues(text: string): SpellingIssue[] {
  const issues: SpellingIssue[] = [];
  const suggestions = new Map<string, string[]>();
  // Keep offsets in the original text; ignore web addresses and email addresses.
  const tokens = text.slice(0, 5000).matchAll(/https?:\/\/\S+|[\w.+-]+@[\w.-]+|[\p{L}]+(?:['’][\p{L}]+)*/gu);
  for (const match of tokens) {
    const word = match[0];
    if (word.includes('@') || word.includes('://') || word.length > 40) continue;
    const normalized = word.replace(/’/g, "'");
    if (spelling.correct(normalized)) continue;
    let options = suggestions.get(normalized);
    if (!options) {
      options = spelling.suggest(normalized).slice(0, 5);
      suggestions.set(normalized, options);
    }
    issues.push({ word, start: match.index!, end: match.index! + word.length, suggestions: options });
    if (issues.length === 20) break;
  }
  return issues;
}
