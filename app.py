"""AI Smart Quality Checker — persistent, explainable verification workflow."""
from datetime import date, datetime
from io import BytesIO
import pandas as pd
import streamlit as st
from src.reports import build_entries_csv, build_summary_pdf
from src.storage import decide, initialize, list_records, list_verifications, save_verification, upsert_record
from src.ui import inject_styles, render_empty, render_header
from src.validators import MAX_FILE_SIZE_MB, read_employee_csv, validate_document
from src.verification import verify_records

st.set_page_config(page_title="AI Smart Quality Checker", page_icon="✅", layout="wide")
inject_styles(); initialize()
for key in ("documents", "activities"): st.session_state.setdefault(key, [])

def activity(action, detail):
    st.session_state.activities.insert(0, {"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "action": action, "detail": detail})

def dashboard():
    render_header("Quality dashboard", "Persistent, explainable invoice-quality operations")
    entries, sources, runs = list_records("employee"), list_records("source"), list_verifications()
    passed = sum(x["status"] == "passed" for x in runs); pending = sum(x["decision"] == "pending" for x in runs)
    average = round(sum(x["quality_score"] for x in runs) / len(runs), 1) if runs else 0
    st.markdown('<div class="hero"><div class="eyebrow">QUALITY CONTROL CENTER</div><h2>Trust every invoice before it moves downstream.</h2><p>Capture source evidence, validate employee data, run explainable checks, and record a human decision in one audit-ready workflow.</p></div>', unsafe_allow_html=True)
    cards = [("Employee records",len(entries),"Saved in SQLite"),("Source records",len(sources),"OCR-ready contract"),("Pass rate",f"{passed/len(runs)*100:.0f}%" if runs else "—",f"{len(runs)} verification run(s)"),("Pending review",pending,f"Average quality: {average}%")]
    for col,(label,value,note) in zip(st.columns(4),cards): col.markdown(f'<div class="metric-card"><span>{label}</span><strong>{value}</strong><small>{note}</small></div>',unsafe_allow_html=True)
    left,right=st.columns([1.4,1])
    with left:
        st.markdown('<div class="section-label">Latest verification runs</div>',unsafe_allow_html=True)
        if runs: st.dataframe(pd.DataFrame([{"invoice":r["invoice_number"],"status":r["status"],"quality":r["quality_score"],"decision":r["decision"],"created":r["created_at"]} for r in runs[:10]]),hide_index=True,use_container_width=True)
        else: render_empty("No verification runs","Add employee and source records, then run a comparison.")
    with right:
        st.markdown('<div class="section-label">Workflow</div>',unsafe_allow_html=True)
        for number,title,status in [("1","Document intake","Validate"),("2","Source capture","Extract"),("3","Rule engine","Compare"),("4","Human review","Decide")]: st.markdown(f'<div class="pipeline"><b>{number}</b><div><strong>{title}</strong><span>{status}</span></div></div>',unsafe_allow_html=True)

def documents():
    render_header("Document intake","Validate files and register source documents")
    st.markdown(f'<div class="notice">PDF, JPG, JPEG or PNG • Maximum {MAX_FILE_SIZE_MB} MB • Metadata remains in this session</div>',unsafe_allow_html=True)
    upload=st.file_uploader("Drop an invoice here",type=["pdf","jpg","jpeg","png"])
    if upload:
        valid,message=validate_document(upload.name,upload.size,upload.type); (st.success if valid else st.error)(message)
        if valid and st.button("Register document",type="primary",use_container_width=True):
            if upload.name in {x["name"] for x in st.session_state.documents}: st.warning("This filename is already registered in the current session.")
            else:
                st.session_state.documents.append({"name":upload.name,"size_kb":round(upload.size/1024,1),"type":upload.type,"uploaded_at":datetime.now().strftime("%Y-%m-%d %H:%M")}); activity("Document registered",upload.name); st.success("Document registered.")
    if st.session_state.documents: st.dataframe(pd.DataFrame(st.session_state.documents),hide_index=True,use_container_width=True)

def record_form(kind,key):
    label="Source / extracted" if kind=="source" else "Employee"
    with st.form(key,clear_on_submit=True):
        a,b=st.columns(2); number=a.text_input("Invoice number *"); invoice_date=b.date_input("Invoice date *",value=date.today()); customer=a.text_input("Customer name *"); amount=b.number_input("Invoice amount *",min_value=0.0,step=0.01); currency=a.selectbox("Currency *",["LKR","USD","EUR","GBP","INR","Other"]); reference=b.text_input("Reference"); submitted=st.form_submit_button(f"Save {label.lower()} record",type="primary",use_container_width=True)
    if submitted:
        if not number.strip() or not customer.strip(): st.error("Invoice number and customer name are required.")
        else:
            payload={"invoice_number":number.strip(),"invoice_date":invoice_date.isoformat(),"customer_name":customer.strip(),"invoice_amount":round(amount,2),"currency":currency,"reference":reference.strip(),"source":label}; upsert_record(kind,payload); activity(f"{label} record saved",number.strip()); st.success(f"{label} record saved. Reusing an invoice number updates it.")

def data_capture():
    render_header("Data capture","Create employee values and independent source-of-truth values")
    employee_tab,source_tab,csv_tab=st.tabs(["Employee entry","Source capture","CSV import"])
    with employee_tab: record_form("employee","employee_form")
    with source_tab:
        st.info("Enter values read from the document. This keeps results honest until an OCR adapter is connected."); record_form("source","source_form")
    with csv_tab:
        uploaded=st.file_uploader("Employee CSV",type=["csv"])
        if uploaded:
            try:
                frame=read_employee_csv(BytesIO(uploaded.getvalue())); st.dataframe(frame,hide_index=True,use_container_width=True)
                if st.button("Import / update records",type="primary",use_container_width=True):
                    for row in frame.fillna("").to_dict("records"): row["source"]="CSV"; upsert_record("employee",row)
                    activity("Employee CSV imported",f"{len(frame)} row(s)"); st.success(f"Imported {len(frame)} record(s).")
            except ValueError as error: st.error(str(error))
    for title,kind in [("Employee records","employee"),("Source records","source")]:
        rows=list_records(kind); st.markdown(f'<div class="section-label">{title}</div>',unsafe_allow_html=True)
        if rows:
            query=st.text_input(f"Search {kind} records",placeholder="Invoice, customer, reference...",key=f"search_{kind}")
            frame=pd.DataFrame(rows)
            if query:
                mask=frame.astype(str).apply(lambda column: column.str.contains(query,case=False,na=False)).any(axis=1)
                frame=frame[mask]
            st.caption(f"Showing {len(frame)} of {len(rows)} record(s)")
            st.dataframe(frame,hide_index=True,use_container_width=True)
        else: render_empty(f"No {kind} records","Add a record above to begin.")

def verification():
    render_header("Quality verification","Run deterministic checks and route exceptions for review")
    employees={x["invoice_number"]:x for x in list_records("employee")}; sources={x["invoice_number"]:x for x in list_records("source")}; eligible=sorted(employees.keys()&sources.keys())
    if not eligible: st.warning("An invoice number must exist in both Employee and Source records.")
    else:
        selected_batch=st.multiselect("Batch selection",eligible,placeholder="Choose several invoices to verify together")
        if st.button("Run selected batch",disabled=not selected_batch,use_container_width=True):
            for selected_invoice in selected_batch:
                batch_result=verify_records(sources[selected_invoice],employees[selected_invoice]); save_verification(selected_invoice,batch_result)
            activity("Batch verification completed",f"{len(selected_batch)} invoice(s)"); st.success(f"Verified {len(selected_batch)} invoice(s)."); st.rerun()
        invoice=st.selectbox("Invoice",eligible)
        if st.button("Run verification",type="primary",use_container_width=True):
            result=verify_records(sources[invoice],employees[invoice]); save_verification(invoice,result); activity("Verification completed",f"{invoice}: {result['status']}"); st.session_state.last_result={"invoice":invoice,**result}
        result=st.session_state.get("last_result")
        if result:
            c1,c2,c3=st.columns(3); c1.metric("Status",result["status"].upper()); c2.metric("Quality score",f"{result['quality_score']}%"); c3.metric("Risk score",f"{result['risk_score']}%"); st.dataframe(pd.DataFrame(result["fields"]),hide_index=True,use_container_width=True)
    runs=list_verifications(); st.markdown('<div class="section-label">Review queue</div>',unsafe_allow_html=True)
    if runs:
        status_filter=st.multiselect("Filter queue",["passed","review","failed"],default=["passed","review","failed"])
        filtered_runs=[r for r in runs if r["status"] in status_filter]
        if not filtered_runs: st.info("No verification runs match the selected filters."); return
        run_map={f"#{r['id']} · {r['invoice_number']} · {r['status']} · {r['quality_score']}%":r for r in filtered_runs}; selected=run_map[st.selectbox("Verification run",list(run_map))]
        st.progress(float(selected["quality_score"])/100,text=f"Quality score: {selected['quality_score']}%")
        field_frame=pd.DataFrame(selected["result"].get("fields",[]))
        if not field_frame.empty: st.dataframe(field_frame,hide_index=True,use_container_width=True)
        with st.form("decision_form"):
            choices=["pending","approved","rejected"]; decision_value=st.selectbox("Decision",choices,index=choices.index(selected["decision"])); note=st.text_area("Reviewer note",value=selected["reviewer_note"]); submit=st.form_submit_button("Save review decision",use_container_width=True)
        if submit: decide(selected["id"],decision_value,note); activity("Review decision saved",f"{selected['invoice_number']}: {decision_value}"); st.success("Review decision saved."); st.rerun()
    else: render_empty("Review queue is empty","Completed verification runs appear here.")

def reports():
    render_header("Reports & audit","Export current data and inspect verification history")
    entries,runs=list_records("employee"),list_verifications(); a,b,c=st.columns(3); a.metric("Records",len(entries)); b.metric("Runs",len(runs)); c.metric("Reviewed",sum(x["decision"]!="pending" for x in runs))
    left,right=st.columns(2); left.download_button("Download employee data (CSV)",build_entries_csv(entries),"employee_records.csv","text/csv",disabled=not entries,use_container_width=True); right.download_button("Download intake summary (PDF)",build_summary_pdf(st.session_state.documents,entries),"quality_intake_summary.pdf","application/pdf",use_container_width=True)
    if runs:
        audit=pd.DataFrame([{"id":x["id"],"invoice":x["invoice_number"],"status":x["status"],"quality_score":x["quality_score"],"decision":x["decision"],"reviewer_note":x["reviewer_note"],"created_at":x["created_at"]} for x in runs]); st.download_button("Download verification audit (CSV)",audit.to_csv(index=False).encode("utf-8"),"verification_audit.csv","text/csv",use_container_width=True); st.dataframe(audit,hide_index=True,use_container_width=True)

def analytics():
    render_header("Quality analytics","Spot trends, recurring exceptions, and review bottlenecks")
    runs=list_verifications()
    if not runs: render_empty("No analytics yet","Complete a verification run to unlock trends."); return
    frame=pd.DataFrame([{"invoice":r["invoice_number"],"status":r["status"],"quality":r["quality_score"],"decision":r["decision"],"created":pd.to_datetime(r["created_at"])} for r in runs]).sort_values("created")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Average quality",f"{frame['quality'].mean():.1f}%")
    c2.metric("High-risk runs",int((frame["quality"]<80).sum()))
    c3.metric("Approval rate",f"{(frame['decision'].eq('approved').mean()*100):.0f}%")
    c4.metric("Pending reviews",int(frame["decision"].eq("pending").sum()))
    left,right=st.columns([1.4,1])
    with left:
        st.markdown('<div class="section-label">Quality trend</div>',unsafe_allow_html=True)
        st.line_chart(frame.set_index("created")[["quality"]],height=300)
    with right:
        st.markdown('<div class="section-label">Outcome mix</div>',unsafe_allow_html=True)
        st.bar_chart(frame["status"].value_counts(),height=300)
    issues=[]
    for run in runs:
        for field in run["result"].get("fields",[]):
            if field.get("status")!="match": issues.append(field.get("field","unknown"))
    st.markdown('<div class="section-label">Most common exception fields</div>',unsafe_allow_html=True)
    if issues: st.bar_chart(pd.Series(issues).value_counts())
    else: st.success("All checked fields match across the current verification history.")

def activity_center():
    render_header("Activity center","Follow work completed during this session")
    activities=st.session_state.activities
    if not activities: render_empty("No session activity","Imports, verifications, and review decisions will appear here."); return
    frame=pd.DataFrame(activities)
    a,b=st.columns([1,3]); available=sorted(frame["action"].unique()); action_filter=a.multiselect("Action",available,default=available); search=b.text_input("Search activity",placeholder="Search action details...")
    filtered=frame[frame["action"].isin(action_filter)]
    if search: filtered=filtered[filtered.astype(str).apply(lambda col: col.str.contains(search,case=False,na=False)).any(axis=1)]
    st.dataframe(filtered,hide_index=True,use_container_width=True)
    st.download_button("Download session activity",filtered.to_csv(index=False).encode("utf-8"),"session_activity.csv","text/csv",use_container_width=True)

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">Q</div><strong>AI Smart<br>Quality Checker</strong></div>',unsafe_allow_html=True); st.caption("Explainable quality operations"); page=st.radio("Navigation",["Dashboard","Document intake","Data capture","Quality verification","Analytics","Reports & audit","Activity center"],label_visibility="collapsed"); st.markdown("---"); st.success("● Persistent engine online"); st.caption("SQLite • Rule-based • Audit-ready")
{"Dashboard":dashboard,"Document intake":documents,"Data capture":data_capture,"Quality verification":verification,"Analytics":analytics,"Reports & audit":reports,"Activity center":activity_center}[page]()
