import sqlite3

from src.billing.discounts import apply_discount


def get_invoice(db: sqlite3.Connection, invoice_id: int) -> dict | None:
    row = db.execute("SELECT id, customer_id, total FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    return None if row is None else {"id": row[0], "customer_id": row[1], "total": row[2]}


def discounted_total(db: sqlite3.Connection, invoice_id: int, rate: float) -> float:
    invoice = get_invoice(db, invoice_id)
    return apply_discount(invoice["total"], rate)
