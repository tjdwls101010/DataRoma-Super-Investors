# Contributing to superinvestor

Thanks for considering a contribution. `superinvestor` is a small, deliberately simple project — around 700 lines across four modules — which means a newcomer can read the whole thing in one sitting and make a meaningful change on their first attempt.

## Scope — what's wanted

Good contributions here look like:

- **Parser robustness.** DataRoma's HTML changes occasionally. Fixes for rows or fields that parse incorrectly are the most valuable contributions this project receives.
- **Bug fixes** with a test that reproduces the bug first.
- **Documentation** — corrections, clearer explanations, better examples in `docs/wiki/`.
- **Test coverage**, particularly for parsing logic, using saved HTML fixtures rather than live requests.

Please **open an issue before** starting on:

- **New dependencies.** The project runs on `requests`, `beautifulsoup4`, and `lxml`. Adding a fourth is a design decision, not an implementation detail.
- **New public API surface.** The `SI` class has five methods on purpose. A sixth needs a discussion about whether it belongs.
- **Async, caching, or DataFrame layers.** These have been considered and left out — see [Non-goals](docs/wiki/Overview.md#non-goals). A compelling case can change that, but start with the issue.

## Ways to contribute

- **Report a bug** — open an issue with the ticker or command you ran, what you got, and what you expected.
- **Fix a parser** — the highest-impact area; see below.
- **Improve the docs** — everything in `docs/wiki/` is fair game.
- **Triage** — reproducing and confirming an open issue is real help.

## Development setup

```bash
git clone https://github.com/tjdwls101010/DataRoma-Super-Investors.git
cd DataRoma-Super-Investors

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e ".[test]"
```

The `-e` (editable) install means your source edits take effect immediately, and it puts the `superinvestor` command on your `PATH`. Verify:

```bash
superinvestor --help
superinvestor buys -n 3          # makes a real request to dataroma.com
```

Python 3.10 or newer is required — the code uses `X | None` union syntax throughout.

## Tests and checks

```bash
pytest
```

That's the full check suite. It should complete in well under a second, because **no test makes a network request** — `tests/test_cli.py` monkeypatches `SI.buys` rather than calling out.

Please keep it that way. A test that hits `dataroma.com` is slow, fails offline, and breaks when the upstream data changes. To test parsing, save a snippet of real HTML as a fixture and feed it to the `parser` functions directly, which take HTML strings and return plain data:

```python
from superinvestor import parser

rows = parser.parse_grid_table(saved_html)
assert rows[1][0] == "AAPL"
```

There is no linter or formatter configured. Match the style of the file you're editing.

## Making a change

1. **Branch** off `main`. Name it for what it does: `fix-manager-firm-split`, `docs-cli-examples`.
2. **Write the test first** when fixing a bug — a test that fails before your fix and passes after is the clearest possible evidence the bug was real.
3. **Keep the diff surgical.** Change what the fix requires and nothing adjacent. Unrelated reformatting makes a two-line fix unreviewable.
4. **Run `pytest`** before pushing.
5. **Open a PR** describing what was broken, how you fixed it, and how you verified it. If it changes behaviour a user would notice, say so explicitly.

Commit messages: a short imperative summary line ("Fix firm name split when manager has a hyphen"), with detail in the body if the change needs explaining.

### What CI checks

The only workflow in this repo, `.github/workflows/publish.yml`, runs on **published releases** and pushes the package to PyPI. It does **not** run tests on pull requests. Nothing catches a failing test for you — run `pytest` locally before you push.

## Reporting bugs

There are no issue templates. A useful report includes:

- the exact command or Python call,
- the full output or traceback,
- what you expected instead,
- your Python version and `superinvestor` version (`pip show superinvestor`).

For parsing bugs, the ticker matters — DataRoma's tables differ subtly between stocks, and "AAPL works but XYZ doesn't" narrows the cause immediately.

**Security issues do not go in the issue tracker.** See [SECURITY.md](SECURITY.md) for the private channel.

## Code of Conduct

Participation in this project is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
