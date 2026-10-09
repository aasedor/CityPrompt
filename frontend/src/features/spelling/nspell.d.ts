// Browser-only subset; inputs are bundled UTF-8 text, never Node Buffers.
declare module 'nspell' {
  interface SpellChecker {
    correct(word: string): boolean;
    suggest(word: string): string[];
    add(word: string): SpellChecker;
  }
  export default function nspell(aff: string, dic: string): SpellChecker;
}
