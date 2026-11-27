# CLAUDE.md

This repository is public. Everything committed here is published.

- Content arrives through pull requests only, never by a push to `main`.
- Posts and articles follow `docs/style-guide.md`. `tools/lint_style.py` enforces its section 4 in CI; do not weaken a rule to make a text pass, rewrite the text.
- The linter, its tests and the negative probe `tests/fixtures/tics.md` change together. The probe must keep being rejected.
- Never add infrastructure details: addresses, host names, domain names, network layout, exact software versions, identifiers of internal tools or jobs, known unfixed weaknesses. When in doubt, leave it out and ask.
- Code, comments and README in English. Posts and articles in their own language folder.
- Commits keep the `Co-Authored-By` line of the AI that helped write them.
