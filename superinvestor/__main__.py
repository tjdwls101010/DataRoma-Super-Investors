"""CLI entry point for superinvestor."""

import argparse
import json
import sys

from superinvestor.client import SI


def main():
    output_options = argparse.ArgumentParser(add_help=False)
    output_options.add_argument(
        "--json",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Output as JSON",
    )
    parser = argparse.ArgumentParser(
        prog="superinvestor",
        description="Track what superinvestors buy and sell together",
        parents=[output_options],
    )
    sub = parser.add_subparsers(dest="command")

    # holdings
    p_holdings = sub.add_parser(
        "holdings", help="Grand portfolio holdings", parents=[output_options]
    )
    p_holdings.add_argument("-n", type=int, default=None, help="Top N results")

    # buys
    p_buys = sub.add_parser("buys", help="Consensus buys", parents=[output_options])
    p_buys.add_argument("--period", default="q", choices=["q", "6m"], help="q=quarterly, 6m=6 months")
    p_buys.add_argument("-n", type=int, default=None, help="Top N results")

    # sells
    p_sells = sub.add_parser("sells", help="Consensus sells", parents=[output_options])
    p_sells.add_argument("--period", default="q", choices=["q", "6m"], help="q=quarterly, 6m=6 months")
    p_sells.add_argument("-n", type=int, default=None, help="Top N results")

    # stock
    p_stock = sub.add_parser("stock", help="Stock detail", parents=[output_options])
    p_stock.add_argument("symbol", help="Stock ticker (e.g. AAPL)")

    # managers
    sub.add_parser("managers", help="List all superinvestors", parents=[output_options])

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    si = SI()
    as_json = getattr(args, "json", False)

    if args.command == "holdings":
        data = si.holdings(n=args.n)
        _output(data, as_json, _format_holdings)

    elif args.command == "buys":
        data = si.buys(period=args.period, n=args.n)
        _output(data, as_json, _format_buys)

    elif args.command == "sells":
        data = si.sells(period=args.period, n=args.n)
        _output(data, as_json, _format_sells)

    elif args.command == "stock":
        data = si.stock(args.symbol)
        _output(data, as_json, _format_stock)

    elif args.command == "managers":
        data = si.managers()
        _output(data, as_json, _format_managers)


def _output(data, as_json: bool, formatter):
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        formatter(data)


def _format_holdings(data: list[dict]):
    if not data:
        print("No data found.")
        return
    print(f"{'Symbol':<8} {'Name':<35} {'Owners':>6} {'Max%':>6} {'Avg Price':>10}")
    print("-" * 70)
    for r in data:
        price = f"${r['avg_hold_price']:.2f}" if r.get("avg_hold_price") else "N/A"
        max_pct = f"{r['max_pct']:.1f}" if r.get("max_pct") else "N/A"
        print(f"{r['symbol']:<8} {r['name'][:35]:<35} {r['ownership_count']:>6} {max_pct:>6} {price:>10}")


def _format_buys(data: list[dict]):
    if not data:
        print("No data found.")
        return
    print(f"{'Symbol':<8} {'Name':<40} {'Buys':>5} {'Avg Price':>10}")
    print("-" * 68)
    for r in data:
        price = f"${r['avg_hold_price']:.2f}" if r.get("avg_hold_price") else "N/A"
        print(f"{r['symbol']:<8} {r['name'][:40]:<40} {r['buy_count']:>5} {price:>10}")


def _format_sells(data: list[dict]):
    if not data:
        print("No data found.")
        return
    print(f"{'Symbol':<8} {'Name':<40} {'Sells':>5} {'Avg Price':>10}")
    print("-" * 68)
    for r in data:
        price = f"${r['avg_hold_price']:.2f}" if r.get("avg_hold_price") else "N/A"
        print(f"{r['symbol']:<8} {r['name'][:40]:<40} {r['sell_count']:>5} {price:>10}")


def _format_stock(data: dict):
    if not data:
        print("No data found.")
        return

    price = f"${data['avg_hold_price']:.2f}" if data.get("avg_hold_price") else "N/A"
    print(f"\n  {data['symbol']} — {data['sector']}")
    print(f"  Ownership: {data['ownership_count']} investors (rank #{data['ownership_rank']})")
    print(f"  Avg Hold Price: {price}")

    if data.get("quarterly_activity"):
        print(f"\n  {'Period':<10} {'Buy':>4} {'Add':>4} {'Reduce':>7} {'Sell':>5} {'Net':>5} {'Net Shares':>12}")
        print("  " + "-" * 52)
        for q in data["quarterly_activity"]:
            print(
                f"  {q['period']:<10} "
                f"{q['buy']['count']:>4} {q['add']['count']:>4} "
                f"{q['reduce']['count']:>7} {q['sell']['count']:>5} "
                f"{q['net']['count']:>5} {q['net']['shares']:>12,}"
            )

    if data.get("holders"):
        print(f"\n  {'Manager':<40} {'Port%':>6} {'Activity':<10} {'Value':>15}")
        print("  " + "-" * 75)
        for h in data["holders"]:
            act = h.get("activity") or ""
            if h.get("activity_pct"):
                act = f"{act} {h['activity_pct']}%"
            val = f"${h['position_value']:,}" if h.get("position_value") else "N/A"
            pct = f"{h['portfolio_pct']:.2f}" if h.get("portfolio_pct") else "N/A"
            print(f"  {h['manager'][:40]:<40} {pct:>6} {act:<10} {val:>15}")
    print()


def _format_managers(data: list[dict]):
    if not data:
        print("No data found.")
        return
    print(f"{'Name':<35} {'Firm':<30} {'Value':>10} {'Stocks':>6}")
    print("-" * 85)
    for r in data:
        print(
            f"{r['name'][:35]:<35} {r['firm'][:30]:<30} "
            f"{r['portfolio_value']:>10} {r['num_stocks']:>6}"
        )


if __name__ == "__main__":
    main()
