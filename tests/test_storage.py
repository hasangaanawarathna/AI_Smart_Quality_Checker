from src.storage import decide, get_record, initialize, list_verifications, save_verification, upsert_record


def test_storage_round_trip(tmp_path):
    path = tmp_path / "test.db"
    initialize(path)
    upsert_record("employee", {"invoice_number":"INV-1", "invoice_amount":10}, path)
    assert get_record("INV-1", "employee", path)["invoice_amount"] == 10
    verification_id = save_verification("INV-1", {"status":"passed", "quality_score":100, "fields":[]}, path)
    decide(verification_id, "approved", "Checked", path)
    row = list_verifications(path)[0]
    assert row["decision"] == "approved" and row["reviewer_note"] == "Checked"
