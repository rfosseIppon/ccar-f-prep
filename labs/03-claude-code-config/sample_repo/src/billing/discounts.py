def apply_discount(total: float, rate: float) -> float:
    """Applique une remise (rate entre 0 et 1) à un total."""
    if not 0 <= rate <= 1:
        raise ValueError("rate doit être compris entre 0 et 1")
    return round(total * (1 - rate), 2)
