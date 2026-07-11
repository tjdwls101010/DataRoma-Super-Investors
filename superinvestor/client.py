"""Public API for superinvestor."""

from __future__ import annotations

import re

from superinvestor import scraper, parser


_PERIOD_PARAMS = {"q": "q", "6m": "h"}


class SI:
    """Client for querying superinvestor consensus data from DataRoma."""

    def holdings(self, n: int | None = None) -> list[dict]:
        """Get the grand portfolio — all stocks held by superinvestors.

        Args:
            n: Return only the top N results. None for all.

        Returns:
            List of dicts sorted by ownership count descending.
        """
        _validate_limit(n)

        all_rows: list[dict] = []
        page = 1

        while True:
            html = scraper.fetch(
                "g/portfolio.php", {"pct": "0", "o": "c", "L": str(page)}
            )
            rows = parser.parse_grid_table(html)

            if len(rows) <= 1:  # only header or empty
                break

            for row in rows[1:]:  # skip header
                parsed = self._parse_portfolio_row(row)
                if parsed:
                    all_rows.append(parsed)

            # Check if there's a next page
            if not self._has_next_page(html, page):
                break
            page += 1

        if n is not None:
            return all_rows[:n]
        return all_rows

    def buys(self, period: str = "q", n: int | None = None) -> list[dict]:
        """Get stocks being bought by superinvestors.

        Args:
            period: "q" for quarterly, "6m" for 6 months.
            n: Return only the top N results. None for all.

        Returns:
            List of dicts sorted by buy count descending.
        """
        _validate_limit(n)
        q = _period_param(period)
        html = scraper.fetch("g/portfolio_b.php", {"q": q})
        rows = parser.parse_grid_table(html)

        results = []
        for row in rows[1:]:  # skip header
            parsed = self._parse_buysell_row(row, "buy_count")
            if parsed:
                results.append(parsed)

        if n is not None:
            return results[:n]
        return results

    def sells(self, period: str = "q", n: int | None = None) -> list[dict]:
        """Get stocks being sold by superinvestors.

        Args:
            period: "q" for quarterly, "6m" for 6 months.
            n: Return only the top N results. None for all.

        Returns:
            List of dicts sorted by sell count descending.
        """
        _validate_limit(n)
        q = _period_param(period)
        html = scraper.fetch("g/portfolio_s.php", {"q": q})
        rows = parser.parse_grid_table(html)

        results = []
        for row in rows[1:]:
            parsed = self._parse_buysell_row(row, "sell_count")
            if parsed:
                results.append(parsed)

        if n is not None:
            return results[:n]
        return results

    def stock(self, symbol: str) -> dict:
        """Get detailed superinvestor consensus for a specific stock.

        Args:
            symbol: Stock ticker (e.g., "AAPL").

        Returns:
            Dict with ownership info, quarterly activity, and holders.
        """
        symbol = symbol.upper()

        # Ownership tab
        ownership_html = scraper.fetch("stock.php", {"sym": symbol})
        info = parser.parse_info_table(ownership_html, "t1")
        grid_rows = parser.parse_grid_table(ownership_html)

        # Activity tab
        activity_html = scraper.fetch("activity.php", {"sym": symbol, "typ": "a"})
        quarters = parser.parse_activity_by_quarter(activity_html)

        # Parse holders from ownership grid
        holders = []
        for row in grid_rows[1:]:  # skip header
            h = parser.parse_holdings_row(row)
            if h:
                holders.append(h)

        return {
            "symbol": symbol,
            "sector": info.get("Sector:", ""),
            "ownership_count": _safe_int(info.get("Ownership count:", "0")),
            "ownership_rank": _safe_int(info.get("Ownership rank:", "0")),
            "avg_hold_price": _safe_float(
                info.get("Hold Price * :", "0").replace("$", "").replace(",", "")
            ),
            "quarterly_activity": quarters[:4],  # last 4 quarters
            "holders": holders,
        }

    def managers(self) -> list[dict]:
        """Get list of all superinvestors tracked by DataRoma.

        Returns:
            List of dicts with manager info and top holdings.
        """
        html = scraper.fetch("managers.php")

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", id="grid")
        if not table:
            return []

        results = []
        for tr in table.find_all("tr")[1:]:  # skip header
            cells = tr.find_all(["td", "th"])
            if len(cells) < 3:
                continue

            manager_text = parser._clean(cells[0].get_text())
            if not manager_text or manager_text == "Portfolio Manager - Firm":
                continue

            name, firm = parser._split_manager_firm(manager_text)
            code = ""
            manager_link = cells[0].find("a", href=True)
            if manager_link and "holdings.php" in manager_link["href"]:
                match = re.search(r"m=([^&]+)", manager_link["href"])
                if match:
                    code = match.group(1)

            portfolio_value = parser._clean(cells[1].get_text()) if len(cells) > 1 else ""
            num_stocks = _safe_int(parser._clean(cells[2].get_text())) if len(cells) > 2 else 0

            # Extract ticker symbols from link text in remaining cells
            top_holdings = []
            for cell in cells[3:]:
                link = cell.find("a")
                if link:
                    ticker = link.get_text().strip()
                    if ticker:
                        top_holdings.append(ticker)

            results.append({
                "name": name,
                "firm": firm,
                "code": code,
                "portfolio_value": portfolio_value,
                "num_stocks": num_stocks,
                "top_holdings": top_holdings,
            })

        return results

    @staticmethod
    def _parse_portfolio_row(cells: list[str]) -> dict | None:
        """Parse a row from portfolio.php grid."""
        if len(cells) < 6:
            return None

        symbol = cells[0].strip()
        if not symbol or symbol == "Symbol":
            return None

        return {
            "symbol": symbol,
            "name": cells[1].strip(),
            "ownership_count": _safe_int(cells[3]),
            "max_pct": _safe_float(cells[5]),
            "avg_hold_price": _safe_float(
                cells[4].replace("$", "").replace(",", "")
            ),
        }

    @staticmethod
    def _parse_buysell_row(cells: list[str], count_key: str) -> dict | None:
        """Parse a row from portfolio_b.php or portfolio_s.php."""
        if len(cells) < 5:
            return None

        symbol = cells[0].strip()
        if not symbol or symbol == "Symbol":
            return None

        return {
            "symbol": symbol,
            "name": cells[1].strip(),
            count_key: _safe_int(cells[3]),
            "avg_hold_price": _safe_float(
                cells[4].replace("$", "").replace(",", "")
            ),
        }

    @staticmethod
    def _has_next_page(html: str, current_page: int) -> bool:
        """Check if there's a next page link."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        next_link = soup.find("a", string="Next")
        return next_link is not None



def _safe_int(text: str) -> int:
    text = str(text).replace("$", "").replace(",", "").strip()
    try:
        return int(text)
    except (ValueError, TypeError):
        return 0


def _safe_float(text: str) -> float | None:
    text = str(text).replace("$", "").replace(",", "").strip()
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def _period_param(period: str) -> str:
    if not isinstance(period, str) or period not in _PERIOD_PARAMS:
        raise ValueError('period must be "q" or "6m"')
    return _PERIOD_PARAMS[period]


def _validate_limit(n: int | None) -> None:
    if n is not None and (isinstance(n, bool) or not isinstance(n, int) or n < 0):
        raise ValueError("n must be a non-negative integer or None")
