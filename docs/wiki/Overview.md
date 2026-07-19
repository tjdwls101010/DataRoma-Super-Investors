# Overview

*What `superinvestor` is, the problem it solves, and where its boundaries are. Read this before anything else.*

## The problem

Every quarter, US institutional investment managers with more than $100 million under management are legally required to disclose their US equity holdings to the SEC on **Form 13F**. This is a remarkable public good: the actual positions of Warren Buffett, Bill Ackman, David Einhorn, Seth Klarman, and dozens of other exceptional investors, filed under penalty of law, free for anyone to read.

The catch is that raw 13F data is close to unusable. Filings arrive as separate documents per manager, per quarter, identifying securities by CUSIP rather than ticker. Answering a simple question — *"which stocks did the most great investors buy this quarter?"* — means downloading dozens of filings, normalising them, diffing each against the prior quarter, and mapping identifiers to tickers.

[DataRoma](https://www.dataroma.com) already does that work and publishes the results. But it publishes them as **web pages**. If you want the numbers in a script, a notebook, or a screener, you are back to copying from a browser.

## What this project does

`superinvestor` closes that last gap. It fetches DataRoma's pages, parses their tables, and hands you plain Python data structures:

```python
from superinvestor import SI

SI().buys(n=5)
# [{'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'buy_count': 11, 'avg_hold_price': 230.82}, ...]
```

Five operations cover the surface:

| Operation | Question it answers |
|---|---|
| `holdings()` | What does the combined superinvestor portfolio look like, ranked by how many own each name? |
| `buys()` | Which stocks are the most superinvestors buying right now? |
| `sells()` | Which are they exiting? |
| `stock(symbol)` | For one stock: who owns it, how much of their portfolio is in it, and what did they do last quarter? |
| `managers()` | Who is on the tracked roster, and what are their largest positions? |

Each is also a CLI subcommand, so none of this requires writing Python.

## The idea underneath it

The project is organised around **consensus**, and that shapes the whole API.

A single investor's purchase carries little information. They may be hedging, rebalancing, accommodating a client mandate, or simply wrong. But independent agreement is different: when a dozen investors with different strategies, different analysts, and no coordination all reach the same conclusion about the same company in the same quarter, the odds that they are all wrong for the same reason drop considerably.

This is why the primary sort key across `holdings()`, `buys()`, and `sells()` is a **count of investors**, not a dollar amount. A $2B position from one manager is one vote. Eleven managers buying is eleven votes. The library is built to surface the second thing.

[Core Concepts](Concepts.md) develops this idea properly, along with its limits.

## Who it's for

- **Python developers building screeners, dashboards, or backtests** who want a clean data source and don't want to write a scraper.
- **Quantitative and fundamental researchers** using superinvestor consensus as one signal among several.
- **Anyone curious** about what great investors own, who would rather type one command than click through a website.

You need to be comfortable with Python or a terminal. You do **not** need a finance background — [Core Concepts](Concepts.md) supplies the vocabulary.

## What makes it different

- **It is a library, not a website.** DataRoma is excellent but browser-bound; this makes the same data scriptable.
- **It requires no credentials.** No API key, no account, no rate-limit tier, no config file. Install and call.
- **It returns plain data.** Dicts and lists, JSON-serialisable as they come. No ORM, no custom classes, no schema to learn — pass results straight to `pandas.DataFrame()` or `json.dumps()`.
- **It is small enough to read.** Roughly 700 lines across four modules. When something looks wrong, you can open [Architecture](Architecture.md) and then read the source that produced it.

## Non-goals

Knowing what this project deliberately does *not* do saves you from expecting the wrong things.

- **It is not a data source of its own.** Every number comes from DataRoma, which gets it from SEC filings. This project adds access, not data.
- **It does not cache.** Every call is a live fetch. If you need results across many calls, hold them in a variable or persist them yourself — see [Architecture](Architecture.md#no-caching-by-design).
- **It has no async interface.** Calls are synchronous and rate-limited on purpose. Concurrency would mean hammering a free service that has no obligation to serve you.
- **It does not return DataFrames.** `pandas` is not a dependency. `pd.DataFrame(si.buys())` works fine and keeps the dependency yours, not the library's.
- **It offers no historical archive.** You get what DataRoma currently publishes — the recent quarters, not a decade of history. `stock()` returns the last four quarters of activity.
- **It gives no advice.** No scoring, ranking, valuation, or recommendation. The library reports what was filed; interpretation is yours.
- **It does not cover non-13F positions.** Short positions, bonds, most foreign-listed equities, and derivatives are outside 13F reporting and therefore invisible here. [Core Concepts](Concepts.md#what-13f-filings-leave-out) covers the blind spots.

## Capabilities at a glance

| | |
|---|---|
| **Language** | Python 3.10+ |
| **Dependencies** | `requests`, `beautifulsoup4`, `lxml` |
| **Interfaces** | Python library (`from superinvestor import SI`) and CLI (`superinvestor`) |
| **Output** | `dict` / `list[dict]`; JSON via `--json` on the CLI |
| **Authentication** | None required |
| **Data source** | [dataroma.com](https://www.dataroma.com), derived from SEC Form 13F |
| **Update cadence** | Quarterly, as filings are published (up to 45 days after quarter end) |
| **License** | MIT |

---

**Next:** [Getting Started →](Getting-Started.md) · **See also:** [Core Concepts](Concepts.md) · [Back to index](README.md)
