import pytest

from src.billing.discounts import apply_discount


def test_discount_is_applied():
    assert apply_discount(100.0, 0.25) == 75.0


def test_rate_out_of_range_is_rejected():
    with pytest.raises(ValueError):
        apply_discount(100.0, 1.5)
