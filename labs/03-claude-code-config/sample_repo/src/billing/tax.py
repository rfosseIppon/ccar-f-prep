def add_vat(amount: float, vat_rate: float = 0.20) -> float:
    return round(amount * (1 + vat_rate), 2)
