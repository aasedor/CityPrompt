# Planning history teaching layer

The authored inputs extend the existing exact-variant style audit with
approximate design-era associations and Canadian/international planning
connections. They do not assign actual construction years. Source facts,
interpretations, held identities and source-only variants remain distinct.

The finite scope is 196 current exact choices (188 classified, eight held),
seven uninstalled reviewed building candidates and a 521-family coverage union:
497 legacy families plus 24 current native families outside those legacy files.
All 196 exact choices occur once in the coverage join. 343 legacy families have
no current exact choice. The native-only rows do not invent a complete source
variant count. No candidate or source-only family is activated by the generator.

```powershell
python -m pytest tools/planning_history tools/catalogue_teaching/test_build_data.py -q
python -m tools.planning_history.build_data --output-dir artifacts/planning-history-review-new
```

The CLI refuses an existing output directory. It writes current-only frontend
JSON, 203-row archetype and 521-row coverage CSVs, a source bibliography CSV and
verification counts. CSVs use UTF-8 with BOM for common spreadsheet readers.
Review differences before explicitly promoting text files into frontend/src/data
or docs. Preserve earlier generated output externally.

The original tools/catalogue_teaching/reviewed-inputs pair and base frontend
overlay remain unchanged. The new evidence-lock binds framework, assignments and
candidate inputs to that original reviewed pair. Scope, duplicates, source/era
references, exact domain/archetype/variant/method/revision, held records and date
basis are checked. Candidate hashes must also match the existing independent
RLASM evidence records; editing this layer's lock cannot approve another model.

Do not refresh locks to accept a changed model or unreviewed historical
interpretation. Review the exact new evidence and preserve a new version first.
The scoped .gitattributes entry keeps authored input bytes stable across Git
line-ending conversion. The generator uses explicit authored records, never
runtime keyword classification or inherited dates for an entire source family.

The research synthesis is docs/PLANNING_IN_THE_CANADIAN_CITY_2026-10-25.md.
External drafting versions,logs and UI evidence belong under
C:/dev-artifacts/CityPrompt/planning-history-20261025.
