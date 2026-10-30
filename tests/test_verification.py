from src.verification import compare_field, verify_records


def test_normalized_invoice_and_customer_match():
    assert compare_field("invoice_number", "INV-001", "inv 001").status == "match"
    assert compare_field("customer_name", "Acme Lanka (Pvt) Ltd", "ACME Lanka Pvt Ltd").status == "match"


def test_amount_mismatch_is_high_risk():
    result = verify_records(
        {"invoice_number":"I-1","invoice_date":"2026-01-01","customer_name":"Acme","invoice_amount":100,"currency":"USD"},
        {"invoice_number":"I-1","invoice_date":"2026-01-01","customer_name":"Acme","invoice_amount":150,"currency":"USD"},
    )
    assert result["status"] == "failed"
    assert result["quality_score"] == 75.0


def test_ambiguous_customer_requires_review():
    assert compare_field("customer_name", "Global Trading Limited", "Global Trade Ltd").status == "review"
