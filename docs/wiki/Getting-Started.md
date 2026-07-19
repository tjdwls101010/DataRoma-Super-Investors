# Getting Started

*From nothing installed to a real result on your screen. Follow this page top to bottom and you'll have both the library and the CLI working.*

## Prerequisites

| Requirement | Notes |
|---|---|
| **Python 3.10 or newer** | The codebase uses `X \| None` union syntax, which is 3.10+. Check with `python3 --version`. |
| **An internet connection** | Every call fetches live from `dataroma.com`. There is no offline mode. |
| **Nothing else** | No API key, no account, no configuration file. |

Dependencies (`requests`, `beautifulsoup4`, `lxml`) install automatically.

## Installation

```bash
pip install superinvestor
```

Inside a virtual environment, which is the recommended way:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install superinvestor
```

Verify the install:

```bash
superinvestor --help
```

```
usage: superinvestor [-h] [--json] {holdings,buys,sells,stock,managers} ...

Track what superinvestors buy and sell together

positional arguments:
  {holdings,buys,sells,stock,managers}
    holdings            Grand portfolio holdings
    buys                Consensus buys
    sells               Consensus sells
    stock               Stock detail
    managers            List all superinvestors
```

If `superinvestor: command not found` appears, your virtual environment isn't active, or pip's script directory isn't on your `PATH`. `python3 -m superinvestor --help` works in either case and is a fine substitute everywhere below.

## Your first result

### From the command line

```bash
superinvestor buys -n 5
```

Within a couple of seconds:

```
Symbol   Name                                      Buys  Avg Price
--------------------------------------------------------------------
AMZN     Amazon.com Inc.                             11    $230.82
META     Meta Platforms Inc.                         10    $660.09
RKT      Rocket Companies Inc.                        6     $19.36
GOOG     Alphabet Inc.                                6    $178.44
UBER     Uber Technologies Inc.                       5     $71.20
```

Read this as: *eleven* of the tracked superinvestors bought Amazon in the most recent quarter, at an average holding price of $230.82. Your numbers will differ — this is live data that changes every quarter.

### From Python

```python
from superinvestor import SI

si = SI()
results = si.buys(n=5)

for r in results:
    print(f"{r['symbol']:6} {r['buy_count']:3} buyers")
```

```
AMZN    11 buyers
META    10 buyers
RKT      6 buyers
GOOG     6 buyers
UBER     5 buyers
```

`SI()` takes no arguments — there's nothing to configure.

## Verifying it worked

You have a working installation if:

1. `superinvestor buys -n 5` prints a table with ticker symbols in it.
2. The tickers are recognisable US-listed companies.
3. `superinvestor buys -n 5 --json` prints valid JSON — confirm with `superinvestor buys -n 5 --json | python3 -m json.tool`.

If you get a `requests.exceptions.HTTPError` or a timeout instead, the problem is network-side: check your connection, and check whether [dataroma.com](https://www.dataroma.com) loads in a browser.

## The five things you can ask

```python
from superinvestor import SI
si = SI()
```

**What are they buying together?**

```python
si.buys(n=10)                  # this quarter
si.buys(period="6m", n=10)     # over the last six months
```

**What are they selling?**

```python
si.sells(n=10)
```

**What does the combined portfolio look like?**

```python
si.holdings(n=20)              # ranked by number of owners
```

Note that `holdings()` with no `n` walks through every page of results and is the slowest call in the library — see [Architecture](Architecture.md#pagination-in-holdings). Pass an `n` while exploring.

**Who owns one particular stock?**

```python
detail = si.stock("AAPL")

detail["ownership_count"]      # how many superinvestors hold it
detail["quarterly_activity"]   # last 4 quarters of buy/add/reduce/sell
detail["holders"]              # every holder, with position size and last action
```

**Who's on the roster?**

```python
for m in si.managers():
    print(m["name"], "—", m["firm"], "—", m["num_stocks"], "positions")
```

## A first real question

Which stocks are superinvestors buying that a lot of them *already* own? Agreement plus accumulation:

```python
from superinvestor import SI

si = SI()

buys = si.buys(n=25)
owned = {h["symbol"]: h["ownership_count"] for h in si.holdings(n=100)}

for b in buys:
    holders = owned.get(b["symbol"])
    if holders and holders >= 10:
        print(f"{b['symbol']:6} {b['buy_count']:2} buying · {holders:2} already hold")
```

Two calls, a dict lookup, and you've combined two views of the data — the thing that was tedious in a browser.

## Getting JSON out

Every CLI command accepts `--json`, before or after the subcommand:

```bash
superinvestor buys -n 5 --json
superinvestor --json buys -n 5      # equivalent
```

Which makes shell pipelines straightforward:

```bash
# Just the tickers being bought
superinvestor buys -n 10 --json | jq -r '.[].symbol'

# Everyone holding more than 10% of their portfolio in Apple
superinvestor stock AAPL --json | jq '.holders[] | select(.portfolio_pct > 10) | .manager'
```

## A note on speed

The library enforces a **1.5-second minimum gap between requests** to avoid overloading a free public service. That means:

- Single calls like `buys()` or `sells()` return in about a second.
- `stock()` makes two requests, so expect roughly 2–3 seconds.
- `holdings()` without `n` makes one request per page and can take tens of seconds.

This is deliberate and not configurable. If you need the same data repeatedly, store the result rather than re-fetching — see [Architecture](Architecture.md#no-caching-by-design).

## Where to go next

- [**Core Concepts**](Concepts.md) — what a 13F filing is, what `avg_hold_price` really measures, and what these numbers can't tell you. Read this before drawing conclusions from the data.
- [**API Reference**](API-Reference.md) — every method, parameter, and returned field.
- [**CLI Reference**](CLI-Reference.md) — every command and flag.

---

**Next:** [Core Concepts →](Concepts.md) · **See also:** [API Reference](API-Reference.md) · [Back to index](README.md)
