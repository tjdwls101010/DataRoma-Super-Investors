<div align="center">

# superinvestor

**Track what legendary investors buy and sell together.**

The only pip-installable library for superinvestor consensus data — see where Buffett, Ackman, Einhorn, and 79 other top investors agree.

[![PyPI](https://img.shields.io/pypi/v/superinvestor)](https://pypi.org/project/superinvestor/)
[![Python](https://img.shields.io/badge/python-3.10%2B-yellow)](#)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)](#)

[Installation](#installation) · [Quick Start](#quick-start) · [API Reference](#api-reference) · [CLI](#cli) · [How It Works](#how-it-works)

</div>

---

## Why This Project?

A single investor buying a stock means nothing — they have their own context, biases, and constraints. But when **dozens of legendary investors independently buy the same stock**, that's a powerful signal.

[DataRoma](https://www.dataroma.com) tracks 82 superinvestors' portfolios from SEC 13F filings. This library gives you **programmatic access** to their consensus — what they're buying together, selling together, and holding together.

```python
from superinvestor import SI

si = SI()
si.buys(n=5)
# [{'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'buy_count': 11, 'avg_hold_price': 230.82},
#  {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'buy_count': 10, 'avg_hold_price': 660.09},
#  {'symbol': 'RKT', 'name': 'Rocket Companies Inc.', 'buy_count': 6, 'avg_hold_price': 19.36}, ...]
```

No API key needed. No config. Just `pip install` and go.

---

## Installation

```bash
pip install superinvestor
```

---

## Quick Start

```python
from superinvestor import SI

si = SI()

# What are superinvestors buying this quarter?
si.buys(n=5)

# What are they selling?
si.sells(n=5)

# Deep dive into a specific stock
si.stock("AAPL")

# Full consensus portfolio
si.holdings(n=10)

# List all 82 tracked superinvestors
si.managers()
```

---

## API Reference

### `SI()`

Create a client instance. No arguments needed.

### `.holdings(n=None) → list[dict]`

Grand portfolio — all stocks held by superinvestors, ranked by ownership count.

```python
si.holdings(n=3)
# [{'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'ownership_count': 31,
#   'max_pct': 33.10, 'avg_hold_price': 230.82}, ...]
```

| Field | Description |
|-------|-------------|
| `symbol` | Ticker symbol |
| `name` | Company name |
| `ownership_count` | Number of superinvestors holding this stock |
| `max_pct` | Maximum portfolio allocation among holders (%) |
| `avg_hold_price` | Weighted average hold price from 13F filings ($) |

### `.buys(period="q", n=None) → list[dict]`

Stocks being bought by multiple superinvestors.

| Parameter | Type | Description |
|-----------|------|-------------|
| `period` | str | `"q"` for quarterly (default), `"6m"` for 6 months |
| `n` | int | Top N results. `None` for all |

```python
si.buys(period="6m", n=10)
```

### `.sells(period="q", n=None) → list[dict]`

Stocks being sold by multiple superinvestors. Same parameters as `.buys()`.

### `.stock(symbol) → dict`

Deep dive into a specific stock: who holds it, quarterly activity trends, and consensus direction.

```python
si.stock("AAPL")
# {
#   'symbol': 'AAPL',
#   'sector': 'Technology',
#   'ownership_count': 18,
#   'ownership_rank': 9,
#   'avg_hold_price': 271.86,
#   'quarterly_activity': [
#     {'period': 'Q4 2025',
#      'buy':    {'count': 0, 'shares': 0},
#      'add':    {'count': 2, 'shares': 30100},
#      'reduce': {'count': 11, 'shares': 13140548},
#      'sell':   {'count': 1, 'shares': 11051},
#      'net':    {'count': -10, 'shares': -13121499}},
#     ...
#   ],
#   'holders': [
#     {'manager': 'Warren Buffett', 'firm': 'Berkshire Hathaway',
#      'portfolio_pct': 22.60, 'activity': 'Reduce',
#      'activity_pct': 4.32, 'position_value': 61961735000},
#     ...
#   ]
# }
```

**Activity types in `quarterly_activity`:**

| Type | Meaning |
|------|---------|
| `buy` | New position opened |
| `add` | Existing position increased |
| `reduce` | Position decreased |
| `sell` | Full exit (0 shares remaining) |
| `net` | (buy + add) − (reduce + sell) |

**Holder fields:**

| Field | Description |
|-------|-------------|
| `manager` | Investor name |
| `firm` | Fund/firm name |
| `portfolio_pct` | % of this investor's portfolio in this stock |
| `activity` | Most recent action: `Buy`, `Add`, `Reduce`, `Sell`, or `None` |
| `activity_pct` | Magnitude of the action (%) |
| `position_value` | Current position value ($) |

### `.managers() → list[dict]`

List all 82 superinvestors tracked by DataRoma.

```python
si.managers()
# [{'name': 'Warren Buffett', 'firm': 'Berkshire Hathaway', 'code': 'BRK',
#   'portfolio_value': '$274 B', 'num_stocks': 42,
#   'top_holdings': ['AAPL', 'AXP', 'BAC', 'KO', 'CVX', ...]}, ...]
```

---

## CLI

All functions are available from the command line.

```bash
# Consensus buys (quarterly, top 5)
superinvestor buys -n 5

# Consensus buys (6 months)
superinvestor buys --period 6m

# Consensus sells
superinvestor sells -n 10

# Stock deep dive
superinvestor stock AAPL

# Grand portfolio
superinvestor holdings -n 20

# All superinvestors
superinvestor managers

# JSON output (for piping to jq, scripts, etc.)
superinvestor buys -n 5 --json
```

---

## How It Works

### The Consensus Thesis

> "If one investor buys a stock, it could mean anything. If ten legendary investors independently buy the same stock, pay attention."

This library is built around the idea that **agreement among multiple independent, skilled investors** is a stronger signal than any single investor's picks. SEC 13F filings (required for institutional managers with $100M+ AUM) reveal what these investors actually own — not what they say on TV.

### Data Source

All data comes from [DataRoma](https://www.dataroma.com), which aggregates SEC 13F filings for 82 carefully curated "superinvestors" including:

- Warren Buffett (Berkshire Hathaway)
- Bill Ackman (Pershing Square)
- David Einhorn (Greenlight Capital)
- Seth Klarman (Baupost Group)
- Li Lu (Himalaya Capital)
- Terry Smith (Fundsmith)
- And 76 more...

### Update Frequency

13F filings are submitted **quarterly**, within 45 days of quarter end. DataRoma processes them as they become available. Real-time data reflects the latest filings.

---

## Disclaimer

This project is **not affiliated with DataRoma** or any of the investors tracked. Data is sourced from public SEC filings via DataRoma.

This tool is for **educational and research purposes only**. It is not financial advice. Past holdings do not predict future performance.

---

## License

MIT
