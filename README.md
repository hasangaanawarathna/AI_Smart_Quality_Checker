# AI Smart Quality Checker

An explainable invoice quality-control application built with Streamlit, pandas, SQLite, and ReportLab.

## What the system does

- Validates PDF and image intake (type, extension, size, and duplicate filename)
- Captures employee-entered invoice data manually or from CSV
- Captures independent source-of-truth values from an invoice
- Persists records and audit history in SQLite
- Compares five critical fields using field-specific rules
- Normalizes invoice numbers, currencies, names, dates, and amounts
- Produces weighted quality and risk scores
- Routes mismatches, missing values, and ambiguous names for human review
- Records approval/rejection decisions with reviewer notes
- Exports employee records, a PDF intake summary, and a verification audit CSV

The system does not claim to perform OCR yet. Source values are captured explicitly, and the verification engine is separated behind a stable record contract so an OCR provider can be connected later.

## Run locally

```powershell
cd "C:\Users\sanda\OneDrive\Desktop\AI_Smart_Quality_Checker"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` if the browser does not open automatically.

## Typical workflow

1. Register a document in **Document intake**.
2. Add the employee record in **Data capture → Employee entry** or import the sample CSV.
3. Add independently read values in **Data capture → Source capture** using the same invoice number.
4. Select the invoice in **Quality verification** and run the comparison.
5. Inspect each field result and save an approval or rejection with a note.
6. Download audit files from **Reports & audit**.

## Verification rules

| Field | Rule | Weight |
|---|---|---:|
| Invoice number | Case and punctuation-insensitive exact match | 25% |
| Invoice date | Parsed calendar-date equality | 20% |
| Customer name | Normalized similarity with a review band | 20% |
| Invoice amount | Decimal comparison with 0.01 tolerance | 25% |
| Currency | Case-insensitive exact match | 10% |

Any clear mismatch or missing value fails the automated check. Ambiguous but plausible values are marked for review. All outcomes remain reviewable by a human.

## Tests

```powershell
pytest -q
```

The suite covers file/CSV validation, normalization, mismatch scoring, review routing, SQLite persistence, and reviewer decisions.

Runtime data is stored in `quality_checker.db`, which is intentionally excluded from Git.
