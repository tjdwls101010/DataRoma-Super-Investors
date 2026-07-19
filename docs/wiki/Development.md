# Development

*Setting up a local environment, running the tests, and releasing a version. For contribution etiquette and PR expectations, see [CONTRIBUTING.md](../../CONTRIBUTING.md); for how the code is organised, see [Architecture](Architecture.md).*

## Local setup

```bash
git clone https://github.com/tjdwls101010/DataRoma-Super-Investors.git
cd DataRoma-Super-Investors

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e ".[test]"
```

The editable install (`-e`) means source edits take effect without reinstalling, and `[test]` pulls in `pytest`.

Confirm it worked:

```bash
superinvestor --help    # the console script is on your PATH
pytest                  # 7 tests, well under a second
```

Python **3.10 or newer** is required — the code uses `X | None` union syntax throughout, which is a syntax error on 3.9.

## Project layout

```
DataRoma-Super-Investors/
├── superinvestor/
│   ├── __init__.py       # exports SI, nothing else
│   ├── scraper.py        # HTTP + rate limiting
│   ├── parser.py         # HTML → plain data (pure, no I/O)
│   ├── client.py         # the SI class — public API
│   └── __main__.py       # argparse CLI
├── tests/
│   ├── test_client.py    # argument validation
│   └── test_cli.py       # CLI flag handling
├── docs/wiki/            # this documentation
├── .github/workflows/
│   └── publish.yml       # PyPI release on GitHub release
└── pyproject.toml        # metadata, deps, entry point, pytest config
```

[Architecture](Architecture.md) explains what each module is responsible for and the layering rule between them.

## Running tests

```bash
pytest                       # everything
pytest tests/test_cli.py     # one file
pytest -v                    # verbose
pytest -k period             # match by name
```

`testpaths = ["tests"]` in `pyproject.toml` means bare `pytest` finds the suite from the repo root.

### No test touches the network

This is the suite's single most important property. `tests/test_cli.py` monkeypatches the client method rather than calling it:

```python
monkeypatch.setattr(
    "superinvestor.__main__.SI.buys",
    lambda self, period, n: [{"symbol": "AAPL"}],
)
```

The result is a suite that runs in ~0.1 seconds, passes offline, and never breaks because a quarter rolled over or DataRoma had an outage.

**Keep it that way.** A test that hits `dataroma.com` is slow, flaky, non-deterministic, and rude to a free service.

### Testing parser changes

Parsing is where most bugs live, and it's the easiest layer to test properly, because `parser.py` functions are pure — HTML string in, plain data out. Save a real snippet as a fixture and assert against it:

```python
from superinvestor import parser

GRID_HTML = """
<table id="grid">
  <tr><th>Symbol</th><th>Stock</th></tr>
  <tr><td>AAPL</td><td>Apple Inc.</td></tr>
</table>
"""

def test_grid_table_skips_nothing():
    rows = parser.parse_grid_table(GRID_HTML)
    assert rows[1] == ["AAPL", "Apple Inc."]
```

To capture real HTML for a fixture:

```python
from superinvestor import scraper
open("fixture.html", "w").write(scraper.fetch("stock.php", {"sym": "AAPL"}))
```

Trim it to the smallest markup that reproduces the case — a whole DataRoma page in a test file is unreadable and will rot.

The functions worth covering directly: `parse_grid_table`, `parse_info_table`, `parse_activity_by_quarter`, `parse_activity_string`, and `parse_holdings_row`.

### What isn't covered

Current tests cover argument validation and CLI flag ordering. **Parsing has no direct test coverage**, which is unfortunate given it's the layer most likely to break. Fixture-based parser tests are the most valuable contribution this repo can receive.

## Linting and formatting

There is no linter, formatter, or type-checker configured, and no pre-commit hook. Match the style of the file you're editing:

- `from __future__ import annotations` at the top of modules using union syntax
- Type hints on public functions
- Docstrings on public methods — Google style, with `Args:` and `Returns:`
- Private helpers prefixed with `_`
- Four-space indentation, double quotes

## Manual verification

Tests don't touch the network, so real-data changes need a manual pass:

```bash
superinvestor buys -n 5
superinvestor sells -n 5 --period 6m
superinvestor stock AAPL
superinvestor stock BRK.B          # ticker with a dot
superinvestor managers | head -5
superinvestor holdings -n 5        # slow — paginates fully
superinvestor buys -n 3 --json | python3 -m json.tool
```

Watch for the failure mode described in [Architecture](Architecture.md#forgiving-by-design): the parser degrades gracefully, so a broken selector shows up as **empty lists or zeroed fields**, not as an exception. Empty output where you expected data means check the parser, not the network.

## Releasing

Releases are automated by `.github/workflows/publish.yml`, which triggers on a **published GitHub release** and pushes to PyPI using the `PYPI_API_TOKEN` repository secret.

The process:

1. **Bump the version** in `pyproject.toml`:
   ```toml
   version = "0.3.0"
   ```
   This project follows semantic versioning: patch for fixes, minor for new methods or fields, major for breaking changes to the `SI` surface or returned dict keys.

2. **Verify locally.**
   ```bash
   pytest
   python -m build
   twine check dist/*
   ```

3. **Commit and tag.**
   ```bash
   git commit -am "Release 0.3.0"
   git tag v0.3.0
   git push && git push --tags
   ```

4. **Publish a GitHub release** for the tag. That's what fires the workflow — pushing the tag alone does nothing.

5. **Confirm** the new version appears on [PyPI](https://pypi.org/project/superinvestor/) and installs cleanly:
   ```bash
   pip install --upgrade superinvestor
   ```

### CI does not run tests

`publish.yml` is the only workflow in the repo, and it runs only on release. **Nothing runs `pytest` on a pull request.** No automated check will catch a failing test before merge — run it locally.

Adding a test workflow would be a genuinely useful contribution.

### Known metadata issue

`pyproject.toml` declares its project URLs as `github.com/tjdwls101010/superinvestor`, while this repository actually lives at `github.com/tjdwls101010/DataRoma-Super-Investors`. The PyPI page therefore links to the wrong place. Worth fixing in the `[project.urls]` block on the next release:

```toml
[project.urls]
Homepage = "https://github.com/tjdwls101010/DataRoma-Super-Investors"
Repository = "https://github.com/tjdwls101010/DataRoma-Super-Investors"
Issues = "https://github.com/tjdwls101010/DataRoma-Super-Investors/issues"
```

## Good first contributions

Concrete, well-scoped, and genuinely wanted — each is described in more detail on the [Architecture](Architecture.md#known-inconsistencies) page:

- **Fixture-based parser tests** — the biggest coverage gap in the project.
- **A CI workflow that runs `pytest`** on pull requests.
- **Move `managers()` parsing into `parser.py`** — it's the one method that parses HTML inside `client.py`.
- **Make `holdings(n=...)` stop paginating early** once N rows are collected, instead of fetching every page and truncating.
- **Handle `ValueError` and `requests` exceptions in the CLI** so users get a clean message instead of a traceback.
- **Remove the unused `current_page` parameter** from `_has_next_page()`.

---

**See also:** [Architecture](Architecture.md) · [CONTRIBUTING.md](../../CONTRIBUTING.md) · [Back to index](README.md)
