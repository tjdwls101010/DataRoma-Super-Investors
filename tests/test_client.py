import pytest

from superinvestor import SI


@pytest.mark.parametrize("method_name", ["holdings", "buys", "sells"])
def test_negative_result_limit_is_rejected(method_name):
    method = getattr(SI(), method_name)

    with pytest.raises(ValueError, match="non-negative"):
        method(n=-1)


@pytest.mark.parametrize("method_name", ["buys", "sells"])
def test_invalid_period_is_rejected(method_name):
    method = getattr(SI(), method_name)

    with pytest.raises(ValueError, match="period"):
        method(period="year")
