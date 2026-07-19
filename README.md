<div align="center">

<img src="https://github.com/tjdwls101010/tjdwls101010/blob/main/Images/superinvestor.png?raw=true" width="640" alt="superinvestor">

# superinvestor

**Python library & CLI for [DataRoma](https://www.dataroma.com) — track what legendary investors buy and sell together.**

[![PyPI](https://img.shields.io/pypi/v/superinvestor)](https://pypi.org/project/superinvestor/)
[![Python](https://img.shields.io/pypi/pyversions/superinvestor)](https://pypi.org/project/superinvestor/)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

[Quick Start](#quick-start) · [Usage](#usage) · [Documentation](#documentation) · [Contributing](#contributing)

</div>

---

## What & why

A single investor buying a stock tells you almost nothing — they have their own mandate, tax situation, and time horizon. But when **dozens of independent, highly-skilled investors buy the same stock in the same quarter**, that agreement is worth looking at.

Every US institutional manager with over $100M under management must disclose their holdings to the SEC each quarter on **Form 13F**. [DataRoma](https://www.dataroma.com) aggregates those filings for a curated roster of "superinvestors" — Buffett, Ackman, Einhorn, Klarman, Li Lu, and dozens more — and publishes them as HTML tables.

`superinvestor` turns those tables into plain Python dicts and JSON. No API key, no account, no configuration — `pip install` and you have programmatic access to what the best investors in the world actually own.

New to 13F filings? [**Core Concepts**](docs/wiki/Concepts.md) explains the filings, the consensus thesis, and the vocabulary in full.

## Key features

- **Consensus-first** — surfaces what many investors are doing *together*, not one guru's picks.
- **Five operations, one class** — holdings, buys, sells, per-stock detail, and the manager roster.
- **Zero configuration** — no API key, no auth, no settings file.
- **Library or CLI** — import it in Python, or run it in a terminal and pipe JSON to `jq`.
- **Polite by default** — a built-in 1.5-second floor between requests, so you don't hammer the source.
- **Plain data** — every result is a `dict` or `list[dict]`; no custom objects to learn.

## Quick start

**Prerequisites:** Python 3.10 or newer.

```bash
pip install superinvestor
```

Find the five stocks most superinvestors bought last quarter:

```python
from superinvestor import SI

si = SI()
si.buys(n=5)
```

```python
[{'symbol': 'AMZN', 'name': 'Amazon.com Inc.',   'buy_count': 11, 'avg_hold_price': 230.82},
 {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'buy_count': 10, 'avg_hold_price': 660.09},
 {'symbol': 'RKT',  'name': 'Rocket Companies Inc.', 'buy_count': 6, 'avg_hold_price': 19.36},
 ...]
```

Or without writing any Python at all:

```bash
superinvestor buys -n 5
```

```
Symbol   Name                                      Buys  Avg Price
--------------------------------------------------------------------
AMZN     Amazon.com Inc.                             11    $230.82
META     Meta Platforms Inc.                         10    $660.09
RKT      Rocket Companies Inc.                        6     $19.36
```

That's the whole setup. Full walkthrough: [**Getting Started**](docs/wiki/Getting-Started.md).

## Usage

```python
from superinvestor import SI

si = SI()

si.buys(n=5)                  # what they're buying together this quarter
si.sells(period="6m", n=5)    # what they're selling, over six months
si.holdings(n=10)             # the grand consensus portfolio
si.stock("AAPL")              # who holds one stock, and what they did with it
si.managers()                 # every superinvestor DataRoma tracks
```

The same five operations from the shell, with `--json` on any of them:

```bash
superinvestor holdings -n 20
superinvestor buys --period 6m
superinvestor stock AAPL
superinvestor managers --json | jq '.[0]'
```

Every method, parameter, and returned field is documented in the [**API Reference**](docs/wiki/API-Reference.md); every flag in the [**CLI Reference**](docs/wiki/CLI-Reference.md).

## Documentation

Full documentation lives in [**`docs/wiki/`**](docs/wiki/README.md):

| Page | What's in it |
|---|---|
| [Overview](docs/wiki/Overview.md) | The problem, the approach, who it's for, and what it deliberately doesn't do |
| [Getting Started](docs/wiki/Getting-Started.md) | Install to first result, step by step |
| [Core Concepts](docs/wiki/Concepts.md) | 13F filings, the consensus thesis, buy/add/reduce/sell/net |
| [API Reference](docs/wiki/API-Reference.md) | All five `SI` methods and every field they return |
| [CLI Reference](docs/wiki/CLI-Reference.md) | Every command and flag |
| [Architecture](docs/wiki/Architecture.md) | How the scraper, parser, and client fit together |
| [Development](docs/wiki/Development.md) | Local setup, tests, and the release process |

## Project status

Stable and ready to use. The five `SI` methods and the dict keys they return are the project's public contract — build on them.

`superinvestor` reads DataRoma's public HTML rather than a formal API, so the [Architecture](docs/wiki/Architecture.md) page documents how parsing behaves and what happens when the upstream layout shifts. Pinning a version in production is a good habit here.

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for setup and the PR process, and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community expectations. To report a security issue privately, see [SECURITY.md](SECURITY.md).

## Disclaimer

This project is **not affiliated with DataRoma** or with any investor it tracks. Data originates from public SEC filings, retrieved via DataRoma.

It is provided for **educational and research purposes only** and is not financial advice. 13F filings are disclosed up to 45 days after quarter end and omit short positions and most non-US holdings, so they are a lagging, partial picture. Past holdings do not predict future performance.

## License

Released under the [MIT License](LICENSE).
