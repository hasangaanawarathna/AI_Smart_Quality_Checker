"""AI Smart Quality Checker - Stage 1."""
from datetime import date, datetime
from io import BytesIO
import pandas as pd
import streamlit as st
from src.reports import build_entries_csv, build_summary_pdf
from src.ui import inject_styles, render_header
from src.validators import MAX_FILE_SIZE_MB, read_employee_csv, validate_document

st.set_page_config(page_title="AI Smart Quality Checker", page_icon="✓", layout="wide")
inject_styles()
for key in ("documents", "entries", "activities"):
    if key not in st.session_state:
        st.session_state[key] = []

def activity(action, detail):
    st.session_state.activities.insert(0, {"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": action, "detail": detail})

def dashboard():
    render_header("Dashboard", "A live overview of this browser session")
    cards = [("Documents uploaded", len(st.session_state.documents), "Stage 1 intake"), ("Employee records", len(st.session_state.entries), "Manual + CSV"), ("Errors detected", "—", "Enabled in Stage 3"), ("Pending review", "—", "Enabled in Stage 3")]
    for col, (label, value, note) in zip(st.columns(4), cards):
        col.markdown(f'<div class="metric-card"><span>{label}</span><strong>{value}</strong><small>{note}</small></div>', unsafe_allow_html=True)
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        st.subheader("Recent activity")
        if st.session_state.activities:
            st.dataframe(pd.DataFrame(st.session_state.activities[:8]), use_container_width=True, hide_index=True)
        else:
            st.info("No activity yet. Upload a document or add an employee record to begin.")
    with right:
        st.subheader("Verification pipeline")
        for number, title, status in [("1", "Document intake", "Available now"), ("2", "OCR extraction", "Stage 2"), ("3", "Field comparison", "Stage 3"), ("4", "Human review", "Stage 3")]:
            st.markdown(f'<div class="pipeline"><b>{number}</b><div><strong>{title}</strong><span>{status}</span></div></div>', unsafe_allow_html=True)
    st.subheader("Error distribution")
    st.info("Error analytics will appear after comparison is introduced in Stage 3. No fabricated values are shown.")

def document_upload():
    render_header("Document Upload", "Securely validate and stage one invoice document")
    st.markdown(f'<div class="notice">Accepted: PDF, JPG, JPEG, PNG · Maximum size: {MAX_FILE_SIZE_MB} MB · Files remain in this session during Stage 1.</div>', unsafe_allow_html=True)
    upload = st.file_uploader("Drop an invoice here or browse", type=["pdf", "jpg", "jpeg", "png"], help="Text extraction is added in Stage 2.")
    if upload:
        valid, message = validate_document(upload.name, upload.size, upload.type)
        (st.success if valid else st.error)(message)
        if valid:
            a, b, c = st.columns(3)
            a.metric("File", upload.name); b.metric("Size", f"{upload.size / 1024:.1f} KB"); c.metric("Type", upload.type or "Extension")
            if st.button("Add document to session", type="primary", use_container_width=True):
                if upload.name in {item["name"] for item in st.session_state.documents}:
                    st.warning("A document with this name is already in the session.")
                else:
                    st.session_state.documents.append({"name": upload.name, "size_kb": round(upload.size / 1024, 1), "type": upload.type, "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M")})
                    activity("Document uploaded", upload.name); st.success(f"{upload.name} was added successfully.")
    if st.session_state.documents:
        st.subheader("Documents in this session")
        st.dataframe(pd.DataFrame(st.session_state.documents), use_container_width=True, hide_index=True)

def employee_data():
    render_header("Employee Data Entry", "Enter invoice data manually or import a CSV file")
    manual_tab, csv_tab = st.tabs(["Manual entry", "CSV upload"])
    with manual_tab:
        with st.form("employee_form", clear_on_submit=True):
            first, second = st.columns(2)
            invoice_number = first.text_input("Invoice Number *", placeholder="INV-2026-001")
            invoice_date = second.date_input("Invoice Date *", value=date.today())
            customer_name = first.text_input("Customer Name *", placeholder="Acme Lanka (Pvt) Ltd")
            invoice_amount = second.number_input("Invoice Amount *", min_value=0.0, step=0.01, format="%.2f")
            currency = first.selectbox("Currency *", ["LKR", "USD", "EUR", "GBP", "INR", "Other"])
            reference = second.text_input("Reference (optional)", placeholder="PO-10042")
            notes = st.text_area("Notes (optional)", max_chars=500)
            submitted = st.form_submit_button("Save employee record", type="primary", use_container_width=True)
        if submitted:
            if not invoice_number.strip() or not customer_name.strip():
                st.error("Invoice Number and Customer Name are required.")
            else:
                st.session_state.entries.append({"invoice_number": invoice_number.strip(), "invoice_date": invoice_date.isoformat(), "customer_name": customer_name.strip(), "invoice_amount": round(invoice_amount, 2), "currency": currency, "reference": reference.strip(), "notes": notes.strip(), "source": "Manual"})
                activity("Employee record added", invoice_number.strip()); st.success("Employee record saved to this session.")
    with csv_tab:
        st.caption("Required columns: invoice_number, invoice_date, customer_name, invoice_amount, currency")
        csv_file = st.file_uploader("Upload employee CSV", type=["csv"], key="employee_csv")
        if csv_file:
            try:
                frame = read_employee_csv(BytesIO(csv_file.getvalue()))
                st.dataframe(frame, use_container_width=True, hide_index=True)
                if st.button("Import valid CSV records", type="primary", use_container_width=True):
                    records = frame.fillna("").to_dict("records")
                    for record in records: record["source"] = "CSV"
                    st.session_state.entries.extend(records); activity("CSV records imported", f"{len(records)} row(s) from {csv_file.name}"); st.success(f"Imported {len(records)} employee record(s).")
            except ValueError as error:
                st.error(str(error))
    if st.session_state.entries:
        st.subheader("Employee records in this session")
        st.dataframe(pd.DataFrame(st.session_state.entries), use_container_width=True, hide_index=True)

def verification_results():
    render_header("Quality Verification", "Compare source documents with employee-entered values")
    st.markdown('<span class="status-pill">Stage 3 · planned</span>', unsafe_allow_html=True)
    st.warning("Verification is intentionally not simulated in Stage 1. OCR extraction (Stage 2) must exist before values can responsibly be labelled.")
    rows = [["Match", "Normalized values agree", "Green"], ["Mismatch", "Values clearly differ", "Red"], ["Needs Manual Review", "OCR is uncertain or ambiguous", "Amber"], ["Missing Value", "One source has no value", "Red"]]
    st.dataframe(pd.DataFrame(rows, columns=["Status", "Meaning", "Visual treatment"]), use_container_width=True, hide_index=True)

def reports():
    render_header("Reports", "Export the real intake data from this session")
    records, documents = len(st.session_state.entries), len(st.session_state.documents)
    c1, c2 = st.columns(2); c1.metric("Documents available", documents); c2.metric("Employee records available", records)
    if not records and not documents:
        st.info("Add a document or employee record to generate a Stage 1 intake report."); return
    left, right = st.columns(2)
    left.download_button("Download employee data (CSV)", build_entries_csv(st.session_state.entries), "employee_intake_report.csv", "text/csv", use_container_width=True, disabled=not records)
    right.download_button("Download intake summary (PDF)", build_summary_pdf(st.session_state.documents, st.session_state.entries), "stage1_intake_summary.pdf", "application/pdf", use_container_width=True)
    st.caption("Verification history and error summaries become available when verification and SQLite are added.")

with st.sidebar:
    st.markdown('<div class="brand"><div>✓</div><strong>AI Smart<br>Quality Checker</strong></div>', unsafe_allow_html=True)
    st.caption("Innodata AI Hackathon 2026")
    page = st.radio("Navigation", ["Dashboard", "Document Upload", "Employee Data", "Quality Verification", "Reports"], label_visibility="collapsed")
    st.markdown("---"); st.caption("SYSTEM STATUS"); st.success("● Stage 1 ready"); st.caption("Offline-first · No external AI calls")

{"Dashboard": dashboard, "Document Upload": document_upload, "Employee Data": employee_data, "Quality Verification": verification_results, "Reports": reports}[page]()
