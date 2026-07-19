# superinvestor documentation

`superinvestor` gives you programmatic access to what the world's best-known investors actually own. It reads [DataRoma](https://www.dataroma.com)'s aggregation of SEC 13F filings and returns plain Python dicts — or JSON on the command line — so you can ask questions like *"which stocks did the most superinvestors buy last quarter?"* in a single line of code.

These pages are the complete documentation. The [project README](../../README.md) is the short version.

## Start here

**New to the project?** Read [Overview](Overview.md) to understand what it does and why, then [Getting Started](Getting-Started.md) to have a result on your screen in a few minutes.

**Don't know what a 13F filing is?** Start with [Core Concepts](Concepts.md) — everything else assumes that vocabulary.

## All pages

| Page | What it covers |
|---|---|
| [Overview](Overview.md) | The problem this solves, how it approaches it, who it's for, and its non-goals |
| [Getting Started](Getting-Started.md) | Prerequisites, installation, and a first end-to-end result you can verify |
| [Core Concepts](Concepts.md) | 13F filings, the consensus thesis, the activity vocabulary, and the fields you'll see |
| [API Reference](API-Reference.md) | All five `SI` methods — parameters, return shapes, every field, and errors |
| [CLI Reference](CLI-Reference.md) | Every command, flag, output format, and exit code |
| [Architecture](Architecture.md) | How the scraper, parser, and client layers fit together and why |
| [Development](Development.md) | Local setup, running tests, project layout, and the release process |

## Quick links

- [Install and first query](Getting-Started.md#installation)
- [`SI.buys()` / `SI.sells()`](API-Reference.md#sibuysperiodq-nnone)
- [`SI.stock()` return shape](API-Reference.md#sistocksymbol)
- [What `avg_hold_price` actually means](Concepts.md#average-hold-price)
- [Rate limiting behaviour](Architecture.md#rate-limiting)
- [Contributing](../../CONTRIBUTING.md)

---

**Next:** [Overview →](Overview.md)
