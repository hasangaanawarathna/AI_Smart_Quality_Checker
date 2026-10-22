from pathlib import Path
import pandas as pd

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
REQUIRED_CSV_COLUMNS = {"invoice_number", "invoice_date", "customer_name", "invoice_amount", "currency"}

def validate_document(filename, size, mime_type):
    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS: return False, "Unsupported file extension. Upload PDF, JPG, JPEG, or PNG."
    if size <= 0: return False, "The uploaded file is empty."
    if size > MAX_FILE_SIZE_BYTES: return False, f"The file exceeds the {MAX_FILE_SIZE_MB} MB limit."
    if mime_type and mime_type not in ALLOWED_MIME_TYPES: return False, "The detected file type does not match an accepted document format."
    return True, "File type and size validation passed."

def read_employee_csv(file):
    try: frame = pd.read_csv(file)
    except (pd.errors.ParserError, UnicodeDecodeError) as error: raise ValueError("The CSV could not be read. Save it as a UTF-8 comma-separated file.") from error
    frame.columns = [str(column).strip().lower() for column in frame.columns]
    missing = sorted(REQUIRED_CSV_COLUMNS - set(frame.columns))
    if missing: raise ValueError(f"Missing required CSV column(s): {', '.join(missing)}")
    if frame.empty: raise ValueError("The CSV contains no employee records.")
    if frame[list(REQUIRED_CSV_COLUMNS)].isnull().any().any(): raise ValueError("Required CSV fields cannot be empty.")
    amounts = pd.to_numeric(frame["invoice_amount"], errors="coerce")
    if amounts.isnull().any() or (amounts < 0).any(): raise ValueError("invoice_amount must contain valid non-negative numbers.")
    frame["invoice_amount"] = amounts.round(2)
    dates = pd.to_datetime(frame["invoice_date"], errors="coerce")
    if dates.isnull().any(): raise ValueError("invoice_date contains an invalid date.")
    frame["invoice_date"] = dates.dt.strftime("%Y-%m-%d")
    return frame
