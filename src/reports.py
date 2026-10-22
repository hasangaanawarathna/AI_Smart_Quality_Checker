from datetime import datetime
from io import BytesIO
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

def build_entries_csv(entries):
    return pd.DataFrame(entries).to_csv(index=False).encode("utf-8")

def _table(rows, widths):
    table = Table(rows, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#102A56")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#CBD5E1")),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F1F5F9")]),("VALIGN",(0,0),(-1,-1),"TOP"),("PADDING",(0,0),(-1,-1),5)]))
    return table

def build_summary_pdf(documents, entries):
    buffer = BytesIO(); pdf = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm); styles = getSampleStyleSheet()
    story = [Paragraph("AI Smart Quality Checker", styles["Title"]), Paragraph("Stage 1 Intake Summary", styles["Heading2"]), Paragraph(f"Generated: {datetime.now():%Y-%m-%d %H:%M}", styles["Normal"]), Spacer(1,10), Paragraph(f"Documents uploaded: {len(documents)}", styles["Normal"]), Paragraph(f"Employee records entered: {len(entries)}", styles["Normal"]), Spacer(1,12)]
    if documents:
        story += [Paragraph("Documents", styles["Heading3"]), _table([["File","Size (KB)","Uploaded"]]+[[x.get("name",""),x.get("size_kb",""),x.get("uploaded_at","")] for x in documents],[85*mm,30*mm,50*mm]), Spacer(1,12)]
    if entries:
        rows=[["Invoice","Date","Customer","Amount","Currency"]]+[[str(x.get("invoice_number","")),str(x.get("invoice_date","")),str(x.get("customer_name",""))[:28],str(x.get("invoice_amount","")),str(x.get("currency",""))] for x in entries]
        story += [Paragraph("Employee Records", styles["Heading3"]), _table(rows,[30*mm,28*mm,62*mm,27*mm,20*mm])]
    story += [Spacer(1,16), Paragraph("Note: This Stage 1 report contains intake data only. OCR and verification results are not yet generated.", styles["Italic"])]
    pdf.build(story); return buffer.getvalue()
