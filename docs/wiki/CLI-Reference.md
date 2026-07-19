# CLI Reference

*Every command, flag, and output format for the `superinvestor` command-line tool. The CLI exposes the same five operations as the Python API — see [API Reference](API-Reference.md) for the underlying methods and their return shapes.*

## Synopsis

```
superinvestor [-h] [--json] {holdings,buys,sells,stock,managers} ...
```

Installing the package puts `superinvestor` on your `PATH`. If the command isn't found, `python3 -m superinvestor` is equivalent and works anywhere the package is importable.

## Global options

| Option | Description |
|---|---|
| `-h`, `--help` | Show help and exit. Works globally and on every subcommand. |
| `--json` | Print raw JSON instead of a formatted table. |

`--json` is accepted **before or after** the subcommand — both of these are valid and do the same thing:

```bash
superinvestor --json buys -n 5
superinvestor buys -n 5 --json
```

Running `superinvestor` with no subcommand prints help and exits with status **1**.

---

## `holdings`

The grand portfolio — every stock held by any superinvestor, ranked by number of owners.

```
superinvestor holdings [-h] [--json] [-n N]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `-n N` | int | all | Show only the top N results |

```bash
superinvestor holdings -n 5
```

```
Symbol   Name                                Owners   Max%  Avg Price
----------------------------------------------------------------------
AMZN     Amazon.com Inc.                         31   33.1    $230.82
META     Meta Platforms Inc.                     27   18.4    $660.09
GOOG     Alphabet Inc.                           24   12.7    $178.44
```

> **This is the slow one.** It fetches every page of results before applying `-n`, at 1.5 seconds per page, so it can take tens of seconds. `-n 5` costs the same as no `-n` at all. Details in [Architecture](Architecture.md#pagination-in-holdings).

Columns map to `symbol`, `name`, `ownership_count`, `max_pct`, and `avg_hold_price`. Unavailable prices and percentages print as `N/A`.

---

## `buys`

Stocks superinvestors are buying, ranked by how many bought.

```
superinvestor buys [-h] [--json] [--period {q,6m}] [-n N]
```

| Option | Type | Default | Description |
|---|---|---|---|
| `--period` | `q` or `6m` | `q` | `q` = most recent quarter, `6m` = last six months |
| `-n N` | int | all | Show only the top N results |

```bash
superinvestor buys -n 5
superinvestor buys --period 6m -n 10
```

```
Symbol   Name                                       Buys  Avg Price
--------------------------------------------------------------------
AMZN     Amazon.com Inc.                              11    $230.82
META     Meta Platforms Inc.                          10    $660.09
RKT      Rocket Companies Inc.                         6     $19.36
```

---

## `sells`

Stocks superinvestors are selling. Same options as `buys`.

```
superinvestor sells [-h] [--json] [--period {q,6m}] [-n N]
```

```bash
superinvestor sells -n 10
superinvestor sells --period 6m
```

```
Symbol   Name                                      Sells  Avg Price
--------------------------------------------------------------------
XYZ      Example Corp.                                 9     $44.10
```

---

## `stock`

Full detail for one stock: ownership summary, four quarters of activity, and every holder.

```
superinvestor stock [-h] [--json] symbol
```

| Argument | Description |
|---|---|
| `symbol` | Ticker, e.g. `AAPL`. Case-insensitive. |

```bash
superinvestor stock AAPL
```

```
  AAPL — Technology
  Ownership: 18 investors (rank #9)
  Avg Hold Price: $271.86

  Period      Buy  Add  Reduce  Sell   Net   Net Shares
  ----------------------------------------------------
  Q4 2025       0    2      11     1   -10  -13,121,499
  Q3 2025       1    3       8     0    -4   -2,455,300

  Manager                                   Port%  Activity            Value
  ---------------------------------------------------------------------------
  Warren Buffett                            22.60  Reduce 4.32%  $61,961,735,000
  Terry Smith                                4.10  Add 1.20%      $1,204,000,000
```

Three blocks: the ownership header, the quarterly activity table (at most four quarters, newest first), and the holder table. See [Core Concepts](Concepts.md#the-activity-vocabulary) for what Buy / Add / Reduce / Sell / Net mean.

This command makes **two** HTTP requests, so it takes roughly 2–3 seconds.

A ticker no superinvestor holds doesn't error — it prints the header with zeros and no tables.

---

## `managers`

The full roster of tracked superinvestors.

```
superinvestor managers [-h] [--json]
```

Takes no arguments beyond `--json` — there is no `-n`.

```bash
superinvestor managers
```

```
Name                                Firm                                Value  Stocks
-------------------------------------------------------------------------------------
Warren Buffett                      Berkshire Hathaway                 $274 B      42
Bill Ackman                         Pershing Square                     $12 B      11
```

The table view omits `code` and `top_holdings`. Use `--json` to get those.

---

## JSON output

`--json` prints the exact structure the Python API returns, indented by 2, with `ensure_ascii=False` so non-ASCII names stay readable.

```bash
superinvestor buys -n 2 --json
```

```json
[
  {
    "symbol": "AMZN",
    "name": "Amazon.com Inc.",
    "buy_count": 11,
    "avg_hold_price": 230.82
  },
  {
    "symbol": "META",
    "name": "Meta Platforms Inc.",
    "buy_count": 10,
    "avg_hold_price": 660.09
  }
]
```

Field-by-field documentation lives in the [API Reference](API-Reference.md) — the JSON is identical to the Python return values.

### Pipeline recipes

```bash
# Tickers only
superinvestor buys -n 10 --json | jq -r '.[].symbol'

# Names bought by 5+ superinvestors
superinvestor buys --json | jq -r '.[] | select(.buy_count >= 5) | .name'

# Managers with more than 10% of their portfolio in Apple
superinvestor stock AAPL --json | jq -r '.holders[] | select(.portfolio_pct > 10) | .manager'

# Save the grand portfolio to CSV
superinvestor holdings --json \
  | jq -r '.[] | [.symbol, .name, .ownership_count] | @csv' > holdings.csv

# Net share flow per quarter for one stock
superinvestor stock MSFT --json | jq -r '.quarterly_activity[] | "\(.period): \(.net.shares)"'
```

Note that `avg_hold_price`, `max_pct`, and `portfolio_pct` can be `null` in JSON — guard with `// 0` or `select(. != null)` in `jq` before doing arithmetic.

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | No subcommand given (help was printed) |
| `2` | Invalid argument — unknown subcommand, or a bad `--period` value |

```bash
superinvestor buys --period 1y
# superinvestor buys: error: argument --period: invalid choice: '1y' (choose from q, 6m)
# exit 2
```

### Known rough edge: negative `-n`

Argparse accepts `-n -1` (it only checks that the value is an integer), and the validation error then surfaces as an unhandled Python traceback rather than a clean message:

```bash
superinvestor buys -n -1
# Traceback (most recent call last):
#   ...
# ValueError: n must be a non-negative integer or None
```

The input is correctly rejected and nothing is fetched — it's the presentation that's rough. Network failures behave the same way, printing a `requests` traceback rather than a friendly error. If you're scripting around this, check `-n` yourself before invoking.

---

## Notes on timing

Every request is spaced at least **1.5 seconds** apart, so:

| Command | Requests | Rough duration |
|---|---|---|
| `buys`, `sells`, `managers` | 1 | ~1 second |
| `stock` | 2 | ~2–3 seconds |
| `holdings` | one per page | tens of seconds |

The interval is not configurable. If you need the same data more than once, redirect it to a file rather than re-running the command — see [Architecture](Architecture.md#no-caching-by-design).

---

**Next:** [Architecture →](Architecture.md) · **See also:** [API Reference](API-Reference.md) · [Back to index](README.md)
