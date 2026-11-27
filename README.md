# governed-ai-homelab

Notes, posts and articles on running AI agents in a homelab where mistakes are not free: governance, verifiable decision records, fail-closed checks, separated agent roles, review.

Work in progress. Nothing is published yet.

## Layout

| Path | Content |
|---|---|
| `posts/fr`, `posts/en` | LinkedIn posts (mostly French) |
| `articles/fr`, `articles/en` | Blog articles |
| `kit/` | Reusable patterns, once they exist |
| `docs/style-guide.md` | Writing style guide (French) |
| `tools/lint_style.py` | Style linter run in CI on `posts/` and `articles/` |

## Checks

Every pull request runs the style linter, its unit tests, a negative probe that must be rejected (`tests/fixtures/tics.md`), and a Gitleaks scan of the full history. `main` only moves through pull requests.

```sh
python -m unittest discover -s tests
python tools/lint_style.py posts articles
```

Written with AI assistance; commits say so.
