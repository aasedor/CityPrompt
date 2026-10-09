import { expect, it } from 'vitest';
import { findSpellingIssues } from './spellingEngine';
it('suggests going for goingg using the real Canadian dictionary', () => {
  const text = 'Have a party goingg on in the park.';
  const [issue] = findSpellingIssues(text);
  expect(issue).toMatchObject({ word: 'goingg', start: 13, end: 19 });
  expect(issue.suggestions).toContain('going');
});
it('accepts Canadian spelling and local planning words', () => {
  expect(findSpellingIssues("Calgary neighbourhood colour centre zoning streetscape aren't" )).toEqual([]);
});
it('keeps occurrence offsets, punctuation and case for repeated misspellings', () => {
  const text = 'Goingg, goingg!';
  const issues = findSpellingIssues(text);
  expect(issues.map(i => [i.start, i.end])).toEqual([[0, 6], [8, 14]]);
  expect(issues[0].suggestions).toContain('Going');
});
it('bounds checking for long input and skips URLs', () => {
  expect(findSpellingIssues('https://example.com/goingg')).toEqual([]);
  expect(findSpellingIssues('goingg '.repeat(100))).toHaveLength(20);
});
