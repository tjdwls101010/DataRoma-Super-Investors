"""Internal HTML parsing utilities for DataRoma tables."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag


def parse_grid_table(html: str) -> list[list[str]]:
    """Parse the <table id='grid'> and return rows as lists of cell text."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", id="grid")
    if not table or not isinstance(table, Tag):
        return []

    rows = []
    for tr in table.find_all("tr"):
        cells = [_clean(td.get_text()) for td in tr.find_all(["td", "th"])]
        if cells:
            rows.append(cells)
    return rows


def parse_info_table(html: str, table_id: str) -> dict[str, str]:
    """Parse a key-value info table (like t1 on stock.php)."""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", id=table_id)
    if not table or not isinstance(table, Tag):
        return {}

    result = {}
    for tr in table.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        if len(cells) >= 2:
            key = _clean(cells[0].get_text())
            val = _clean(cells[1].get_text())
            if key:
                result[key] = val
    return result


def parse_activity_by_quarter(html: str) -> list[dict]:
    """Parse the activity.php page into quarterly groups.

    Returns a list of dicts, each with 'period' and activity counts.
    """
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", id="grid")
    if not table or not isinstance(table, Tag):
        return []

    quarters: list[dict] = []
    current_quarter: dict | None = None

    for tr in table.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        cell_texts = [_clean(c.get_text()) for c in cells]

        # Skip header row
        if cell_texts and cell_texts[0] == "History":
            continue

        # Quarter header row (single cell like "Q4  2025")
        if len(cells) == 1 and re.match(r"Q\d\s+\d{4}", cell_texts[0]):
            if current_quarter:
                _finalize_quarter(current_quarter)
                quarters.append(current_quarter)
            current_quarter = {
                "period": _normalize_period(cell_texts[0]),
                "buy": {"count": 0, "shares": 0},
                "add": {"count": 0, "shares": 0},
                "reduce": {"count": 0, "shares": 0},
                "sell": {"count": 0, "shares": 0},
                "net": {"count": 0, "shares": 0},
            }
            continue

        # Activity row: [history_icon, manager, activity, share_change, pct_change]
        if current_quarter and len(cell_texts) >= 4:
            activity_text = cell_texts[2] if len(cell_texts) >= 5 else cell_texts[1]
            share_change_text = cell_texts[3] if len(cell_texts) >= 5 else cell_texts[2]

            action, _ = parse_activity_string(activity_text)
            shares = _parse_int(share_change_text)

            if action in ("Buy", "Add", "Reduce", "Sell"):
                key = action.lower()
                current_quarter[key]["count"] += 1
                current_quarter[key]["shares"] += shares

    if current_quarter:
        _finalize_quarter(current_quarter)
        quarters.append(current_quarter)

    return quarters


def parse_activity_string(text: str) -> tuple[str | None, float | None]:
    """Parse an activity string like 'Reduce 4.32%' into (action, pct).

    Returns (None, None) for empty/no activity.
    """
    if not text:
        return None, None

    text = text.strip()

    match = re.match(r"(Buy|Add|Reduce|Sell)\s+([\d.]+)%?", text)
    if match:
        return match.group(1), float(match.group(2))

    if text in ("Buy", "Add", "Reduce", "Sell"):
        return text, None

    return None, None


def parse_holdings_row(cells: list[str]) -> dict | None:
    """Parse a row from the holdings grid (Ownership tab on stock.php).

    Expected columns: [history_icon, manager_name, pct, activity, shares, value]
    """
    if len(cells) < 6:
        return None

    manager_text = cells[1]
    if not manager_text or manager_text == "Portfolio Manager":
        return None

    # Split "Manager Name - Firm Name" or just "Firm Name"
    name, firm = _split_manager_firm(manager_text)
    activity, activity_pct = parse_activity_string(cells[3])

    return {
        "manager": name,
        "firm": firm,
        "portfolio_pct": _parse_float(cells[2]),
        "activity": activity,
        "activity_pct": activity_pct,
        "position_value": _parse_int(cells[5]),
    }


def _finalize_quarter(q: dict) -> None:
    """Calculate net counts and shares for a quarter."""
    buy_count = q["buy"]["count"] + q["add"]["count"]
    sell_count = q["reduce"]["count"] + q["sell"]["count"]
    buy_shares = q["buy"]["shares"] + q["add"]["shares"]
    sell_shares = q["reduce"]["shares"] + q["sell"]["shares"]
    q["net"]["count"] = buy_count - sell_count
    q["net"]["shares"] = buy_shares - sell_shares


def _normalize_period(text: str) -> str:
    """Normalize 'Q4  2025' to 'Q4 2025'."""
    return re.sub(r"\s+", " ", text.strip())


def _split_manager_firm(text: str) -> tuple[str, str]:
    """Split 'Warren Buffett - Berkshire Hathaway' into (name, firm).

    If no ' - ' separator, returns (text, text).
    """
    if " - " in text:
        parts = text.split(" - ", 1)
        return parts[0].strip(), parts[1].strip()
    return text.strip(), text.strip()


def _clean(text: str) -> str:
    """Clean whitespace from text."""
    return " ".join(text.split()).strip()


def _parse_float(text: str) -> float | None:
    """Parse a float from text, stripping $ and commas."""
    text = text.replace("$", "").replace(",", "").replace("%", "").strip()
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def _parse_int(text: str) -> int:
    """Parse an integer from text, stripping $ and commas."""
    text = text.replace("$", "").replace(",", "").strip()
    try:
        return int(text)
    except (ValueError, TypeError):
        return 0
