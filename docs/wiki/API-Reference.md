# API Reference

*Complete reference for the Python API: every method, parameter, returned field, and error. For terminology (`ownership_count`, `avg_hold_price`, the activity actions), see [Core Concepts](Concepts.md).*

## Import and instantiate

```python
from superinvestor import SI

si = SI()
```

`SI` is the only public name the package exports. Its constructor takes **no arguments** — there is nothing to configure: no API key, no base URL, no session options. The `scraper` and `parser` modules exist but are internal; they're documented in [Architecture](Architecture.md) and may change without notice.

`SI` holds no state. Instances are interchangeable, and creating several is harmless — though the rate limiter is process-global, so extra instances won't make anything faster. See [Architecture](Architecture.md#rate-limiting).

## Method summary

| Method | Returns | Requests made |
|---|---|---|
| [`holdings(n=None)`](#siholdingsnnone) | `list[dict]` | One per page (many) |
| [`buys(period="q", n=None)`](#sibuysperiodq-nnone) | `list[dict]` | 1 |
| [`sells(period="q", n=None)`](#sisellsperiodq-nnone) | `list[dict]` | 1 |
| [`stock(symbol)`](#sistocksymbol) | `dict` | 2 |
| [`managers()`](#simanagers) | `list[dict]` | 1 |

---

## `SI.holdings(n=None)`

The **grand portfolio** — every stock held by any superinvestor, ranked by how many hold it.

```python
si.holdings(n=3)
```

```python
[{'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'ownership_count': 31,
  'max_pct': 33.10, 'avg_hold_price': 230.82},
 {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'ownership_count': 27,
  'max_pct': 18.44, 'avg_hold_price': 660.09},
 ...]
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `n` | `int \| None` | `None` | Return only the first N results. `None` returns everything. |

### Returns

`list[dict]`, sorted by `ownership_count` descending:

| Field | Type | Description |
|---|---|---|
| `symbol` | `str` | Ticker symbol |
| `name` | `str` | Company name |
| `ownership_count` | `int` | How many superinvestors hold this stock |
| `max_pct` | `float \| None` | Largest portfolio allocation any single holder has in it (%) |
| `avg_hold_price` | `float \| None` | Estimated average acquisition price across holders ($) |

### Performance note

**This is the slowest method in the library.** It paginates: one HTTP request per page of results, continuing until no "Next" link is found, with the mandatory 1.5-second gap between each. A full run makes many requests and can take tens of seconds.

Crucially, `n` is applied **after** all pages are fetched — it truncates the result list, it does not stop the fetching early. `holdings(n=10)` costs exactly as much as `holdings()`. See [Architecture](Architecture.md#pagination-in-holdings) for why.

---

## `SI.buys(period="q", n=None)`

Stocks superinvestors are **buying**, ranked by how many bought.

```python
si.buys(n=5)
si.buys(period="6m", n=10)
```

```python
[{'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'buy_count': 11, 'avg_hold_price': 230.82},
 {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'buy_count': 10, 'avg_hold_price': 660.09},
 ...]
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `period` | `str` | `"q"` | `"q"` = most recent quarter, `"6m"` = last six months. No other value is accepted. |
| `n` | `int \| None` | `None` | Return only the first N results. |

### Returns

`list[dict]`, sorted by `buy_count` descending:

| Field | Type | Description |
|---|---|---|
| `symbol` | `str` | Ticker symbol |
| `name` | `str` | Company name |
| `buy_count` | `int` | How many superinvestors bought it during the period |
| `avg_hold_price` | `float \| None` | Estimated average acquisition price ($) |

`buy_count` aggregates both new positions and increases to existing ones. To separate them for a specific stock, use [`stock()`](#sistocksymbol), whose `quarterly_activity` splits `buy` from `add`.

---

## `SI.sells(period="q", n=None)`

Stocks superinvestors are **selling**. Identical in every respect to [`buys()`](#sibuysperiodq-nnone), except the count field is named `sell_count`.

```python
si.sells(period="6m", n=5)
```

```python
[{'symbol': 'XYZ', 'name': 'Example Corp.', 'sell_count': 9, 'avg_hold_price': 44.10}, ...]
```

| Field | Type | Description |
|---|---|---|
| `symbol` | `str` | Ticker symbol |
| `name` | `str` | Company name |
| `sell_count` | `int` | How many superinvestors sold or reduced it during the period |
| `avg_hold_price` | `float \| None` | Estimated average acquisition price ($) |

---

## `SI.stock(symbol)`

Everything about **one stock**: who holds it, how much of their portfolio it represents, what they did last quarter, and the trend across the last four quarters.

```python
si.stock("AAPL")
```

```python
{
  'symbol': 'AAPL',
  'sector': 'Technology',
  'ownership_count': 18,
  'ownership_rank': 9,
  'avg_hold_price': 271.86,
  'quarterly_activity': [
    {'period': 'Q4 2025',
     'buy':    {'count': 0,  'shares': 0},
     'add':    {'count': 2,  'shares': 30100},
     'reduce': {'count': 11, 'shares': 13140548},
     'sell':   {'count': 1,  'shares': 11051},
     'net':    {'count': -10, 'shares': -13121499}},
    ...
  ],
  'holders': [
    {'manager': 'Warren Buffett', 'firm': 'Berkshire Hathaway',
     'portfolio_pct': 22.60, 'activity': 'Reduce',
     'activity_pct': 4.32, 'position_value': 61961735000},
    ...
  ]
}
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `symbol` | `str` | Ticker, e.g. `"AAPL"`. Case-insensitive — uppercased internally, so `"aapl"` works. |

### Returns

A single `dict`:

| Field | Type | Description |
|---|---|---|
| `symbol` | `str` | The uppercased ticker you asked for |
| `sector` | `str` | Sector classification; `""` if unavailable |
| `ownership_count` | `int` | How many superinvestors hold it |
| `ownership_rank` | `int` | Rank by ownership count against all tracked stocks (1 = most held) |
| `avg_hold_price` | `float \| None` | Estimated average acquisition price ($) |
| `quarterly_activity` | `list[dict]` | **At most 4** entries, most recent quarter first |
| `holders` | `list[dict]` | Every superinvestor holding it |

### `quarterly_activity` entries

| Field | Type | Description |
|---|---|---|
| `period` | `str` | Quarter label, e.g. `"Q4 2025"` |
| `buy` | `dict` | `{'count': int, 'shares': int}` — **new** positions opened |
| `add` | `dict` | `{'count': int, 'shares': int}` — existing positions increased |
| `reduce` | `dict` | `{'count': int, 'shares': int}` — positions decreased, not to zero |
| `sell` | `dict` | `{'count': int, 'shares': int}` — full exits |
| `net` | `dict` | `{'count': int, 'shares': int}` — (buy + add) − (reduce + sell) |

`count` is the number of managers who took that action; `shares` is the total shares involved. `net` is computed by this library, not supplied by DataRoma — see [Core Concepts](Concepts.md#net) for how to read it, including why `net.count` and `net.shares` can point in opposite directions.

The list is truncated to the **four most recent quarters**; there is no parameter to request more.

### `holders` entries

| Field | Type | Description |
|---|---|---|
| `manager` | `str` | Investor name, e.g. `"Warren Buffett"` |
| `firm` | `str` | Firm name, e.g. `"Berkshire Hathaway"` |
| `portfolio_pct` | `float \| None` | Share of that manager's portfolio in this stock (%) |
| `activity` | `str \| None` | Most recent action: `"Buy"`, `"Add"`, `"Reduce"`, `"Sell"`, or `None` for no change |
| `activity_pct` | `float \| None` | Size of that action (%); `None` when unstated |
| `position_value` | `int` | Position value at the filing date ($); `0` if unparseable |

When a source entry has no separate manager and firm — some funds are listed under a single name — `manager` and `firm` are both set to that same name.

### Unknown symbols

`stock()` does not raise for a ticker no superinvestor holds. DataRoma serves a page regardless, and parsing an empty page yields a result with zeroed and empty fields:

```python
si.stock("NOSUCHTICKER")
# {'symbol': 'NOSUCHTICKER', 'sector': '', 'ownership_count': 0,
#  'ownership_rank': 0, 'avg_hold_price': None,
#  'quarterly_activity': [], 'holders': []}
```

Check `ownership_count` or `holders` to distinguish "not held by anyone tracked" from real data:

```python
data = si.stock(ticker)
if not data["holders"]:
    print(f"No tracked superinvestor holds {ticker}")
```

---

## `SI.managers()`

The full roster of superinvestors DataRoma tracks, with each one's largest positions.

```python
si.managers()
```

```python
[{'name': 'Warren Buffett', 'firm': 'Berkshire Hathaway', 'code': 'BRK',
  'portfolio_value': '$274 B', 'num_stocks': 42,
  'top_holdings': ['AAPL', 'AXP', 'BAC', 'KO', 'CVX']},
 ...]
```

Takes no parameters and returns everything — there is no `n`.

### Returns

`list[dict]`:

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Investor name |
| `firm` | `str` | Firm name |
| `code` | `str` | DataRoma's internal manager code (e.g. `"BRK"`); `""` if not found |
| `portfolio_value` | `str` | Total disclosed portfolio value **as a display string**, e.g. `"$274 B"` |
| `num_stocks` | `int` | Number of positions disclosed |
| `top_holdings` | `list[str]` | Ticker symbols of the largest positions |

> **`portfolio_value` is a string, not a number.** It comes through as DataRoma formats it (`"$274 B"`), so sorting or arithmetic on it requires parsing it yourself. Every other numeric field in this library is a real `int` or `float`; this one is the exception.

As with `firm` elsewhere, single-name funds get the same value in `name` and `firm`.

---

## Errors

### `ValueError` — invalid arguments

Raised **before** any network request, so bad input fails instantly.

```python
si.buys(n=-1)          # ValueError: n must be a non-negative integer or None
si.holdings(n="10")    # ValueError: n must be a non-negative integer or None
si.buys(n=True)        # ValueError — bools are explicitly rejected despite being ints
si.buys(period="year") # ValueError: period must be "q" or "6m"
si.sells(period="1y")  # ValueError: period must be "q" or "6m"
```

`n=0` is valid and returns an empty list.

Validation applies to `holdings()`, `buys()`, and `sells()`. `stock()` and `managers()` take no validated arguments.

### Network errors

The library does not wrap network failures — exceptions from `requests` propagate unchanged:

| Exception | When |
|---|---|
| `requests.exceptions.HTTPError` | DataRoma returned 4xx or 5xx |
| `requests.exceptions.Timeout` | No response within 30 seconds |
| `requests.exceptions.ConnectionError` | DNS failure, no route, connection refused |

There are no retries. A failed request raises immediately.

```python
import requests
from superinvestor import SI

try:
    data = SI().buys(n=5)
except requests.exceptions.RequestException as e:
    print(f"Could not reach DataRoma: {e}")
```

`requests.exceptions.RequestException` is the base class for all three and is the right thing to catch if you want one handler.

### Parsing behaviour on unexpected input

The parser is deliberately forgiving. When a value can't be parsed it substitutes a default rather than raising:

- Integer fields (`ownership_count`, `position_value`, `num_stocks`) → `0`
- Float fields (`avg_hold_price`, `max_pct`, `portfolio_pct`) → `None`
- Rows with too few cells are skipped entirely

The practical consequence: **an upstream layout change surfaces as empty lists or zeroed fields, not as an exception.** If a method returns `[]` and you expected data, that's the signal to check whether DataRoma's page structure moved. Always guard float fields before formatting them:

```python
price = f"${r['avg_hold_price']:.2f}" if r.get("avg_hold_price") else "N/A"
```

---

## Working with the results

Every return value is built from plain lists, dicts, strings, ints, and floats, so it's JSON-serialisable and ready for other tools without conversion:

```python
import json
import pandas as pd
from superinvestor import SI

si = SI()

json.dumps(si.buys(n=5))          # straight to JSON
pd.DataFrame(si.holdings(n=50))   # straight to a DataFrame
```

`pandas` is not a dependency of this project — install it separately if you want that second line.

---

**Next:** [CLI Reference →](CLI-Reference.md) · **See also:** [Core Concepts](Concepts.md) · [Architecture](Architecture.md) · [Back to index](README.md)
