import json
import sys

import pytest

from superinvestor.__main__ import main


@pytest.mark.parametrize(
    "argv",
    [
        ["superinvestor", "--json", "buys", "-n", "1"],
        ["superinvestor", "buys", "-n", "1", "--json"],
    ],
)
def test_json_option_is_accepted_before_or_after_the_command(monkeypatch, capsys, argv):
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(
        "superinvestor.__main__.SI.buys",
        lambda self, period, n: [{"symbol": "AAPL"}],
    )

    main()

    assert json.loads(capsys.readouterr().out) == [{"symbol": "AAPL"}]
