export interface SpellingIssue {
  word: string;
  start: number;
  end: number;
  suggestions: string[];
}
