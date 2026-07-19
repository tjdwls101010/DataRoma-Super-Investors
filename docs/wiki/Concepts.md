# Core Concepts

*The vocabulary and mental models you need to read this library's output correctly. Concepts are defined in dependency order — each builds on the ones above it.*

If you already know 13F filings inside out, skip to [The activity vocabulary](#the-activity-vocabulary), which is where this library's specific terms are defined.

## Form 13F

**Form 13F** is a quarterly report that US institutional investment managers must file with the SEC if they exercise discretion over more than **$100 million** in qualifying US securities. It lists the positions the manager held **on the last day of the quarter**.

Three properties make it the foundation of everything here:

1. **It's mandatory.** Filing is a legal obligation, not a marketing decision. A manager cannot report only their winners.
2. **It's public.** Anyone can read every filing, free, from the SEC's EDGAR system.
3. **It's actual positions.** Not opinions, predictions, or television appearances — the securities the fund genuinely owned.

That combination is why 13F data is worth building on: it's one of the few places where you can observe what sophisticated investors *did* rather than what they *said*.

### What 13F filings leave out

A 13F is a snapshot with real gaps. Every one of these limits the conclusions you can draw:

- **Only long US equity positions.** Short positions are not reported at all. A fund could hold Apple shares and a larger offsetting short elsewhere, and the 13F would show only conviction.
- **No bonds, currencies, commodities, or most foreign-listed stock.** For a fund whose main strategy is outside US equities, the 13F may represent a small slice of the portfolio.
- **No cash.** You cannot tell from a 13F whether a manager is fully invested or sitting on 40% cash.
- **Quarter-end only.** A position bought and sold within the quarter never appears. A position established the day before quarter end looks identical to one held for a decade.

### The 45-day lag

Filings are due **within 45 days after the quarter ends**. A position held on 31 December may not become public until mid-February.

So the data is *always* stale by between 45 days and roughly four and a half months, depending on when you look. **This data tells you what smart investors owned recently, not what they own now.** Treat it as a research starting point, never a trade signal.

## Superinvestors

**Superinvestor** is DataRoma's term, not a regulatory one. It refers to their curated roster of managers with long track records of outperformance — Warren Buffett, Bill Ackman, David Einhorn, Seth Klarman, Li Lu, Terry Smith, and dozens more.

Two things follow from the roster being *curated*:

- **It's a selection, and selection is a judgement.** DataRoma decides who qualifies. A different curator would produce a different list and therefore different consensus numbers.
- **It carries survivorship bias.** Managers earn a place on the list by having already done well. That is precisely the group whose past performance is least predictive of the future.

`SI.managers()` returns the current roster.

## The consensus thesis

This is the idea the whole library is organised around.

**One investor's purchase is weak evidence.** They might be rebalancing, hedging an unreported position, deploying a client inflow, satisfying a mandate, or simply wrong. You cannot distinguish conviction from housekeeping in a single line of a single filing.

**Independent agreement is stronger evidence.** When a dozen managers with different strategies, different analysts, and no coordination all buy the same company in the same quarter, "they all made the same mistake for the same reason" becomes a much less comfortable explanation than "there is something here."

This is why every ranked method in the library sorts by **a count of investors**, not by dollars:

| Method | Sorted by |
|---|---|
| `holdings()` | `ownership_count` — how many superinvestors hold it |
| `buys()` | `buy_count` — how many bought it this period |
| `sells()` | `sell_count` — how many sold it this period |

A single $2 billion position counts once. Eleven managers buying counts eleven times. The library is built to surface the second.

### Where the thesis breaks down

Take the signal seriously, but know its failure modes:

- **The agreement isn't fully independent.** Managers read the same research, attend the same conferences, and are known to watch each other's filings. Some consensus is imitation.
- **You're always looking backward.** By the time you see eleven buyers, the quarter closed at least 45 days ago and the price has moved.
- **Crowding is a risk, not just a signal.** A heavily-owned name can unwind violently when several large holders head for the exit at once.
- **The roster is selected on past success**, as above.

Consensus is a good place to *start* research. It is not a conclusion.

## The activity vocabulary

DataRoma classifies each manager's quarter-over-quarter change into four actions. These strings appear in `stock()` results, in `quarterly_activity`, and in the `activity` field of each holder.

| Action | Meaning |
|---|---|
| **Buy** | A **new** position. The manager did not hold this stock last quarter and does now. |
| **Add** | An **existing** position increased. |
| **Reduce** | An existing position **decreased**, but not to zero. |
| **Sell** | A **full exit**. Zero shares remain. |

The distinction that matters most is `Buy` vs `Add`. A new position is a fresh decision to own something; adding to an existing one is often mechanical rebalancing or averaging down. Similarly, `Sell` (complete exit) is a stronger statement than `Reduce` (trimming).

Each action usually carries a percentage — the size of the change relative to the prior position. `Reduce 4.32%` means the position shrank by 4.32%, which is trimming; `Reduce 85%` is nearly an exit.

### Net

`superinvestor` computes a fifth value that DataRoma does not publish directly. In `quarterly_activity`, each quarter has a `net` entry defined as:

```
net.count  = (buy.count  + add.count)  − (reduce.count  + sell.count)
net.shares = (buy.shares + add.shares) − (reduce.shares + sell.shares)
```

Buying actions minus selling actions. A positive `net.count` means more superinvestors moved in than out that quarter; negative means net exodus.

**These two numbers can disagree, and that's informative.** `net.count` of `+5` with `net.shares` deeply negative means several small buyers and one very large seller — the vote count says accumulation while the share count says distribution. Read them together.

The implementation is `_finalize_quarter()` in `parser.py`.

## Fields you'll encounter

### Ownership count

`ownership_count` is the number of superinvestors on the roster holding a stock. It is the core consensus number: the closest thing here to a vote tally.

`ownership_rank` (returned by `stock()`) is where that count places the stock against every other stock DataRoma tracks — rank 1 is the most widely held.

### Average hold price

`avg_hold_price` is the estimated average price at which current holders acquired their shares. **It is an estimate derived from 13F filings, not a figure anyone reported.** Filings disclose share counts and quarter-end values, not purchase prices, so this is reconstructed from position changes across quarters.

Compared against the current market price, it's a rough gauge of whether holders are collectively above or below water. Do not treat it as a precise cost basis.

It may be `None` when the source value can't be parsed — always guard before formatting:

```python
price = f"${h['avg_hold_price']:.2f}" if h.get("avg_hold_price") else "N/A"
```

### Portfolio percentage

`portfolio_pct` (per holder) is what share of *that manager's* disclosed portfolio sits in this stock. It's the best available proxy for conviction: a manager with 22% of their portfolio in one name is making a very different statement than one with 0.3%.

`max_pct` in `holdings()` results is the highest `portfolio_pct` any single holder has in that stock — the strongest individual conviction among all holders.

### Position value

`position_value` is the dollar value of a holder's position as of the filing date. Because filings are quarter-end snapshots, this is the value *then*, not now.

## Periods

`buys()` and `sells()` accept a `period` argument with exactly two valid values:

| Value | Meaning |
|---|---|
| `"q"` | The most recent quarter (default) |
| `"6m"` | The last six months, roughly two quarters |

The six-month window smooths out a single unusual quarter and surfaces sustained accumulation or distribution. Anything other than these two strings raises `ValueError`.

---

**Next:** [API Reference →](API-Reference.md) · **See also:** [Overview](Overview.md) · [Back to index](README.md)
