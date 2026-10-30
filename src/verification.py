"""Explainable invoice verification rules.

The engine intentionally accepts already extracted/source fields. OCR can be added later
without changing the comparison contract.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher
import re
from typing import Any


@dataclass(frozen=True)
class FieldResult:
    field: str
    source_value: str
    employee_value: str
    status: str
    score: float
    message: str


WEIGHTS = {
    "invoice_number": 0.25,
    "invoice_date": 0.20,
    "customer_name": 0.20,
    "invoice_amount": 0.25,
    "currency": 0.10,
}


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", _text(value).casefold())


def _date(value: Any) -> date | None:
    text = _text(value)
    for pattern in (r"^(\d{4})-(\d{1,2})-(\d{1,2})$", r"^(\d{1,2})/(\d{1,2})/(\d{4})$"):
        match = re.match(pattern, text)
        if match:
            a, b, c = map(int, match.groups())
            try:
                return date(a, b, c) if len(match.group(1)) == 4 else date(c, b, a)
            except ValueError:
                return None
    return None


def _amount(value: Any) -> Decimal | None:
    try:
        return Decimal(re.sub(r"[^0-9.\-]", "", _text(value)))
    except (InvalidOperation, ValueError):
        return None


def compare_field(field: str, source: Any, employee: Any, amount_tolerance: Decimal = Decimal("0.01")) -> FieldResult:
    left, right = _text(source), _text(employee)
    if not left or not right:
        return FieldResult(field, left, right, "missing", 0.0, "A value is missing from one source.")

    if field == "invoice_amount":
        a, b = _amount(left), _amount(right)
        if a is None or b is None:
            return FieldResult(field, left, right, "review", 0.35, "An amount could not be parsed safely.")
        delta = abs(a - b)
        match = delta <= amount_tolerance
        return FieldResult(field, left, right, "match" if match else "mismatch", 1.0 if match else 0.0, f"Difference: {delta:.2f}")

    if field == "invoice_date":
        a, b = _date(left), _date(right)
        if a is None or b is None:
            return FieldResult(field, left, right, "review", 0.35, "A date could not be parsed safely.")
        return FieldResult(field, left, right, "match" if a == b else "mismatch", 1.0 if a == b else 0.0, "Dates agree." if a == b else f"Dates differ by {abs((a-b).days)} day(s).")

    if field == "customer_name":
        similarity = SequenceMatcher(None, _key(left), _key(right)).ratio()
        if similarity >= 0.90:
            status, message = "match", "Names agree after normalization."
        elif similarity >= 0.72:
            status, message = "review", "Names are similar but need confirmation."
        else:
            status, message = "mismatch", "Names are materially different."
        return FieldResult(field, left, right, status, round(similarity, 3), message)

    match = _key(left) == _key(right)
    return FieldResult(field, left, right, "match" if match else "mismatch", 1.0 if match else 0.0, "Values agree after normalization." if match else "Values differ.")


def verify_records(source: dict[str, Any], employee: dict[str, Any]) -> dict[str, Any]:
    results = [compare_field(field, source.get(field), employee.get(field)) for field in WEIGHTS]
    quality = round(sum(item.score * WEIGHTS[item.field] for item in results) * 100, 1)
    mismatches = sum(item.status in {"mismatch", "missing"} for item in results)
    reviews = sum(item.status == "review" for item in results)
    status = "failed" if mismatches else "review" if reviews else "passed"
    return {
        "status": status,
        "quality_score": quality,
        "risk_score": round(100 - quality, 1),
        "summary": f"{sum(x.status == 'match' for x in results)}/{len(results)} critical fields matched",
        "fields": [asdict(item) for item in results],
    }
