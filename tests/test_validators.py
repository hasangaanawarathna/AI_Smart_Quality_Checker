from io import BytesIO
import pytest
from src.validators import MAX_FILE_SIZE_BYTES, read_employee_csv, validate_document

def test_valid_pdf_passes():
    assert validate_document("invoice.pdf",1000,"application/pdf")[0]

def test_oversized_file_fails():
    valid,message=validate_document("invoice.pdf",MAX_FILE_SIZE_BYTES+1,"application/pdf")
    assert not valid and "limit" in message

def test_csv_is_normalised():
    frame=read_employee_csv(BytesIO(b"invoice_number,invoice_date,customer_name,invoice_amount,currency\nINV-1,2026-01-20,Acme,100.5,USD\n"))
    assert frame.loc[0,"invoice_date"]=="2026-01-20" and frame.loc[0,"invoice_amount"]==100.5

def test_csv_missing_column_fails():
    with pytest.raises(ValueError,match="Missing required"):
        read_employee_csv(BytesIO(b"invoice_number,invoice_date\nINV-1,2026-01-20\n"))
